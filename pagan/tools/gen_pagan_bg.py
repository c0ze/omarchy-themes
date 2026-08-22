#!/usr/bin/env python3
"""Generate Pagan theme wallpapers.

Atmosphere comes from the band site's own fog plates (src/assets/fog1.png,
fog2.png) rather than synthesised noise, so the desktop and pagan.tr share the
same mist. Three per theme:

  1-sigil      the band logo in the fog
  2-fog        fog alone
  3-pentagram  the pentagram out of the logo, drawn large and faint

    ./gen_pagan_bg.py themes/
"""
import json, math, os, sys

import numpy as np
from PIL import Image, ImageDraw

W, H = 3840, 2160
SITE = os.environ.get(
    "PAGAN_SITE", os.path.expanduser("~/projects/music/pagan/pagan.tr"))
LOGO = os.path.join(SITE, "src/assets/pagan-logo.jpg")
FOG = [os.path.join(SITE, "src/assets", f) for f in ("fog1.png", "fog2.png")]


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def fog(offset=0.0, flip=False):
    """The site's fog plates, upscaled and layered into one coverage map."""
    out = np.zeros((H, W), dtype=np.float64)
    for i, path in enumerate(FOG):
        im = Image.open(path).convert("L")
        if flip and i:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        im = im.resize((int(W * 1.4), int(H * 1.4)), Image.BICUBIC)
        dx = int((im.width - W) * ((offset + 0.35 * i) % 1.0))
        dy = int((im.height - H) * ((offset * 0.6 + 0.5 * i) % 1.0))
        out += np.asarray(im.crop((dx, dy, dx + W, dy + H)), dtype=np.float64) / 255.0
    return np.clip(out / len(FOG) * 1.6, 0.0, 1.0)


def radial(cx, cy, radius, power=1.0):
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - cx) / radius) ** 2 + ((y - cy) / radius) ** 2)
    return np.clip(1.0 - d, 0.0, 1.0) ** power


def logo_mask():
    """Alpha of the logo PNG (it is an RGBA file despite the .jpg name)."""
    im = Image.open(LOGO)
    a = im.split()[-1] if im.mode in ("RGBA", "LA") else im.convert("L")
    return a


def place(mask, height_frac, cx, cy):
    """Scale a mask to a fraction of canvas height and drop it on a full plane."""
    h = int(H * height_frac)
    w = max(1, int(mask.width * h / mask.height))
    small = np.asarray(mask.resize((w, h), Image.LANCZOS), dtype=np.float64) / 255.0
    plane = np.zeros((H, W), dtype=np.float64)
    x0, y0 = int(cx * W - w / 2), int(cy * H - h / 2)
    sx, sy = max(0, -x0), max(0, -y0)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W, x0 + w - sx), min(H, y0 + h - sy)
    if x1 > x0 and y1 > y0:
        plane[y0:y1, x0:x1] = small[sy:sy + (y1 - y0), sx:sx + (x1 - x0)]
    return plane


