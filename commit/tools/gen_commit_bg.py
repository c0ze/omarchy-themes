#!/usr/bin/env python3
"""Generate Commit!!! theme wallpapers.

Three per theme, all on a scanlined CRT ground:
  1-pulse  the Commit Pulse bar, the game's signature screen
  2-graph  a branch-and-merge commit graph
  3-crt    quiet phosphor glow and scanlines, nothing else

    ./gen_commit_bg.py themes/
"""
import math, os, sys

import numpy as np
from PIL import Image, ImageDraw

W, H = 3840, 2160
SCAN_PERIOD = 4          # px between scanlines at 4K


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def radial(cx, cy, radius, power=1.0):
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - cx) / radius) ** 2 + ((y - cy) / radius) ** 2)
    return np.clip(1.0 - d, 0.0, 1.0) ** power


def grain(amount, seed):
    rng = np.random.default_rng(seed)
    n = rng.normal(0.0, amount, (H // 2, W // 2)).astype(np.float32)
    return np.asarray(Image.fromarray(n, mode="F").resize((W, H), Image.BILINEAR))[..., None]


def scanlines(strength):
    """Darken every other band, the way a CRT's raster does."""
    rows = (np.arange(H) % SCAN_PERIOD) < (SCAN_PERIOD // 2)
    return np.where(rows, 1.0, 1.0 - strength)[:, None, None]


def layer(base, art, colour, alpha):
    """Composite a greyscale coverage map in one colour over base."""
    a = (art * alpha)[..., None]
    return base * (1.0 - a) + colour * a


def draw(fn, supersample=2):
    """Render a drawing callback at 2x and box-filter it down."""
    img = Image.new("L", (W // supersample, H // supersample), 0)
    fn(ImageDraw.Draw(img), W // supersample, H // supersample)
    img = img.resize((W, H), Image.LANCZOS)
    return np.asarray(img, dtype=np.float64) / 255.0


# The Commit Pulse zone colours, from commit/game/theme/palette.gd's ZONE_COLORS.
ZONES = [
    ("red", "#FF5C57", 0.13), ("yellow", "#F3F99D", 0.09),
    ("green", "#5AF78E", 0.11), ("perfect", "#57C7FF", 0.05),
    ("green", "#5AF78E", 0.10), ("yellow", "#F3F99D", 0.08),
    ("red", "#FF5C57", 0.20), ("red", "#FF5C57", 0.24),
]

THEMES = {
    "commit-late-night": dict(
        bg="#0B0F14", glow="#18232F", edge="#030507",
        ink="#5AF78E", dim="#33486A", scan=0.30, grain=2.4, art=1.0),
    "commit-evening": dict(
        bg="#12100A", glow="#2A2314", edge="#080704",
        ink="#FFB454", dim="#5C4A2C", scan=0.30, grain=2.6, art=1.0),
    "commit-morning": dict(
        bg="#EEF1F5", glow="#FFFFFF", edge="#D1D9E3",
        ink="#0F8A4B", dim="#8797A8", scan=0.10, grain=1.8, art=0.85),
}


def ground(t, cx, cy, radius, power):
    glow, edge, bg = hexrgb(t["glow"]), hexrgb(t["edge"]), hexrgb(t["bg"])
    g = radial(cx, cy, radius, power)
    canvas = edge + (glow - edge) * g[..., None]
    return canvas * 0.55 + bg * 0.45


def pulse_lattice(d, w, h):
    """The faint diagonal graph lines the Pulse screen draws behind the bar."""
    stroke = max(1, int(w * 0.0012))
    for band in (0.17, 0.78):
        y = band * h
        span = 0.16 * h
        for k in range(-1, 5):
            x = (0.10 + k * 0.20) * w
            d.line([(x, y), (x + 0.10 * w, y - span), (x + 0.20 * w, y)],
                   fill=255, width=stroke)
        d.line([(0, y), (w, y)], fill=255, width=stroke)


def pulse_bar(d, w, h):
    """The Pulse Bar frame: the outline plus the stop cursor."""
    bw, bh = int(w * 0.66), int(h * 0.075)
    x0, y0 = (w - bw) // 2, int(h * 0.46)
    edge = max(2, int(w * 0.0016))
    pad = int(h * 0.008)
    d.rectangle([x0 - pad, y0 - pad, x0 + bw + pad, y0 + bh + pad],
                outline=255, width=edge)
    cx = x0 + int(bw * 0.615)
    d.rectangle([cx - edge, y0 - int(h * 0.022), cx + edge, y0 + bh + int(h * 0.022)],
                fill=255)


def pulse_zones():
    """Coverage maps per zone colour, so each can be tinted separately."""
    bw, bh = int(W * 0.66), int(H * 0.075)
    x0, y0 = (W - bw) // 2, int(H * 0.46)
    out = []
    x = x0
    for _, colour, frac in ZONES:
        span = int(bw * frac)
        img = Image.new("L", (W, H), 0)
        ImageDraw.Draw(img).rectangle([x, y0, x + span, y0 + bh], fill=255)
        out.append((colour, np.asarray(img, dtype=np.float64) / 255.0))
        x += span
    return out


def commit_graph(d, w, h):
    """Branch-and-merge lanes drifting up the canvas."""
    stroke = max(2, int(w * 0.0035))
    r = int(w * 0.0090)

    def node(x, y):
        d.ellipse([x - r, y - r, x + r, y + r], fill=255)

    lanes = [0.20, 0.30, 0.40]
    d.line([(lanes[0] * w, -0.05 * h), (lanes[0] * w, 1.05 * h)], fill=255, width=stroke)
    for i in range(9):
        node(lanes[0] * w, (0.02 + i * 0.12) * h)

    # Two side branches, each leaving the trunk and merging back further up.
    for lane, (top, bot) in zip(lanes[1:], [(0.08, 0.42), (0.54, 0.92)]):
        d.line([(lanes[0] * w, bot * h), (lane * w, (bot - 0.06) * h),
                (lane * w, (top + 0.06) * h), (lanes[0] * w, top * h)],
               fill=255, width=stroke, joint="curve")
        steps = int((bot - top) / 0.12)
        for i in range(1, steps):
            node(lane * w, (top + 0.06 + i * 0.12) * h)


def main():
    out_root = sys.argv[1]
    for name, t in THEMES.items():
        d = os.path.join(out_root, name, "backgrounds")
        os.makedirs(d, exist_ok=True)
        ink, dim = hexrgb(t["ink"]), hexrgb(t["dim"])
        print(name)

        # 1 - pulse
        canvas = ground(t, W * 0.5, H * 0.50, W * 0.85, 1.3)
        canvas = layer(canvas, radial(W * 0.5, H * 0.50, W * 0.42, 2.0), ink,
                       0.05 * t["art"])
        for colour, cov in pulse_zones():
            canvas = layer(canvas, cov, hexrgb(colour), 0.34 * t["art"])
        canvas = layer(canvas, draw(pulse_lattice), dim, 0.40 * t["art"])
        canvas = layer(canvas, draw(pulse_bar), ink, 0.42 * t["art"])
        canvas = canvas * scanlines(t["scan"]) + grain(t["grain"], 3)
        save(canvas, os.path.join(d, wp("1-pulse", name, "commit")))

        # 2 - graph
        canvas = ground(t, W * 0.30, H * 0.45, W * 1.00, 1.15)
        canvas = layer(canvas, draw(commit_graph), dim, 0.55 * t["art"])
        canvas = canvas * scanlines(t["scan"]) + grain(t["grain"], 17)
        save(canvas, os.path.join(d, wp("2-graph", name, "commit")))

        # 3 - crt
        canvas = ground(t, W * 0.5, H * 0.40, W * 0.80, 1.7)
        canvas = layer(canvas, radial(W * 0.5, H * 0.42, W * 0.30, 2.4), ink,
                       0.05 * t["art"])
        canvas = canvas * scanlines(t["scan"]) + grain(t["grain"] * 1.4, 41)
        save(canvas, os.path.join(d, wp("3-crt", name, "commit")))


# Wallpaper basenames are unique per THEME, not just per family, for two
# reasons. Qt caches the background by URL and every theme resolves to the same
# path, so shared basenames let one theme serve another's stale image. And
# omarchy-theme-set picks the background *after* the current one: when the new
# theme has no file matching the old link it falls back to the first, so unique
# names make a theme switch land on the signature wallpaper instead of walking
# one step further into the set each time.
def wp(name, theme, family):
    return f"{name}-{theme[len(family) + 1:]}.webp"


def save(arr, path):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").save(
        path, "WEBP", quality=92, method=6)
    print("  ->", os.path.basename(path), f"{os.path.getsize(path)//1024}K")


if __name__ == "__main__":
    main()
