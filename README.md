# omarchy-themes

The Gand look for [Omarchy](https://omarchy.org/): three themes, the About /
fastfetch branding, and the screensaver panel. Everything derives from
[gand.tr](https://gand.tr) — its three CSS themes and its logo mark.

```sh
git clone git@github.com:c0ze/omarchy-themes.git ~/projects/gand/omarchy-themes
cd ~/projects/gand/omarchy-themes
./install.sh --theme earth
./tools/fit-about.sh          # only if you installed the fastfetch config
```

`omarchy theme install <url>` will *not* work on this repo: it clones the whole
repo into `~/.config/omarchy/themes/<repo-basename>` and treats it as a single
theme. That command wants one repo per theme with `colors.toml` at the root;
this one carries three themes plus the branding, so use `install.sh`.

## Themes

Mapped 1:1 to the three themes on the site.

| Theme | background | accent | site source |
|---|---|---|---|
| **Gand Dark** | `#0c0c0e` | `#d49a64` | `[data-theme="dark"]` — OLED night |
| **Gand Earth** | `#3a332a` | `#d6a06b` | `:root` / mid — aged manuscript by firelight |
| **Gand Light** | `#f0ebe1` | `#7a4f30` | `[data-theme="light"]` — warm vellum |

The ANSI palette is built from the site's three accents: bronze staff (*gandr*)
as `blue`/`accent`, patina sage as `green`, balbal stone grey as `cyan`, plus an
ember red and heather magenta the site does not define. Every color clears 3.4:1
on its background.

Each theme ships three 3840×2160 wallpapers (`1-sigil`, `2-ring`, `3-vellum`),
a Plymouth `unlock.png`, a neovim colorscheme spec and a VS Code theme mapping.
There is no `preview.png`, so the theme switcher falls back to the first
wallpaper — stock themes put a desktop screenshot there instead.

## Branding

`branding/about.txt` is the sigil at 50×26, inside omarchy's 54×26 logo budget.
`branding/screensaver.txt` is the sigil over the GAND wordmark, the tagline and
the hostname; `install.sh` rewrites that last line for the local machine.

`fastfetch/config.jsonc` is generated *from* omarchy's stock config, so every
module, Nerd Font glyph and box width is identical. Only three things change:
the section headers (`The Stone · Hardware`, `The Staff · Software`,
`The Vigil · Age / Uptime / Update`), the key colors, and a tagline. Key colors
are ANSI *names*, so they track whatever theme is active rather than pinning
Gand's hexes into a global config.

### The About window gotcha

`omarchy-launch-about` measures its content and remembers a window size — but it
skips that pass entirely when `~/.config/fastfetch/config.jsonc` exists. Install
the fastfetch config and About falls back to the 920×480 default float size,
which clips the layout. `tools/fit-about.sh` borrows omarchy's own measurement
with the config moved aside, adds the rows the Gand config contributes, and
writes an `o.window("org.omarchy.about", ...)` rule into `~/.config/hypr/hyprland.lua`.

Re-run it after changing the fastfetch layout, the terminal font, or the logo.

## Rebuilding the art

The logo's gold linework is too low-contrast to dither cleanly at terminal
resolution — a direct transcode is all speckle. `gen_sigil.py` therefore lifts
only the solid serif G out of the artwork (connected-component extraction,
morphologically closed to kill the engraved texture) and redraws the celestial
ring, tick marks, pole nodes, crown star and base finial as vectors around it.

```sh
tools/gen_sigil.py     /tmp/sigil.png      # the clean mark everything else uses
tools/gen_ascii.py     branding/           # about.txt + screensaver.txt
tools/gen_bg.py        themes/             # wallpapers, all three themes
tools/gen_unlock.py    themes/             # Plymouth logos, all three themes
tools/gen_fastfetch.py                     # rewrites ~/.config/fastfetch/config.jsonc
```

They read the logo from `~/projects/gand/gand.tr/public/assets/gand-logo-1024.webp`;
set `GAND_LOGO` to point elsewhere. Needs `python-pillow`, `python-numpy` and
ImageMagick. The generators are deterministic — re-running them reproduces the
committed files byte for byte.
