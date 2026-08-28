#!/usr/bin/env python3
"""Render a code sample through each theme's ANSI palette, offline.

Omarchy pins BAT_THEME=ansi, so `bat` paints syntax with the terminal's 16
colours and the theme's colors.toml decides every one of them:

    31 red      keywords in some languages     35 magenta  keywords
    32 green    strings AND comments           36 cyan     parameters, builtins
    33 yellow   numbers, class names           37 white    plain text (foreground)
    34 blue     function names, dict keys      90 grey     line numbers (muted)

This runs bat, parses the SGR codes it emits, and repaints them with a theme's
palette into a PNG -- so a palette change can be judged without switching the
live theme and taking a screenshot.

    tools/code_swatch.py                 # every theme -> previews/swatches/
    tools/code_swatch.py commit-morning  # one theme
"""

import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = Path("/usr/share/fonts/TTF")
REGULAR = FONT_DIR / "MesloLGSNerdFontMono-Regular.ttf"
BOLD = FONT_DIR / "MesloLGSNerdFontMono-Bold.ttf"

SAMPLE = '''\
import math
from pathlib import Path

CELL = 54                      # px per glyph cell
TAILS = {"head": 1.0, "body": 0.55}


class Column:
    """One falling column of the rain."""

    def __init__(self, x, period=20, phase=0):
        self.x = x
        self.period = period
        self.phase = phase % period

    def alpha(self, row: int) -> float:
        step = (row - self.phase) % self.period
        if step == 0:
            return TAILS["head"]
        return max(0.0, TAILS["body"] * math.exp(-step / 6.0))


def build(path: Path, columns=64, rows=40):
    grid = [Column(i, period=20) for i in range(columns)]
    return [[c.alpha(r) for c in grid] for r in range(rows)]
'''

# 30..37 and 90..97 in colors.toml terms, per omarchy's kitty/alacritty templates.
NORMAL = ["background", "red", "green", "yellow", "blue", "magenta", "cyan", "foreground"]
BRIGHT = ["muted", "bright_red", "bright_green", "bright_yellow",
          "bright_blue", "bright_magenta", "bright_cyan", "bright_foreground"]

SGR = re.compile(r"\x1b\[([0-9;]*)m")


def palette(theme_dir):
    out = {}
    for line in (theme_dir / "colors.toml").read_text().splitlines():
        m = re.match(r'\s*(\w+)\s*=\s*"(#[0-9a-fA-F]{6})"', line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def highlight(text, lang="py"):
    """bat's ANSI output for the sample, as (text, sgr-state) runs per line."""
    proc = subprocess.run(
        ["bat", "--theme=ansi", "--color=always", "--style=numbers",
         "--paging=never", f"--language={lang}"],
        input=text, capture_output=True, text=True, check=True,
    )
    return proc.stdout


def runs(line):
    """Split one ANSI line into (string, fg-slot-or-None, bold) runs."""
    out, pos, fg, bold = [], 0, None, False
    for m in SGR.finditer(line):
        if m.start() > pos:
            out.append((line[pos:m.start()], fg, bold))
        for code in (m.group(1) or "0").split(";"):
            code = int(code or 0)
            if code == 0:
                fg, bold = None, False
            elif code == 1:
                bold = True
            elif code == 22:
                bold = False
            elif 30 <= code <= 37:
                fg = NORMAL[code - 30]
            elif code == 39:
                fg = None
            elif 90 <= code <= 97:
                fg = BRIGHT[code - 90]
        pos = m.end()
    if pos < len(line):
        out.append((line[pos:], fg, bold))
    return out


def render(theme_dir, out_path, size=22, pad=26):
    c = palette(theme_dir)
    reg = ImageFont.truetype(str(REGULAR), size)
    bold = ImageFont.truetype(str(BOLD), size)
    cw = reg.getlength("M")
    ch = int(size * 1.55)

    lines = [l.rstrip("\n") for l in highlight(SAMPLE).split("\n")]
    cols = max(len(SGR.sub("", l)) for l in lines)
    w = int(cols * cw) + pad * 2
    h = ch * len(lines) + pad * 2

    im = Image.new("RGB", (w, h), c["background"])
    d = ImageDraw.Draw(im)
    for row, line in enumerate(lines):
        x = pad
        for text, slot, is_bold in runs(line):
            colour = c.get(slot, c["foreground"]) if slot else c["foreground"]
            d.text((x, pad + row * ch), text, font=bold if is_bold else reg, fill=colour)
            x += cw * len(text)
    im.save(out_path)
    return im


def main():
    args = sys.argv[1:]
    out_dir = ROOT / "previews" / "swatches"
    out_dir.mkdir(parents=True, exist_ok=True)
    made = []
    for toml in sorted(ROOT.glob("*/themes/*/colors.toml")):
        theme = toml.parent
        if args and not any(a in theme.name for a in args):
            continue
        p = out_dir / f"{theme.name}.png"
        render(theme, p)
        made.append(p)
        print(p.relative_to(ROOT))
    if len(made) > 1:
        ims = [Image.open(p) for p in made]
        cols = 2
        rows = (len(ims) + cols - 1) // cols
        cw = max(i.width for i in ims)
        chh = max(i.height for i in ims)
        sheet = Image.new("RGB", (cw * cols, chh * rows), "#101010")
        for i, im in enumerate(ims):
            sheet.paste(im, ((i % cols) * cw, (i // cols) * chh))
        sheet.save(out_dir / "contact-sheet.png")
        print((out_dir / "contact-sheet.png").relative_to(ROOT))


if __name__ == "__main__":
    main()
