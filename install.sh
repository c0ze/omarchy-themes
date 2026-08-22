#!/bin/bash

# Install the Gand look on an Omarchy machine: three themes, the About/fastfetch
# branding and the screensaver panel.
#
#   ./install.sh                 # install everything, apply nothing
#   ./install.sh --theme earth   # ...and switch to Gand Earth
#   ./install.sh --no-fastfetch  # skip the fastfetch config (keeps omarchy's)
#
# Existing files are backed up with a timestamp before being replaced.

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEMES_DIR="$HOME/.config/omarchy/themes"
BRANDING_DIR="$HOME/.config/omarchy/branding"
FASTFETCH_DIR="$HOME/.config/fastfetch"

apply_theme=""
want_fastfetch=1

while (($# > 0)); do
  case "$1" in
  --theme)
    shift
    apply_theme="${1:-}"
    [[ -n $apply_theme ]] || { echo "--theme needs a name (dark|earth|light)" >&2; exit 1; }
    ;;
  --no-fastfetch) want_fastfetch=0 ;;
  -h | --help)
    sed -n '3,11p' "$BASH_SOURCE" | sed 's/^# \?//'
    exit 0
    ;;
  *)
    echo "Unknown option: $1" >&2
    exit 1
    ;;
  esac
  shift
done

backup() {
  [[ -e $1 ]] || return 0
  cp -a "$1" "$1.bak.$(date +%s)"
  echo "  backed up $(basename "$1")"
}

# --- themes -----------------------------------------------------------------
mkdir -p "$THEMES_DIR"
for theme in "$SRC"/themes/*/; do
  name=$(basename "$theme")
  rm -rf "${THEMES_DIR:?}/$name"
  cp -r "$theme" "$THEMES_DIR/$name"
  echo "theme: $name"
done

# --- branding ---------------------------------------------------------------
# The screensaver panel carries a hostname line; re-centre it for this machine.
mkdir -p "$BRANDING_DIR"
backup "$BRANDING_DIR/about.txt"
backup "$BRANDING_DIR/screensaver.txt"
cp "$SRC/branding/about.txt" "$BRANDING_DIR/about.txt"

field=$(LC_ALL=C.UTF-8 wc -L <"$SRC/branding/screensaver.txt")
host=$(hostname)
pad=$(((field - ${#host}) / 2))
head -n -1 "$SRC/branding/screensaver.txt" >"$BRANDING_DIR/screensaver.txt"
printf '%*s%s\n' "$pad" "" "$host" >>"$BRANDING_DIR/screensaver.txt"
echo "branding: about.txt, screensaver.txt (host: $host)"

# --- fastfetch --------------------------------------------------------------
# A user-level fastfetch config disables omarchy-launch-about's measure-and-fit
# pass, so the About window needs an explicit size rule -- see tools/fit-about.sh.
if ((want_fastfetch)); then
  mkdir -p "$FASTFETCH_DIR"
  backup "$FASTFETCH_DIR/config.jsonc"
  cp "$SRC/fastfetch/config.jsonc" "$FASTFETCH_DIR/config.jsonc"
  echo "fastfetch: config.jsonc"
  echo "  note: run tools/fit-about.sh to size the About window for this display"
fi

# --- apply ------------------------------------------------------------------
if [[ -n $apply_theme ]]; then
  [[ $apply_theme == gand-* ]] || apply_theme="gand-$apply_theme"
  omarchy theme set "$apply_theme"
  echo "applied: $apply_theme"
else
  echo
  echo "Installed. Apply one with:  omarchy theme set \"Gand Earth\""
fi
