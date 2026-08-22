#!/usr/bin/env python3
"""Generate Gand theme wallpapers from the gand.tr logo mark."""
import math, os, sys
import numpy as np
from PIL import Image, ImageFilter

W, H = 3840, 2160
LOGO = os.environ.get(
    "GAND_LOGO",
    os.path.expanduser("~/projects/gand/gand.tr/public/assets/gand-logo-1024.webp"))
OUT = sys.argv[1]

def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], dtype=np.float64)

# --- logo -> ink mask (1.0 = ink, 0.0 = paper) ---------------------------------
_logo = Image.open(LOGO).convert("L")
_a = np.asarray(_logo, dtype=np.float64)
_paper = np.percentile(_a, 99)
MASK = np.clip((_paper - _a) / _paper, 0.0, 1.0)
# The logo's paper is not perfectly flat. Its residue was invisible while the
# mark was composited at a fixed low alpha, but alpha_for_contrast pushes the
# light themes past 0.5 and the residue then shows as a rectangle around the
# artwork -- so floor it before lifting the linework.
MASK = np.clip((MASK - 0.10) / 0.90, 0.0, 1.0)
MASK = np.clip(MASK * 1.35, 0.0, 1.0)          # lift the faint gold linework
MASK_IMG = Image.fromarray((MASK * 255).astype(np.uint8))

def mask_scaled(size, box=None):
    m = MASK_IMG
    if box:
        m = m.crop(box)
    return np.asarray(m.resize(size, Image.LANCZOS), dtype=np.float64) / 255.0

def annulus(size, inner, feather):
    """Mask that hides the centre of a square patch, keeping the outer ring."""
    y, x = np.mgrid[0:size, 0:size]
    r = np.sqrt((x - size / 2) ** 2 + (y - size / 2) ** 2) / (size / 2)
    return np.clip((r - inner) / max(feather - inner, 1e-6), 0.0, 1.0)

def radial(cx, cy, radius, power=1.0):
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - cx) / radius) ** 2 + ((y - cy) / radius) ** 2)
    return np.clip(1.0 - d, 0.0, 1.0) ** power

