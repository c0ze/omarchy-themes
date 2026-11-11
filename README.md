# omarchy-themes

[Omarchy](https://omarchy.org/) theme families, each derived from one of my own
projects: colours, wallpapers, the About panel and the screensaver.

[![Watch the demo: ten Omarchy themes](https://img.youtube.com/vi/2rXn40bUuC8/maxresdefault.jpg)](https://youtu.be/2rXn40bUuC8)

*Every theme for fifteen seconds, plus each family's About panel and screensaver — [3m33s](https://youtu.be/2rXn40bUuC8). There is a [write-up of how it was built](https://blog.arda.tr/blog/2026-08-23-ten-omarchy-themes/) too.*

```sh
git clone git@github.com:c0ze/omarchy-themes.git ~/projects/gand/omarchy-themes
cd ~/projects/gand/omarchy-themes
./install.sh                     # all families
./install.sh commit --theme late-night
./tools/fit-about.sh             # once per machine, if you installed branding
```

| Family | Source | Themes |
|---|---|---|
| [`gand/`](gand) | [gand.tr](https://gand.tr) — the studio | Gand Dark · Gand Earth · Gand Light |
| [`commit/`](commit) | [commit.gand.tr](https://commit.gand.tr) — the game | Commit Late Night · Commit Evening · Commit Morning |
| [`pagan/`](pagan) | [pagan.tr](https://pagan.tr) — the band | Pagan Dark · Pagan Light |
| [`pagan-old/`](pagan-old) | Pagan's pre-2019 sigil | Pagan Old Dark · Pagan Old Light |
| [`forest/`](forest) | [arda.tr](https://arda.tr) — One Bit Forest | Forest Night · Forest Dusk · Forest Xerox |

`omarchy theme install <url>` will *not* work on this repo: it clones the whole
repo into `~/.config/omarchy/themes/<repo-basename>` and treats it as a single
theme. That command wants one repo per theme with `colors.toml` at the root; use
`install.sh` here.

That one-repo-per-theme shape is also what
[omarchy.org/themes](https://omarchy.org/themes) lists. The split-out repos —
exported from here with `tools/split-theme.sh`, so a copy, not a rewrite:

| Theme | Repo |
|---|---|
| Commit Late Night | [c0ze/omarchy-commit-theme](https://github.com/c0ze/omarchy-commit-theme) |
| Commit Evening | [c0ze/omarchy-commit-evening-theme](https://github.com/c0ze/omarchy-commit-evening-theme) |
| Commit Morning | [c0ze/omarchy-commit-morning-theme](https://github.com/c0ze/omarchy-commit-morning-theme) |
| Gand Earth | [c0ze/omarchy-gand-theme](https://github.com/c0ze/omarchy-gand-theme) |
| Gand Dark | [c0ze/omarchy-gand-dark-theme](https://github.com/c0ze/omarchy-gand-dark-theme) |
| Gand Light | [c0ze/omarchy-gand-light-theme](https://github.com/c0ze/omarchy-gand-light-theme) |
| Pagan Dark | [c0ze/omarchy-pagan-theme](https://github.com/c0ze/omarchy-pagan-theme) |
| Pagan Light | [c0ze/omarchy-pagan-light-theme](https://github.com/c0ze/omarchy-pagan-light-theme) |

Commit Late Night, Gand Earth and Pagan Dark are listed on
[omarchy.org/themes](https://omarchy.org/themes); the rest install from their
repos the same way.

## Gand

**[gand.tr](https://gand.tr)** — an independent software studio between Istanbul
and Tokyo, building small focused products: [Skriv.ist](https://skriv.ist/),
[Fable Spun Kids](https://kids.fable.tr/), [Vigil Today](https://vigil.today/),
[SUDONE](https://sudone.jp/). Source on [GitHub](https://github.com/gandtr).

Mapped 1:1 to the three themes on the site.

| Theme | background | accent | site source |
|---|---|---|---|
| **Gand Dark** | `#0c0c0e` | `#d49a64` | `[data-theme="dark"]` — OLED night |
| **Gand Earth** | `#3a332a` | `#d6a06b` | `:root` / mid — aged manuscript by firelight |
| **Gand Light** | `#f0ebe1` | `#7a4f30` | `[data-theme="light"]` — warm vellum |

The ANSI palette is built from the site's three accents: bronze staff (*gandr*)
as `accent`, patina sage as `green`, balbal stone grey as `blue` and `cyan`,
plus an ember red and heather magenta the site does not define. Wallpapers:
`1-sigil`, `2-ring`, `3-vellum`.

`blue` used to *be* the bronze accent, which meant function names, numbers and
keywords all landed on one warm hue and code read as one colour. It now comes
off the balbal stone with enough chroma to tell itself apart, and `cyan` turns
the same stone toward verdigris. Every ANSI slot clears 4.5:1 on its
background — `tools/palette_check.py` is the report, `tools/code_swatch.py`
renders a file through a palette without switching the live theme.

## Commit!!!

**[commit.gand.tr](https://commit.gand.tr)** — a software-career sim: push code,
pull requests, merge a life. Built in Godot 4 for Windows, Linux and Android.
Pay once, no ads, no accounts, works offline.

**Out now** on **[Steam](https://store.steampowered.com/app/4994630/)** and
**[Google Play](https://play.google.com/store/apps/details?id=tr.gand.commit)**.

The game ships a fully specified CRT palette in `commit/game/theme/palette.gd`,
with WCAG ratios worked out in its comments. **Late Night is that palette
verbatim** — it is the game's own look, not an interpretation. The three themes
are the game's own Commit Slots, the mechanic the whole sim runs on.

| Theme | background | accent | reading |
|---|---|---|---|
| **Commit Late Night** | `#0B0F14` | `#5AF78E` | the shipped palette: phosphor green on a cold CRT ground |
| **Commit Evening** | `#12100A` | `#FFB454` | the other classic phosphor; the amber of the `!!!` promoted to body text |
| **Commit Morning** | `#EEF1F5` | `#00793B` | the CRT ground inverted into ink on paper |

Accents across all three are the game's Snazzy-family ANSI set. Wallpapers:
`1-pulse` (the Commit Pulse bar, zone colours straight from `ZONE_COLORS`),
`2-graph` (branch-and-merge lanes), `3-crt` (scanlines and phosphor glow only).

**`accent` and `blue` are deliberately different here.** Every stock Omarchy
theme sets them equal, but the templates use them independently — `accent`
drives the bar and window borders, `blue` is an ANSI slot. Collapsing them would
make terminal blue and green identical and flatten syntax highlighting, so the
phosphor green stays the accent while `blue` keeps the palette's own `#57C7FF`.

## Pagan

**[pagan.tr](https://pagan.tr)** — Turkish black metal from Istanbul, exploring
paganism, shamanism and mysticism since 1995.
[Bandcamp](https://pagantr.bandcamp.com) ·
[Spotify](https://open.spotify.com/artist/4MoLQW8VHxjNk2vPxkpLqF) ·
[YouTube](https://www.youtube.com/@pagantr) ·
[Metal Archives](https://www.metal-archives.com/bands/Pagan/4260)

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

## Forest

**[arda.tr](https://arda.tr)** — and blog.arda.tr, resume.arda.tr and
ai.arda.tr, which share its design: **One Bit Forest**, a night spruce valley
ordered-dithered to one bit, with one neon phosphor per site. arda.tr's is
lichen. Everything pictorial on those sites is dithered live by `onebit.js`;
here `forest/tools/onebit.py` ports the valley from it — the same rng, noise,
spruce and ridge-top radio mast, seed 2004 — so the desktop and the hero are
the same place.

| Theme | background | accent | site source |
|---|---|---|---|
| **Forest Night** | `#060708` | `#c6ff3a` | `night`, the default: bone ink on near-black |
| **Forest Dusk** | `#31352e` | `#c6ff3a` | none — the mid ground the site does not have |
| **Forest Xerox** | `#efede6` | `#3f5f00` | `xerox`: the valley photocopied, printed as a positive |

Neutrals are the site's tokens verbatim (`--bg`, `--surface`, `--fg`, `--fg-2`,
`--signal`); Dusk is derived between them and still prints as a night, so its
moon stays bright. The site has no hue but the signal, so the ANSI slots are
pale inks by night and toner inks on Xerox, low in chroma, with `green` set to
the lichen itself so the fastfetch keys and a terminal's green are the signal.

Wallpapers are the scene at 640x360 — what `forest()` renders at on a 4K screen
— enlarged 6x with nearest-neighbour and saved lossless (about 10 KiB each):
`1-valley` (the site's hero, moon high on the right), `2-stars` (moonless, the
Milky Way), `3-moonrise` (a full moon half behind the far ridge). All three
share one valley and differ only in the sky, which is what lets one set of
backdrop plates serve all three.

The terminal art is a positive emblem rather than the dithered scene: dithered
into braille, the dark spruces become gaps in a grey field and vanish. The
Plymouth strip and the screensaver wordmark set `arda.tr` in a monospace
rendered without antialiasing — pixel type, as an early Mac would draw it —
after a block of signal, the site's own mark.

## Animated backdrop

`shell/gand.backdrop` is a small Quickshell plugin that animates plates over the
wallpaper. A theme opts in by shipping a `backdrop/` directory: the plates, plus
a `backdrop.json` naming a profile, an intensity and a speed. Themes without one
cost nothing — the layer model stays empty and no animation is created.

Four kinds of motion, because each family wants a different one:

| Profile | Kind | Used by |
|---|---|---|
| `fog` | drift, 3 layers | Pagan Dark |
| `mist` | drift, 2 layers, inverted plates | Pagan Light |
| `orrery` | spin, 3 rings | all three Gand themes |
| `pulse` | rain × 3 behind sweep × 1 | all three Commit themes |
| `valley` | drift × 2 between still × 2, pixelated | all three Forest themes |

`kind` is a property of the profile, but a layer may override it: `pulse` is the
one profile that mixes two.

**drift** slides two copies of each plate sideways by exactly one copy width, so
the wrap is seamless. Ported from pagan.tr's `fog.css`: movement and opacity run
on deliberately unrelated periods (15s/13s against 10s/21s), and that beat is
what reads as swirling rather than sliding.

**spin** rotates plates about the screen centre at different rates in opposing
directions. Gand's mark is an astronomical device — a serif G inside a ticked
ring with laurel, crescents and dotted orbits — so its backdrop turns rather
than drifts. `gen_orrery.py` draws three concentric rings to match: a ticked
ring, a dotted orbit carrying eight four-point stars, and a hairline ring with
crescents at the poles. Periods are 7, 5 and 9 minutes per revolution. An orrery
that visibly turns is a fidget; this should only be noticeable if you sit and
watch it.

**sweep** translates a plate across a bounded span and reverses.
`pulse_screen.gd` opens by describing the game's core interaction as "a cursor
ping-pongs across a colored bar", so that is what the Commit backdrop is. The
plate holds only the cursor, drawn on a canvas with the same 16:9 geometry the
wallpapers use and rendered the same way, so on `1-pulse` it tracks the real bar
it was drawn against rather than floating free of it. The bar's baked-in static
cursor was removed once the live one existed — two cursors on one bar read as a
mistake. A full there-and-back is 18s: the game's cursor is frantic by design,
and a backdrop that frantic would be unusable.

**rain** falls: two copies of a plate stacked vertically, scrolled by exactly
one screen height so the wrap is seamless — drift turned through ninety degrees.
Commit's glyph waterfall runs three of them behind the cursor. `gen_rain.py`
hands each plate one third of the columns (0, 3, 6… on the first, 1, 4, 7… on
the second) and the shell falls them at 31s, 43s and 57s per screen, so
neighbouring columns never descend together and the three sheets never re-align
into one visible front. A column's brightness is a function of `(row - phase)
mod period` and every period divides the 40 rows, so what leaves the bottom is
what arrives at the top. Glyphs are half-width katakana mirrored as the film's
are, salted with digits that are not — a mirrored numeral just reads as a broken
glyph. They do not re-roll as they fall: the plate is a static image the shell
translates, trading the flicker for one texture and no per-frame work. Ink is
per theme — phosphor green under white heads on Late Night, amber under cream on
Evening, and on Morning the CRT ground becomes the ink, exactly as the cursor
does, because pale rain on pale paper would not be there at all.

**valley** animates what the site animates on top of the valley, and leaves the
valley itself still. Scrolling it in parallax, as the hero does, would need
opaque moving strips: over the wallpaper's own trees they ghost (the far
ridge's mast showed twice), and hiding the wallpaper under a sky plate would
bury the desktop widgets that share the background layer. So two one-bit fog
sheets drift through the site's fog bands at 300s and 210s per screen, and a
**still** plate — a layer that does not move, only runs its opacity stops —
lays an exact copy of the middle and near spruces over them, so the fog passes
behind the trees. Fog is not in the wallpapers; with the plugin off the valley
is clear. The mast light is a second still plate holding the mast top *unlit*:
the wallpaper has it lit, the plate covers it for 60% of a 3s beat, and it
blinks. `pixelated` draws the 640x360 plates unsmoothed, so each lands on the
wallpaper's 6x6 grid instead of blurring to grey.

All five are tunable live, without touching QML:

```sh
$EDITOR ~/.config/omarchy/themes/gand-earth/backdrop/backdrop.json
omarchy-shell backdrop refresh
```

`intensity` is the master opacity; `speed` multiplies the rate (2.0 is twice as
fast, 0.5 half). Commit's is 1.0, because it covers every layer alike and the
cursor is meant to be a hard line, not a ghost of one — the rain carries its own
dimming in the plate alphas instead. Pagan's is 0.20/0.14 rather than the site's
values:
`fog.css` is tuned for a small hero, and at 4K the same opacities produce a wall
of cloud that swallows the mark — measured, it fell from 3.72:1 to 2.28:1.

Turn it off with `omarchy plugin disable gand.backdrop`, or skip it at install
with `--no-backdrop`. Cost while the desktop is covered measured at 0.0% CPU:
Hyprland withholds frame callbacks from an occluded surface, so it idles rather
than animating behind your windows.

Three things that bit, all worth keeping in mind when editing the QML:

- A `NumberAnimation on x` claims the property as a value source *even while
  stopped*, destroying any binding on it. Drift animates a separate `driftX`
  so spin layers keep their centring binding.
- A running animation keeps the `to` it started with. The layer surface is
  only configured after it turns visible, so drift, rain and sweep started at
  width 0 and animated from 0 to 0 forever: every drifting and falling
  backdrop stood still until they were made to wait for `panel.width > 0`.
- Escaped quotes inside a QML string collapse. The resolver's `jq` filters are
  passed bare (`jq -r .speed`) for that reason; `jq -r ".speed // 1"` silently
  became `.speed // 1` unquoted and fell back on every read.

## Pagan Old

**[pagan.tr](https://pagan.tr)** — the same band, its earlier mark.

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

## Wallpaper selection, and why filenames carry the theme

Setting a theme *does* change the wallpaper — but not to the theme's first one.
`omarchy-theme-set` picks the background **after** whichever is currently
linked, and only falls back to the first when nothing in the new theme matches
the old link:

```bash
if (( index == -1 )); then CHOSEN_THEME_BACKGROUND="${backgrounds[0]}"
else next_index=$(((index + 1) % ${#backgrounds[@]}))
```

That comparison is against the resolved path, and every theme's wallpapers live
at the same path — `~/.local/state/omarchy/current/theme/backgrounds/<name>`.
So while sibling themes shared basenames, switching dark→light always *advanced*
one step, landing you on a wallpaper without the mark two times in three.

Basenames therefore carry the theme: `1-seal-dark.webp`, `1-seal-light.webp`.
Nothing matches across themes, `index` comes back -1, and a theme switch lands
on `backgrounds[0]` — the `1-` mark wallpaper. Re-applying the *same* theme
still advances, which is a reasonable way to cycle, as is `omarchy theme bg
next`. To pin one:

```sh
omarchy theme bg set ~/.local/state/omarchy/current/theme/backgrounds/1-seal-dark.webp
```

The same uniqueness closes a second hazard: Qt caches the background by URL, and
with a shared path plus a shared basename one theme could serve another's stale
image.

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

forest/tools/gen_forest_bg.py       forest/themes/        # ~1 min: pure-Python port
forest/tools/gen_forest_assets.py   forest/themes/ forest/branding/
forest/tools/gen_forest_fastfetch.py forest/fastfetch/config.jsonc
tools/gen_backdrop_anim.py          forest/themes/forest-night
```

Gand's generators read the logo from
`~/projects/gand/gand.tr/public/assets/gand-logo-1024.webp` (`GAND_LOGO`
overrides); Pagan's read the logo and fog from `~/projects/music/pagan/pagan.tr`
(`PAGAN_SITE`); Commit's redraw the icon from scratch and need no source art; Forest's draw
the valley from its seed and need nothing either. Needs
`python-pillow`, `python-numpy` and ImageMagick. All are deterministic — a
re-run reproduces the committed files byte for byte.
