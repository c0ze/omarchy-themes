#!/bin/bash

# Retake previews/<display name>.webp: a real desktop under each theme.
#
#   tools/shoot-previews.sh                 # every theme that has a repo
#   tools/shoot-previews.sh commit-morning  # just this one
#
# Three windows on an empty workspace, tiled by Hyprland's dwindle: the family's
# fastfetch About panel down the left, the ANSI palette and the theme's name top
# right, and a source file under `bat` bottom right.
#
# The code window matters. Omarchy pins BAT_THEME=ansi, so bat paints syntax
# with the terminal's sixteen colours and the theme decides every one of them --
# a preview that renders code in some other theme's palette is showing the
# reader a screenshot of a different theme. Earlier shots did exactly that, and
# they are the reason all of this looked colourless.
#
# Restores the theme and workspace that were in use when it started.

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$SRC/previews"
CLASS="theme-shot"
SETTLE=2.5   # theme-set, the branding hook and the backdrop reload
# Zero, and pinned so a shot is the same on any machine. Tempting as it is to
# frame the windows in wallpaper, the omarchy shell's desktop widgets sit on the
# background layer: any gap that shows the wallpaper shows the host's weather,
# process list and resource meters along with it. The windows keep their
# accent-coloured borders, which is separation enough.
GAPS_OUT=0
GAPS_IN=0
PAINT=3.4    # windows mapped and resized, code window painted

# slug|display name|source file shown in the code window|first line to show
SHOTS=(
  "commit-late-night|Commit|commit/tools/gen_rain.py|56"
  "commit-evening|Commit Evening|commit/tools/gen_rain.py|56"
  "commit-morning|Commit Morning|commit/tools/gen_rain.py|56"
  "gand-earth|Gand|gand/tools/gen_orrery.py|54"
  "gand-dark|Gand Dark|gand/tools/gen_orrery.py|54"
  "gand-light|Gand Light|gand/tools/gen_orrery.py|54"
  "pagan-dark|Pagan|tools/gen_backdrop_anim.py|66"
  "pagan-light|Pagan Light|tools/gen_backdrop_anim.py|66"
)

want=("$@")

# By pid, not by close dispatch: kitty holds an interactive shell here and
# answers a Wayland close request with a confirmation prompt, so the windows
# pile up on the shot workspace instead of going away.
kill_shots() {
  hyprctl clients -j |
    python3 -c "
import json, sys
for c in json.load(sys.stdin):
    if c['class'] == '$CLASS':
        print(c['pid'])" |
    while read -r pid; do kill "$pid" 2>/dev/null || true; done
}

# Opaque on purpose. Omarchy's terminals are translucent, and at half a 4K
# screen the desktop widgets read straight through them -- a preview should
# show the theme, not what this machine happens to be running.
term() { # term <title> <font size> <command>
  setsid kitty --class "$CLASS" --title "$1" \
    -o background_opacity=1.0 -o background_blur=0 -o font_size="$2" \
    bash --norc -c "$3; PS1='[\\u@\\h \\W]\\\$ ' exec bash --norc" \
    >/dev/null 2>&1 &
}

# Hyprland's own opacity rule wins over kitty's background_opacity, so the
# windows have to be told again once they exist.
shot_addrs() {
  hyprctl clients -j | python3 -c "
import json, sys
for c in json.load(sys.stdin):
    if c['class'] == '$CLASS':
        print(c['address'], c['title'])"
}

make_opaque() {
  shot_addrs | while read -r addr _; do
    hyprctl dispatch \
      "hl.dsp.window.set_prop({ window = \"address:$addr\", prop = \"opaque\", value = \"1\" })" \
      >/dev/null
  done
}