def grain(amount, seed):
    rng = np.random.default_rng(seed)
    n = rng.normal(0.0, amount, (H // 2, W // 2))
    n = np.asarray(Image.fromarray(n.astype(np.float32), mode="F").resize((W, H), Image.BILINEAR))
    return n[..., None]

def _lum(v):
    x = v / 255.0
    return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4


def alpha_for_contrast(canvas, cov, colour, target):
    """Alpha that lands a mark at `target` contrast against the ground it covers.

    The same alpha reads very differently on light and dark grounds: lifting a
    near-black ground moves the luminance ratio a long way, darkening a
    near-white one barely moves it at all. Solving for the ratio keeps the light
    themes' marks as present as the dark ones' instead of washing them out.
    """
    here = cov > 0.5
    if not here.any():
        return 0.5
    ground = float(np.median(canvas[here].reshape(-1, 3) @ [0.2126, 0.7152, 0.0722]))
    ink = float(colour @ [0.2126, 0.7152, 0.0722])

    lo, hi = 0.0, 1.0
    for _ in range(40):
        a = (lo + hi) / 2
        mix = ground * (1 - a) + ink * a
        lg, lm = _lum(ground), _lum(mix)
        ratio = (max(lg, lm) + 0.05) / (min(lg, lm) + 0.05)
        if ratio < target:
            lo = a
        else:
            hi = a
    return (lo + hi) / 2


def over(base, tint, alpha):
    """alpha: HxW float; tint: rgb"""
    return base * (1.0 - alpha[..., None]) + tint * alpha[..., None]

def place(alpha_small, size, cx, cy):
    """Drop a HxW-sized alpha patch onto a full-canvas alpha plane."""
    plane = np.zeros((H, W), dtype=np.float64)
    w, h = size
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    sx0, sy0 = max(0, -x0), max(0, -y0)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W, x0 + w - sx0), min(H, y0 + h - sy0)
    plane[y0:y1, x0:x1] = alpha_small[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
    return plane

def save(arr, path):
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    img.save(path, "WEBP", quality=92, method=6)
    print("  ->", os.path.relpath(path, OUT), f"{os.path.getsize(path)//1024}K")

# ------------------------------------------------------------------------------
THEMES = {
    "gand-dark": dict(
        glow="#1b1b20", edge="#050506", base="#0c0c0e",
        ink="#d49a64", ink2="#84b09c", stone="#5e6d78",
        sigil=2.6, ring=1.9, grain=2.6,   # contrast targets, not alphas
    ),
    "gand-earth": dict(
        glow="#544a39", edge="#221d17", base="#3a332a",
        ink="#d6a06b", ink2="#8eb0a0", stone="#8593a0",
        sigil=2.6, ring=1.9, grain=3.0,
    ),
    "gand-light": dict(
        glow="#faf7f0", edge="#d8d0c0", base="#f0ebe1",
        ink="#7a4f30", ink2="#3d6052", stone="#6f7780",
        sigil=2.6, ring=1.9, grain=2.2,
    ),
}

for name, t in THEMES.items():
    d = os.path.join(OUT, name, "backgrounds")
    os.makedirs(d, exist_ok=True)
    glow, edge, base = hexrgb(t["glow"]), hexrgb(t["edge"]), hexrgb(t["base"])
    ink, ink2, stone = hexrgb(t["ink"]), hexrgb(t["ink2"]), hexrgb(t["stone"])
    print(name)

    # 1 - sigil: the full mark, centred, over a firelight glow
    g = radial(W * 0.5, H * 0.46, W * 0.72, 1.35)
    canvas = edge + (glow - edge) * g[..., None]
    canvas = over(canvas, base, np.full((H, W), 0.25))
    s = int(H * 0.86)
    cov = place(mask_scaled((s, s)), (s, s), W * 0.5, H * 0.47)
    canvas = over(canvas, ink, cov * alpha_for_contrast(canvas, cov, ink, t["sigil"]))
    canvas += grain(t["grain"], 11)
    save(canvas, os.path.join(d, "1-sigil.webp"))

    # 2 - ring: the celestial ring alone (centre punched out), bleeding off-canvas
    g = radial(W * 0.28, H * 0.72, W * 1.0, 1.15)
    canvas = edge + (glow - edge) * g[..., None]
    canvas = over(canvas, base, np.full((H, W), 0.35))
    s = int(H * 1.75)
    ring = mask_scaled((s, s)) * annulus(s, 0.56, 0.63)
    cov = place(ring, (s, s), W * 0.80, H * 0.30)
    canvas = over(canvas, ink, cov * alpha_for_contrast(canvas, cov, ink, t["ring"]))
    s2 = int(H * 1.05)
    ring2 = mask_scaled((s2, s2)) * annulus(s2, 0.56, 0.65)
    cov2 = place(ring2, (s2, s2), W * 0.13, H * 0.95)
    canvas = over(canvas, stone, cov2 * alpha_for_contrast(canvas, cov2, stone, t["ring"] * 0.9))
    canvas += grain(t["grain"], 23)
    save(canvas, os.path.join(d, "2-ring.webp"))

    # 3 - vellum: quiet texture only, no mark
    g = radial(W * 0.5, H * 0.38, W * 0.85, 1.6)
    canvas = edge + (glow - edge) * g[..., None]
    canvas = over(canvas, base, np.full((H, W), 0.45))
    y = np.linspace(0.0, 1.0, H)[:, None, None]
    canvas = canvas * (1.0 - 0.06 * y) + edge * (0.06 * y)
    canvas += grain(t["grain"] * 1.5, 37)
    save(canvas, os.path.join(d, "3-vellum.webp"))
