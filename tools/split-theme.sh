#!/bin/bash

# Export one theme as a standalone repository.
#
#   tools/split-theme.sh <theme-slug> <output-dir> "<Display Name>" "<one-line blurb>"
#
# omarchy.org/themes lists one repository per theme, because that is the unit
# omarchy-theme-install understands: it clones a repo into
# ~/.config/omarchy/themes/<basename> and expects colors.toml at the root. This
# monorepo carries ten themes, so a theme going to that directory needs its own
# repo with everything lifted one level up.
#
# The export is a copy, never a rewrite: the theme directories here already have
# exactly the shape the installer wants. Re-run this after changing a theme and
# push the result, rather than editing the standalone repo by hand.

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
slug="${1:?theme slug, e.g. gand-earth}"
out="${2:?output directory}"
name="${3:?display name, e.g. Gand}"
blurb="${4:?one-line description}"

theme=$(find "$SRC" -mindepth 3 -maxdepth 3 -type d -path "*/themes/$slug" | head -1)
[[ -n $theme ]] || { echo "no such theme: $slug" >&2; exit 1; }

mkdir -p "$out"
# Everything except the repo-only extras; colors.toml and friends land at root.
cp -a "$theme/." "$out/"

preview="$SRC/previews/${name,,}.webp"
[[ -f $preview ]] && cp "$preview" "$out/preview.webp"

cat >"$out/README.md" <<EOF
# $name — an Omarchy theme

$blurb

![$name](preview.webp)

## Install

\`\`\`sh
omarchy theme install https://github.com/c0ze/$(basename "$out")
\`\`\`

Or in the menu: **Super + Space → Install → Style → Theme**, then paste the URL.

## What is in here

\`colors.toml\` is the palette. \`backgrounds/\` holds three wallpapers —
Omarchy cycles them, and \`omarchy theme bg next\` steps through. There is also
an \`icons.theme\` and \`unlock.png\` for the Plymouth boot screen. Neovim and
VS Code need no files here: Omarchy regenerates their configs from
\`colors.toml\` when it stages an installed theme.

\`backdrop/\` holds plates for an **animated wallpaper layer** — this is what
it looks like in motion:

![$name backdrop animation](backdrop/animation.webp)

The plates do nothing on their own — the animation needs the small Quickshell
plugin that ships with the full set:

> **[c0ze/omarchy-themes](https://github.com/c0ze/omarchy-themes)** — all ten
> themes across four families, the backdrop plugin, the About and screensaver
> branding, and the generators that build every asset from its source artwork.

## Where the colours came from

Not one of them was picked by eye. Every value is read out of the project this
theme is named after. There is a [write-up](https://blog.arda.tr/blog/2026-08-23-ten-omarchy-themes/)
and a [three-minute demo](https://youtu.be/2rXn40bUuC8) of all ten.
EOF

echo "$name -> $out"
ls "$out"