# The palette window only ever holds four lines. Shrinking it hands the rest of
# the column to the code, which is the half of the shot worth looking at.
shrink_palette() {
  local addr
  addr=$(shot_addrs | awk '$2 == "palette" { print $1; exit }')
  [[ -n $addr ]] || return 0
  local w
  w=$(hyprctl clients -j | python3 -c "
import json, sys
for c in json.load(sys.stdin):
    if c['address'] == '$addr':
        print(int(c['size'][0]))")
  hyprctl dispatch \
    "hl.dsp.window.resize({ window = \"address:$addr\", x = $w, y = 185 })" >/dev/null
}

gap() { # gap <option> -> first value of "css gap data: a b c d"
  hyprctl getoption "general:$1" | awk '/css gap data/ { print $4; exit }'
}

start_theme=$(cat "$HOME/.local/state/omarchy/current/theme.name" 2>/dev/null || true)
start_out=$(gap gaps_out)
start_in=$(gap gaps_in)
start_ws=$(hyprctl activeworkspace -j | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
shot_ws=$(hyprctl workspaces -j | python3 -c "
import json, sys
used = {w['id'] for w in json.load(sys.stdin) if w['windows']}
print(next(i for i in range(1, 100) if i not in used))")

cleanup() {
  kill_shots
  hyprctl eval "hl.config({ general = { gaps_out = ${start_out:-10}, gaps_in = ${start_in:-10} } })" >/dev/null 2>&1
  [[ -n $start_theme ]] && omarchy theme set "$start_theme" >/dev/null 2>&1
  hyprctl dispatch "hl.dsp.focus({ workspace = \"$start_ws\" })" >/dev/null 2>&1
  return 0
}
trap cleanup EXIT

hyprctl dispatch "hl.dsp.focus({ workspace = \"$shot_ws\" })" >/dev/null
sleep 0.6

for shot in "${SHOTS[@]}"; do
  IFS='|' read -r slug display source first <<<"$shot"
  if ((${#want[@]})) && ! printf '%s\n' "${want[@]}" | grep -qx "$slug"; then
    continue
  fi

  omarchy theme set "$slug" >/dev/null
  sleep "$SETTLE"
  # After the theme, never before: theme-set reloads the Hyprland config and
  # takes the gaps back to whatever looknfeel.lua says.
  hyprctl eval "hl.config({ general = { gaps_out = $GAPS_OUT, gaps_in = $GAPS_IN } })" >/dev/null
  sleep 0.4

  # Left: the family's About panel, exactly as the theme-set hook staged it.
  # --logo-position top: the family's fastfetch config is fitted to the About
  # window, which is wider than half a screen, and side-by-side clips. --pipe
  # false keeps the colour and the box art through the pipe; head keeps the
  # terminal from scrolling, which would cut the top off the logo.
  term about 12 "fastfetch --pipe false --logo-position top \
      | head -n \$((\$(tput lines) - 2))"
  sleep 0.9
  # Top right: the sixteen ANSI slots, then the theme's name.
  term palette 17 "printf '\n'
    for c in 0 1 2 3 4 5 6 7; do printf \"\\033[4\${c}m      \\033[0m\"; done; printf '\n'
    for c in 0 1 2 3 4 5 6 7; do printf \"\\033[10\${c}m      \\033[0m\"; done; printf '\n\n'
    printf '  \\033[1m%s\\033[0m\n\n' '$display'"
  sleep 0.9
  # Bottom right: code, in this theme's own colours.
  # Sized from inside the window: bat wraps to the real width, and head counts
  # the display rows it emitted, so the code fills the pane and never scrolls.
  # The sleep is load-bearing -- tput has to run after shrink_palette has given
  # this window the rest of the column, or it measures the pre-resize height.
  term code 17 "sleep 2.6
    bat --theme=ansi --style=numbers --paging=never --color=always \
      --terminal-width=\$(tput cols) --line-range=$first: '$SRC/$source' \
      | head -n \$((\$(tput lines) - 2))"
  sleep 1.0
  make_opaque
  shrink_palette
  sleep "$PAINT"

  raw=$(mktemp --suffix=.png)
  grim "$raw"
  python3 - "$raw" "$OUT/${display,,}.webp" <<'PY'
import sys
from PIL import Image
src, dest = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
im.resize((1200, 675), Image.LANCZOS).save(dest, quality=88, method=6)
print(f"  {dest}")
PY
  rm -f "$raw"
  echo "$display"

  kill_shots
  sleep 0.6
done
