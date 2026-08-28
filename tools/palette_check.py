#!/usr/bin/env python3
"""Contrast and colour-spread report for every theme's colors.toml.

Terminal syntax highlighting in Omarchy runs through the ANSI slots: bat is
pinned to BAT_THEME=ansi, so `red`..`bright_magenta` ARE the colours code is
painted in. A slot that sits under ~4.5:1 on the background reads as mud, and
slots that share a hue read as no highlighting at all.

  ratio   WCAG contrast against `background`
  C       LCh chroma -- how much colour is actually in the slot
  h       LCh hue angle, to spot slots that have collapsed onto each other
"""

import math
import re
import sys
from pathlib import Path

ANSI = ["red", "yellow", "orange", "green", "cyan", "blue", "magenta", "brown"]
BRIGHT = ["bright_" + n for n in ANSI[:1] + ["yellow", "green", "cyan", "blue", "magenta"]]
NEUTRAL = ["foreground", "dark_foreground", "light_foreground", "bright_foreground",
           "muted", "accent"]


def parse(path):
    out = {}
    for line in path.read_text().splitlines():
        m = re.match(r'\s*(\w+)\s*=\s*"(#[0-9a-fA-F]{6})"', line)
        if m:
            out[m.group(1)] = m.group(2).lower()
    return out


def rgb(hexstr):
    h = hexstr.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexstr):
    r, g, b = (lin(c) for c in rgb(hexstr))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def lch(hexstr):
    """sRGB -> CIELCh(ab), D65."""
    r, g, b = (lin(c) for c in rgb(hexstr))
    x = 0.4124 * r + 0.3576 * g + 0.1805 * b
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = 0.0193 * r + 0.1192 * g + 0.9505 * b
    xn, yn, zn = 0.95047, 1.0, 1.08883

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29

    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    bb = 200 * (fy - fz)
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def report(path):
    c = parse(path)
    bg = c["background"]
    print(f"\n\033[1m{path.parent.name}\033[0m  bg {bg}  mode={('light' if luminance(bg) > 0.4 else 'dark')}")
    print(f"  {'slot':<18} {'hex':<9} {'ratio':>6} {'L':>5} {'C':>5} {'h':>5}")
    worst = []
    for name in NEUTRAL + ANSI + BRIGHT:
        if name not in c:
            continue
        v = c[name]
        r = ratio(v, bg)
        L, C, h = lch(v)
        flag = ""
        if name in ANSI + BRIGHT:
            if r < 4.5:
                flag = " \033[31m<4.5\033[0m"
                worst.append((name, r))
            if C < 25:
                flag += " \033[33mflat\033[0m"
        print(f"  {name:<18} {v:<9} {r:>6.2f} {L:>5.1f} {C:>5.1f} {h:>5.0f}{flag}")
    fg = ratio(c["foreground"], bg)
    print(f"  -> foreground {fg:.2f}:1", end="")
    if worst:
        print("   under-contrast ANSI: " + ", ".join(f"{n} {r:.1f}" for n, r in worst))
    else:
        print("   every ANSI slot >= 4.5:1")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    args = sys.argv[1:]
    for p in sorted(root.glob("*/themes/*/colors.toml")):
        if args and not any(a in str(p) for a in args):
            continue
        report(p)
