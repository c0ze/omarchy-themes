#!/bin/bash

# Size the Omarchy About window for this display.
#
# omarchy-launch-about measures its own content and remembers a window size --
# but only while there is no user-level ~/.config/fastfetch/config.jsonc. Once
# the Gand config is installed that pass is skipped and About falls back to the
# 920x480 default float size, which clips the layout.
#
# So do the measurement here: work out the grid the content needs (the same
# formula omarchy uses), probe the terminal at two sizes to solve for its cell
# size and padding, then write an o.window rule into ~/.config/hypr/hyprland.lua.
#
# Padding is a fixed offset, not a proportion -- deriving the cell height as
# height/rows undercounts it and clips the top of the panel. Hence two probes.
#
# Needs a live Hyprland session. Re-run after changing the fastfetch layout,
# the terminal, its font, or the logo dimensions.

set -uo pipefail

LOGO="$HOME/.config/omarchy/branding/about.txt"
HYPR="$HOME/.config/hypr/hyprland.lua"
PROBE_CLASS="org.gand.probe"
PROBE_OUT="${XDG_RUNTIME_DIR:-/tmp}/gand-probe-grid"
MARKER="-- gand: About window size"

command -v hyprctl >/dev/null || { echo "hyprctl not found -- run this inside Hyprland" >&2; exit 1; }
[[ -f $LOGO ]] || { echo "no $LOGO" >&2; exit 1; }

close_class() {
  hyprctl clients -j | jq -r --arg c "$1" '.[] | select(.class==$c) | .address' |
    while read -r address; do hyprctl dispatch closewindow "address:$address" >/dev/null; done
}

probe_rule() {
  hyprctl eval "if gand_probe then gand_probe:set_enabled(false) end; gand_probe = ${1:-nil}" >/dev/null 2>&1
}

# Open a terminal at an exact pixel size and report the character grid it got.
probe() {
  local w=$1 h=$2
  : >"$PROBE_OUT"
  probe_rule "hl.window_rule({ match = { class = \"$PROBE_CLASS\" }, float = true, size = { $w, $h } })"
  setsid xdg-terminal-exec --app-id="$PROBE_CLASS" -e \
    sh -c "sleep 1; stty size > $PROBE_OUT; sleep 1" </dev/null >/dev/null 2>&1 &
  local waited=0
  while ((waited < 12)); do
    [[ -s $PROBE_OUT ]] && break
    sleep 1
    ((waited++))
  done
  close_class "$PROBE_CLASS"
  cat "$PROBE_OUT"
}

# --- what grid does the content need? ---------------------------------------
# Mirrors omarchy-launch-about: 2 columns of padding, the logo, 6 columns of
# gutter, the modules, 2 more columns; rows are the taller of logo+2 or the
# module block, plus a row for the cursor.
logo_w=$(LC_ALL=C.UTF-8 wc -L <"$LOGO")
logo_h=$(wc -l <"$LOGO")
modules=$(fastfetch --logo none | sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g')
module_w=$(printf '%s' "$modules" | LC_ALL=C.UTF-8 wc -L)
module_h=$(printf '%s\n' "$modules" | wc -l)

target_c=$((2 + logo_w + 6 + module_w + 2))
target_r=$(((logo_h + 2 > module_h ? logo_h + 2 : module_h) + 1))
echo "content: ${target_c}x${target_r} cells (logo ${logo_w}x${logo_h}, modules ${module_w}x${module_h})"

# --- solve the terminal's cell size and padding ------------------------------
read -r r1 c1 <<<"$(probe 1200 700)"
read -r r2 c2 <<<"$(probe 1700 1000)"
[[ -n ${r1:-} && -n ${r2:-} && $r1 != "$r2" && $c1 != "$c2" ]] || {
  probe_rule
  echo "probe failed (got '$r1 $c1' / '$r2 $c2') -- is a terminal launchable?" >&2
  exit 1
}
probe_rule
echo "probe: 1200x700 -> ${c1}x${r1} cells, 1700x1000 -> ${c2}x${r2} cells"

# width = pad_w + cols * cell_w, solved from the two samples
cell_w=$(( (1700 - 1200) * 100 / (c2 - c1) ))          # x100, integer math
pad_w=$((1700 * 100 - c2 * cell_w))
cell_h=$(( (1000 - 700) * 100 / (r2 - r1) ))
pad_h=$((1000 * 100 - r2 * cell_h))

# One extra cell of slack in each axis, the same tolerance omarchy allows.
win_w=$(((pad_w + (target_c + 1) * cell_w + 99) / 100))
win_h=$(((pad_h + (target_r + 1) * cell_h + 99) / 100))
echo "cell ${cell_w}/100 x ${cell_h}/100 px, padding ${pad_w}/100 x ${pad_h}/100 -> window ${win_w}x${win_h}"

read -r screen_w screen_h <<<"$(hyprctl monitors -j | jq -r '.[0] | "\(.width) \(.height)"')"
if ((win_w > screen_w || win_h > screen_h)); then
  echo "warning: ${win_w}x${win_h} exceeds the ${screen_w}x${screen_h} screen; clamping" >&2
  ((win_w > screen_w)) && win_w=$screen_w
  ((win_h > screen_h)) && win_h=$screen_h
fi

# --- write the rule ----------------------------------------------------------
cp -a "$HYPR" "$HYPR.bak.$(date +%s)"
grep -v "^o.window(\"org.omarchy.about\"" "$HYPR" | grep -v -- "^$MARKER" >"$HYPR.tmp"
{
  echo ""
  echo "$MARKER (measured by omarchy-themes/tools/fit-about.sh)"
  echo "o.window(\"org.omarchy.about\", { size = { $win_w, $win_h } })"
} >>"$HYPR.tmp"
mv "$HYPR.tmp" "$HYPR"

hyprctl reload >/dev/null
errors=$(hyprctl configerrors)
[[ -z $errors || $errors == "no errors"* ]] || { echo "$errors" >&2; exit 1; }
echo "wrote rule to $HYPR and reloaded"
