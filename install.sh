#!/bin/bash

# Install theme families on an Omarchy machine.
#
#   ./install.sh                        # every family's themes + branding store
#   ./install.sh commit                 # just this family
#   ./install.sh commit --theme evening # ...and switch to it
#   ./install.sh --no-branding          # themes only; leave About/fastfetch alone
#   ./install.sh --no-backdrop          # skip the animated-backdrop shell plugin
#
# Themes from every family coexist in the theme list. Branding does not:
# Omarchy has one About logo, one screensaver panel and one user fastfetch
# config. So each family's branding is staged under
# ~/.config/omarchy/branding/families/<name>/ and a theme-set hook swaps the
# live slot whenever you pick a theme from that family. Stock themes leave
# whatever is installed in place.
#
# Existing files are backed up with a timestamp before being replaced.

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEMES_DIR="$HOME/.config/omarchy/themes"
BRANDING_DIR="$HOME/.config/omarchy/branding"
FAMILY_DIR="$BRANDING_DIR/families"

families=()
apply_theme=""
want_branding=1
want_fog=1

while (($# > 0)); do
  case "$1" in
  --theme)
    shift
    apply_theme="${1:-}"
    [[ -n $apply_theme ]] || {
      echo "--theme needs a name" >&2
      exit 1
    }
    ;;
  --no-branding) want_branding=0 ;;
  --no-backdrop) want_fog=0 ;;
  -h | --help)
    sed -n '3,19p' "$BASH_SOURCE" | sed 's/^# \?//'
    exit 0
    ;;
  -*)
    echo "Unknown option: $1" >&2
    exit 1
    ;;
  *)
    [[ -d $SRC/$1/themes ]] || {
      echo "No such family: $1" >&2
      exit 1
    }
    families+=("$1")
    ;;
  esac
  shift
done

if ((${#families[@]} == 0)); then
  for d in "$SRC"/*/themes; do
    families+=("$(basename "$(dirname "$d")")")
  done
fi

backup() {
  [[ -e $1 ]] || return 0
  cp -a "$1" "$1.bak.$(date +%s)"
}

mkdir -p "$THEMES_DIR" "$BRANDING_DIR"

for family in "${families[@]}"; do
  echo "family: $family"

  for theme in "$SRC/$family"/themes/*/; do
    name=$(basename "$theme")
    rm -rf "${THEMES_DIR:?}/$name"
    cp -r "$theme" "$THEMES_DIR/$name"
    echo "  theme: $name"
  done

  ((want_branding)) || continue

  dest="$FAMILY_DIR/$family"
  mkdir -p "$dest"
  for f in about.txt screensaver.txt; do
    [[ -f $SRC/$family/branding/$f ]] && install -m 644 "$SRC/$family/branding/$f" "$dest/$f"
  done
  [[ -f $SRC/$family/fastfetch/config.jsonc ]] &&
    install -m 644 "$SRC/$family/fastfetch/config.jsonc" "$dest/fastfetch.jsonc"
  echo "  branding staged: $dest"
done

# The hook is what makes the staged families reachable.
#
# Do NOT back the hook up in place: omarchy-hook runs *every* file in
# theme-set.d/, so a timestamped copy alongside it keeps executing after the
# real one and silently re-applies whatever routing it had. Sweep any that a
# previous version of this script left behind. The hook is versioned here, so
# there is nothing worth keeping a local copy of anyway.
if ((want_branding)); then
  hook_dir="$HOME/.config/omarchy/hooks/theme-set.d"
  if compgen -G "$hook_dir/10-branding-family.bak.*" >/dev/null; then
    rm -f "$hook_dir"/10-branding-family.bak.*
    echo "  removed stale hook copies that were shadowing the current one"
  fi
  omarchy hook install theme-set "$SRC/hooks/10-branding-family" >/dev/null
  echo "hook: theme-set/10-branding-family"
fi

# The backdrop plugin only ever draws for a theme that ships a backdrop/
# directory, so installing it is inert for the rest. Disable it any time with:
#   omarchy plugin disable gand.backdrop
if ((want_fog)) && [[ -d $SRC/shell/gand.backdrop ]]; then
  # gand.fog was this plugin's name while it only did fog. Retire it, or both
  # would run and draw two stacked layer surfaces.
  if [[ -d $HOME/.config/omarchy/plugins/gand.fog ]]; then
    omarchy plugin remove gand.fog --yes >/dev/null 2>&1 || true
    rm -rf "$HOME/.config/omarchy/plugins/gand.fog"
    echo "  retired gand.fog (superseded by gand.backdrop)"
  fi
  dest="$HOME/.config/omarchy/plugins/gand.backdrop"
  changed=1
  [[ -d $dest ]] && diff -rq "$SRC/shell/gand.backdrop" "$dest" >/dev/null 2>&1 && changed=0
  mkdir -p "$dest"
  cp -a "$SRC/shell/gand.backdrop/." "$dest/"
  omarchy-shell shell rescanPlugins >/dev/null 2>&1 || true
  omarchy plugin enable gand.backdrop >/dev/null 2>&1 || true
  echo "plugin: gand.backdrop (animated backdrop)"
  # rescanPlugins finds a *new* plugin but keeps running the QML it already
  # loaded, so an edit to Backdrop.qml is invisible until the shell restarts.
  if ((changed)); then
    omarchy restart shell >/dev/null 2>&1 || true
    echo "  shell restarted to pick up the plugin"
  fi
fi

if [[ -n $apply_theme ]]; then
  # Bare names resolve against the single family being installed.
  if [[ $apply_theme != *-* ]] && ((${#families[@]} == 1)); then
    apply_theme="${families[0]}-$apply_theme"
  fi
  backup "$BRANDING_DIR/about.txt"
  backup "$BRANDING_DIR/screensaver.txt"
  backup "$HOME/.config/fastfetch/config.jsonc"
  omarchy theme set "$apply_theme"
  echo "applied: $apply_theme"
else
  echo
  echo "Installed. Pick one with:  omarchy theme set \"Commit Late Night\""
  echo "Branding follows the theme you pick; run tools/fit-about.sh once per machine."
fi
