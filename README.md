# omarchy-themes

[Omarchy](https://omarchy.org/) theme families, each derived from one of my own
projects: colours, wallpapers, the About panel and the screensaver.

```sh
git clone git@github.com:c0ze/omarchy-themes.git ~/projects/gand/omarchy-themes
cd ~/projects/gand/omarchy-themes
./install.sh                     # all families
./install.sh commit --theme late-night
./tools/fit-about.sh             # once per machine, if you installed branding
```

| Family | Source | Themes |
|---|---|---|
| [`gand/`](gand) | [gand.tr](https://gand.tr) | Gand Dark · Gand Earth · Gand Light |
| [`commit/`](commit) | the game *Commit!!!* | Commit Late Night · Commit Evening · Commit Morning |

`omarchy theme install <url>` will *not* work on this repo: it clones the whole
repo into `~/.config/omarchy/themes/<repo-basename>` and treats it as a single
theme. That command wants one repo per theme with `colors.toml` at the root; use
`install.sh`.

## Gand

Mapped 1:1 to the three themes on the site.

| Theme | background | accent | site source |
|---|---|---|---|
| **Gand Dark** | `#0c0c0e` | `#d49a64` | `[data-theme="dark"]` — OLED night |
| **Gand Earth** | `#3a332a` | `#d6a06b` | `:root` / mid — aged manuscript by firelight |
| **Gand Light** | `#f0ebe1` | `#7a4f30` | `[data-theme="light"]` — warm vellum |

The ANSI palette is built from the site's three accents: bronze staff (*gandr*)
as `blue`/`accent`, patina sage as `green`, balbal stone grey as `cyan`, plus an
ember red and heather magenta the site does not define. Every colour clears
3.4:1 on its background. Wallpapers: `1-sigil`, `2-ring`, `3-vellum`.

## Commit!!!

The game ships a fully specified CRT palette in `commit/game/theme/palette.gd`,
with WCAG ratios worked out in its comments. **Late Night is that palette
verbatim** — it is the game's own look, not an interpretation. The three themes
are the game's own Commit Slots, the mechanic the whole sim runs on.

| Theme | background | accent | reading |
|---|---|---|---|
| **Commit Late Night** | `#0B0F14` | `#5AF78E` | the shipped palette: phosphor green on a cold CRT ground |
| **Commit Evening** | `#12100A` | `#FFB454` | the other classic phosphor; the amber of the `!!!` promoted to body text |
| **Commit Morning** | `#EEF1F5` | `#0F8A4B` | the CRT ground inverted into ink on paper |

Accents across all three are the game's Snazzy-family ANSI set. Wallpapers:
`1-pulse` (the Commit Pulse bar, zone colours straight from `ZONE_COLORS`),
`2-graph` (branch-and-merge lanes), `3-crt` (scanlines and phosphor glow only).

**`accent` and `blue` are deliberately different here.** Every stock Omarchy
theme sets them equal, but the templates use them independently — `accent`
drives the bar and window borders, `blue` is an ANSI slot. Collapsing them would
make terminal blue and green identical and flatten syntax highlighting, so the
phosphor green stays the accent while `blue` keeps the palette's own `#57C7FF`.

## Branding, and why there is a hook

Themes from every family coexist in the theme list. Branding does not: Omarchy
has exactly one About logo, one screensaver panel and one user fastfetch config.

So `install.sh` stages each family's branding under
`~/.config/omarchy/branding/families/<name>/` and installs a `theme-set` hook
that swaps the live slot whenever you pick a theme from that family. Pick Commit
Late Night and the About logo becomes the commit graph; pick Gand Earth and it
becomes the sigil. Stock themes are left alone, so whatever was last installed
stays. `--no-branding` skips the whole mechanism.

Both `omarchy-launch-about` and `omarchy-screensaver` read only `about.txt` and
`screensaver.txt`, so the `families/` subdirectory is inert to them.

### The About window gotcha

`omarchy-launch-about` measures its content and remembers a window size — but it
skips that pass entirely when `~/.config/fastfetch/config.jsonc` exists. Install
a family's fastfetch config and About falls back to the 920×480 default float
size, which clips the layout. `tools/fit-about.sh` probes the terminal at two
sizes to solve for its cell size *and* padding (padding is a fixed offset, not a
proportion — dividing height by rows undercounts it and clips the top), then
writes an `o.window("org.omarchy.about", ...)` rule into `~/.config/hypr/hyprland.lua`.

One rule covers both families as long as it was measured against the *widest*
logo — Gand's is 50 columns, Commit's 45. Re-run it after changing the fastfetch
layout, the terminal, its font, or a logo's dimensions.

## Rebuilding the art

Both families face the same problem: the source artwork does not survive
downscaling to a terminal grid. Gand's logo has gold linework too low-contrast
to dither cleanly; the Commit icon is 256px pixel art that turns to mush. Both
answers are the same — lift the one solid element out of the original and redraw
everything around it as vectors.

```sh
gand/tools/gen_sigil.py    /tmp/s.png    # G lifted by connected component, ring redrawn
gand/tools/gen_ascii.py    gand/branding/
gand/tools/gen_bg.py       gand/themes/
gand/tools/gen_unlock.py   gand/themes/
gand/tools/gen_fastfetch.py

commit/tools/gen_commit_sigil.py  graph /tmp/g.png   # mark, or mark in a commit graph
commit/tools/gen_commit_assets.py commit/themes/ commit/branding/
commit/tools/gen_commit_bg.py     commit/themes/
commit/tools/gen_commit_fastfetch.py commit/fastfetch/config.jsonc
```

Gand's generators read the logo from
`~/projects/gand/gand.tr/public/assets/gand-logo-1024.webp` (`GAND_LOGO`
overrides); Commit's redraw the icon from scratch and need no source art. Needs
`python-pillow`, `python-numpy` and ImageMagick. All are deterministic — a
re-run reproduces the committed files byte for byte.
