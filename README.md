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
| [`pagan/`](pagan) | the band *Pagan* ([pagan.tr](https://pagan.tr)) | Pagan Dark · Pagan Light |
| [`pagan-old/`](pagan-old) | Pagan's pre-2019 circular sigil | Pagan Old Dark · Pagan Old Light |

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

## Pagan

The band site already defines exactly two themes, so these are them. Neutrals
and accents are its HSL tokens (`src/index.css`) converted verbatim.

| Theme | background | accent | site source |
|---|---|---|---|
| **Pagan Dark** | `#0A0A0A` | `#25AFF4` | the default: black metal ground, icy blue |
| **Pagan Light** | `#FFFFFF` | `#262626` | "inverted for accessibility" — and monochrome |

The light theme's `accent` is grey on purpose: the site drops *every*
atmospheric token to grey in light mode, so there is no blue to inherit. Its
ANSI slots do carry hue, though — a terminal needs distinguishable colours or
syntax highlighting collapses — as woodcut inks: oxblood, ochre, moss, slate,
iron, plum. The hues neither theme defines (green, yellow, magenta) are kept
cold and desaturated so they stay in register.

Wallpapers take their atmosphere from the site's own fog plates
(`src/assets/fog1.png`, `fog2.png`) rather than synthesised noise, so the
desktop and pagan.tr share the same mist: `1-logo` (the logo in the fog),
`2-fog`, `3-pentagram` (the element at the centre of the logo, drawn large).

Nothing sets the band name in type. A black metal logo *is* the wordmark and
its illegibility is the point, so the About logo, the screensaver and the
Plymouth strip are all the logo alone. The screensaver's one line of text is
`IN HOC SIGNO VINCES` — the band's own first demo, 1995.

## Animated fog

Pagan's wallpapers can drift. `shell/gand.fog` is a small Quickshell plugin that
lays slowly moving fog over the wallpaper, ported from pagan.tr's own `fog.css`
— same plates, same timings.

A theme opts in by shipping a `fog/` directory: the plates, plus a `fog.json`
naming a profile and an intensity. Themes without one cost nothing, because the
layer model stays empty and no animation is ever created. Only Pagan ships one
today; drop a `fog/` into any other theme and it picks it up.

```
pagan/themes/pagan-dark/fog/{fog1.png,fog2.png,fog.json}   profile "fog",  3 layers
pagan/themes/pagan-light/fog/{...}                          profile "mist", 2 layers
```

Two details worth keeping:

- **Movement and opacity run on unrelated periods** (15s/13s against 10s/21s).
  That beat is what reads as swirling rather than sliding — matching the periods
  would just look like a sheet moving sideways.
- **The light profile's plates ship pre-inverted**, so its fog is dark rather
  than luminous. White fog over a white ground is invisible; the site solves the
  same problem with `filter: invert(1)`, and doing it in the plate means no
  runtime shader. The plates also carry an alpha channel taken from their own
  luminance, so only the fog draws — an opaque plate would veil the whole frame
  and wash the logo back out.

It is **not** a fork of `omarchy.background`. It draws its own surface on
`WlrLayer.Bottom` — above the wallpaper, below ordinary windows — masked to an
empty input region so clicks fall through as usual. That way the stock
background renderer keeps updating normally, and a mistake here cannot leave the
desktop black.

**Dark asks for far more mark contrast than light** (6.5:1 against 3.4:1), and
gets less fog (0.14 against 0.20). An equal ratio is not an equal read: light
puts a dark mark at ~105 on a ~200 ground, a wide absolute separation, while
dark puts a mid-grey at ~139 on ~62 — and luminous fog lifts that ground from
37, halving the separation the mark had before the fog existed. Measured on
screen across a fog cycle, dark now holds 5.6–6.0:1 and light 3.3–3.4:1.

**Fog intensity is 0.20/0.14, not the site's values.** pagan.tr's fog sits over a small
hero; scaled to a 4K wallpaper the same opacities produce a wall of cloud that
swallows the logo. Measured against real captures, the mark falls from 3.72:1
with no fog to 2.28:1 at 0.55 — 0.20 keeps the drift and leaves the mark at
~3.4:1. Change it live:

```sh
$EDITOR ~/.config/omarchy/themes/pagan-dark/fog/fog.json
omarchy-shell fog refresh
```

Turn it off with `omarchy plugin disable gand.fog`, or skip it at install with
`--no-fog`. Cost while the desktop is covered measured at 0.0% CPU: Hyprland
withholds frame callbacks from an occluded surface, so it idles rather than
animating behind your windows.

## Pagan Old

The band's earlier mark: an inverted pentagram in a ring with PAGAN worked into
its arms, hand-drawn. Same palette, same fog, same fastfetch panel as `pagan` —
the era changed the mark, not the colours — so the only difference is the
artwork. Wallpapers are `1-seal`, `2-veil`, `3-halo`; the third is the sigil
oversized until it bleeds off the frame, since a drawn pentagram would just
repeat what the mark already is.

Both Pagan variants come out of one pair of generators via `--variant`:

```sh
pagan/tools/gen_pagan_bg.py     pagan-old/themes --variant old
pagan/tools/gen_pagan_assets.py pagan-old/themes pagan-old/branding --variant old
```

The old sigil is drawn in ~15px hairlines on a 3307px canvas. Scaled to a
terminal grid (30× down) or a Plymouth strip (20× down) those vanish entirely,
so `thicken()` dilates the alpha first, solving for the radius that lands a
stroke at about two output pixels. It pads before dilating — the mask is
cropped to its bounding box, and dilating in place clips the ring.

## Wallpaper filenames must be unique across families

Every theme's wallpaper resolves to the same path —
`~/.local/state/omarchy/current/theme/backgrounds/<name>` — and Omarchy's
background renderer loads it with `cache: true`. Qt keys its pixmap cache on
that URL, so two themes sharing a wallpaper *basename* can serve each other's
stale image after a theme switch.

Pagan originally shipped `1-sigil.webp`, colliding with Gand's; it is now
`1-logo.webp`. Keep basenames distinct across families:

| Family | Wallpapers |
|---|---|
| gand | `1-sigil` `2-ring` `3-vellum` |
| commit | `1-pulse` `2-graph` `3-crt` |
| pagan | `1-logo` `2-fog` `3-pentagram` |

Also worth knowing: `omarchy theme set` advances to the *next* wallpaper in the
theme every time it runs, so a run of theme switches walks the selection along.
To land on a specific one:

```sh
omarchy theme bg set ~/.local/state/omarchy/current/theme/backgrounds/1-logo.webp
```

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

**Never leave a backup copy inside `theme-set.d/`.** `omarchy-hook` runs *every*
file in that directory, so a timestamped copy keeps executing after the real one
and silently re-applies whatever routing it had — which is exactly how
`pagan-old-*` kept resolving to `pagan`. `install.sh` sweeps any it finds. For
the same reason the family match for `pagan-old-*` has to precede `pagan-*` in
the case statement, or the prefix swallows it.

### The About window gotcha

`omarchy-launch-about` measures its content and remembers a window size — but it
skips that pass entirely when `~/.config/fastfetch/config.jsonc` exists. Install
a family's fastfetch config and About falls back to the 920×480 default float
size, which clips the layout. `tools/fit-about.sh` probes the terminal at two
sizes to solve for its cell size *and* padding (padding is a fixed offset, not a
proportion — dividing height by rows undercounts it and clips the top), then
writes an `o.window("org.omarchy.about", ...)` rule into `~/.config/hypr/hyprland.lua`.

One rule covers every family as long as it was measured against the *widest*
logo: Pagan's is 54 columns, Gand's 50, Commit's 45. So measure with a Pagan
theme active — measuring against a narrower one clips the panel's right edge for
the others. Re-run after changing the fastfetch layout, the terminal, its font,
or a logo's dimensions.

## Rebuilding the art

Gand and Commit face the same problem: the source artwork does not survive
downscaling to a terminal grid. Gand's logo has gold linework too low-contrast
to dither cleanly; the Commit icon is 256px pixel art that turns to mush. Both
answers are the same — lift the one solid element out of the original and redraw
everything around it as vectors. Pagan needs none of that: its logo is already a
high-contrast alpha PNG (despite the `.jpg` name), so the transcoder takes it
directly.

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

pagan/tools/gen_pagan_assets.py   pagan/themes/ pagan/branding/
pagan/tools/gen_pagan_bg.py       pagan/themes/
pagan/tools/gen_pagan_fastfetch.py pagan/fastfetch/config.jsonc
```

Gand's generators read the logo from
`~/projects/gand/gand.tr/public/assets/gand-logo-1024.webp` (`GAND_LOGO`
overrides); Pagan's read the logo and fog from `~/projects/music/pagan/pagan.tr`
(`PAGAN_SITE`); Commit's redraw the icon from scratch and need no source art. Needs
`python-pillow`, `python-numpy` and ImageMagick. All are deterministic — a
re-run reproduces the committed files byte for byte.