def pentagram():
    """The inverted pentagram in a circle, the element at the logo's centre."""
    s = 4
    img = Image.new("L", (W // s, H // s), 0)
    d = ImageDraw.Draw(img)
    cx, cy = (W // s) / 2, (H // s) / 2
    r = (H // s) * 0.40
    stroke = max(1, int((H // s) * 0.008))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=255, width=stroke)
    # Point-down: start at the bottom vertex and step by two around the circle.
    pts = [(cx + r * math.cos(math.radians(90 + i * 72)),
            cy + r * math.sin(math.radians(90 + i * 72))) for i in range(5)]
    order = [pts[(i * 2) % 5] for i in range(6)]
    d.line(order, fill=255, width=stroke, joint="curve")
    return np.asarray(img.resize((W, H), Image.LANCZOS), dtype=np.float64) / 255.0


def grain(amount, seed):
    rng = np.random.default_rng(seed)
    n = rng.normal(0.0, amount, (H // 2, W // 2)).astype(np.float32)
    return np.asarray(Image.fromarray(n, mode="F").resize((W, H), Image.BILINEAR))[..., None]


def _lum(v):
    x = v / 255.0
    return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4


def alpha_for_contrast(canvas, cov, colour, target):
    """Alpha that lands a mark at `target` contrast against the ground it covers.

    The same alpha reads very differently on light and dark grounds: lifting a
    near-black ground moves the luminance ratio a long way, darkening a
    near-white one barely moves it at all. So solve for the ratio instead of
    hand-picking an alpha per theme, and the light themes stop washing out.
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


def over(base, cov, colour, alpha):
    a = (cov * alpha)[..., None]
    return base * (1.0 - a) + colour * a


THEMES = {
    "pagan-dark": dict(
        bg="#0A0A0A", mist="#9FB6C4", ink="#F2F2F2", accent="#25AFF4",
        # sigil/penta are target contrast ratios, not alphas
        fog_alpha=0.22, sigil=3.4, penta=1.9, grain=2.2),
    "pagan-light": dict(
        bg="#FFFFFF", mist="#5E6B76", ink="#141414", accent="#262626",
        fog_alpha=0.34, sigil=3.4, penta=1.9, grain=1.6),
}


def save(arr, path):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").save(
        path, "WEBP", quality=92, method=6)
    print("  ->", os.path.basename(path), f"{os.path.getsize(path)//1024}K")


# Fog plates for the animated background (see the shell plugin under shell/).
# The site's plates are opaque black-and-white, which works there because they
# sit on a black hero. Composited over a wallpaper they would veil the whole
# frame -- and on the light theme that would wash the logo back out -- so give
# them an alpha channel taken from their own luminance and colour the fog
# itself. That is the same idea as the site's `filter: invert(1)` for light
# mode, done in the plate rather than at draw time.
FOG_INK = {"pagan-dark": "#DCE8F0", "pagan-light": "#39424C"}


def write_fog_plates(out_root):
    for name, ink in FOG_INK.items():
        d = os.path.join(out_root, name, "fog")
        os.makedirs(d, exist_ok=True)
        for src in FOG:
            plate = Image.open(src).convert("L")
            rgba = Image.new("RGBA", plate.size, tuple(int(ink[i:i + 2], 16)
                                                       for i in (1, 3, 5)) + (0,))
            rgba.putalpha(plate)
            rgba.save(os.path.join(d, os.path.basename(src)))
        profile = "fog" if name.endswith("dark") else "mist"
        intensity = 0.55 if name.endswith("dark") else 0.50
        with open(os.path.join(d, "fog.json"), "w") as f:
            json.dump({"profile": profile, "intensity": intensity}, f, indent=2)
            f.write("\n")
        print(f"  -> {name}/fog ({profile})")


def main():
    out_root = sys.argv[1]
    mask = logo_mask()
    penta = pentagram()
    write_fog_plates(out_root)

    for name, t in THEMES.items():
        d = os.path.join(out_root, name, "backgrounds")
        os.makedirs(d, exist_ok=True)
        bg, mist = hexrgb(t["bg"]), hexrgb(t["mist"])
        ink, accent = hexrgb(t["ink"]), hexrgb(t["accent"])
        print(name)

        def base(offset, flip=False, vignette=1.6):
            canvas = np.repeat(np.repeat(bg[None, None, :], H, 0), W, 1)
            canvas = over(canvas, fog(offset, flip), mist, t["fog_alpha"])
            # Draw the frame back down into the ground so the mist sits inside it.
            v = 1.0 - radial(W * 0.5, H * 0.45, W * 0.78, vignette)
            return canvas * (1.0 - 0.55 * v[..., None]) + bg * (0.55 * v[..., None])

        canvas = base(0.10)
        cov = place(mask, 0.46, 0.5, 0.46)
        canvas = over(canvas, cov, ink, alpha_for_contrast(canvas, cov, ink, t["sigil"]))
        canvas += grain(t["grain"], 5)
        save(canvas, os.path.join(d, "1-sigil.webp"))

        canvas = base(0.62, flip=True, vignette=1.2)
        canvas = over(canvas, radial(W * 0.5, H * 0.40, W * 0.34, 2.6), accent, 0.05)
        canvas += grain(t["grain"], 19)
        save(canvas, os.path.join(d, "2-fog.webp"))

        canvas = base(0.31)
        canvas = over(canvas, penta, ink, alpha_for_contrast(canvas, penta, ink, t["penta"]))
        canvas += grain(t["grain"], 43)
        save(canvas, os.path.join(d, "3-pentagram.webp"))


if __name__ == "__main__":
    main()
