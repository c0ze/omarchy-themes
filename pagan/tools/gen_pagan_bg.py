#!/usr/bin/env python3
"""Generate Pagan theme wallpapers.

Atmosphere comes from the band site's own fog plates (src/assets/fog1.png,
fog2.png) rather than synthesised noise, so the desktop and pagan.tr share the
same mist. Three per theme:

  1-logo       the band logo in the fog
  2-fog        fog alone
  3-pentagram  the pentagram out of the logo, drawn large and faint

    ./gen_pagan_bg.py themes/                # current logo -> pagan-*
    ./gen_pagan_bg.py themes/ --variant old  # 2019 circular sigil -> pagan-old-*

Both variants share the band site's colour tokens and its fog; only the mark
differs, which is the whole point of the "old" set.
"""
import json, math, os, sys

import numpy as np
from PIL import Image, ImageDraw

W, H = 3840, 2160
SITE = os.environ.get(
    "PAGAN_SITE", os.path.expanduser("~/projects/music/pagan/pagan.tr"))
FOG = [os.path.join(SITE, "src/assets", f) for f in ("fog1.png", "fog2.png")]

# The two marks differ in shape, so each needs its own placement. The current
# logo is wide (1344x768) and sits as a band; the 2019 sigil is square and
# wants to be smaller on screen or it dominates the frame.
VARIANTS = {
    # Basenames get a per-theme suffix appended at save time -- see the note in
    # main(). Unique per theme, not just per family.
    "current": dict(
        logo="pagan-logo.jpg", prefix="pagan",
        mark_h=0.46, names=("1-logo", "2-fog", "3-pentagram"), third_scale=None),
    "old": dict(
        logo="PAGAN-old.logo.png", prefix="pagan-old",
        mark_h=0.64, names=("1-seal", "2-veil", "3-halo"), third_scale=1.45),
}
VARIANT = VARIANTS["current"]
LOGO = os.path.join(SITE, "src/assets", VARIANT["logo"])


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
    "dark": dict(
        bg="#0A0A0A", mist="#9FB6C4", ink="#F2F2F2", accent="#25AFF4",
        # sigil/penta are target contrast ratios, not alphas.
        # Dark deliberately asks for far more than light. An equal ratio is not
        # an equal read: light puts a dark mark at ~105 on a ~200 ground, a wide
        # absolute separation, while dark puts a mid-grey at ~139 on ~62 -- and
        # the fog lifts that ground from 37, halving the separation the mark had
        # before the fog existed. So the dark mark goes near-white instead.
        fog_alpha=0.22, sigil=6.5, penta=2.6, grain=2.2),
    "light": dict(
        bg="#FFFFFF", mist="#5E6B76", ink="#141414", accent="#262626",
        fog_alpha=0.34, sigil=3.4, penta=1.9, grain=1.6),
}


def save(arr, path):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").save(
        path, "WEBP", quality=92, method=6)
    print("  ->", os.path.basename(path), f"{os.path.getsize(path)//1024}K")


# Backdrop plates for the animated background (shell/gand.backdrop).
# The site's plates are opaque black-and-white, which works there because they
# sit on a black hero. Composited over a wallpaper they would veil the whole
# frame -- and on the light theme that would wash the logo back out -- so give
# them an alpha channel taken from their own luminance and colour the fog
# itself. That is the same idea as the site's `filter: invert(1)` for light
# mode, done in the plate rather than at draw time.
FOG_INK = {"dark": "#DCE8F0", "light": "#39424C"}


def write_fog_plates(out_root):
    for suffix, ink in FOG_INK.items():
        name = f"{VARIANT['prefix']}-{suffix}"
        d = os.path.join(out_root, name, "backdrop")
        os.makedirs(d, exist_ok=True)
        for src in FOG:
            plate = Image.open(src).convert("L")
            rgba = Image.new("RGBA", plate.size, tuple(int(ink[i:i + 2], 16)
                                                       for i in (1, 3, 5)) + (0,))
            rgba.putalpha(plate)
            rgba.save(os.path.join(d, os.path.basename(src)))
        profile = "fog" if suffix == "dark" else "mist"
        # Tuned against real captures, not the site's values. pagan.tr's fog
        # sits over a small hero; scaled to a 4K wallpaper the same opacities
        # produce a wall of cloud that swallows the logo entirely (measured:
        # the mark drops from 3.72:1 to 2.28:1 at 0.55). 0.20 keeps the drift
        # while leaving the mark essentially untouched at ~3.4:1.
        intensity = 0.14 if suffix == "dark" else 0.20
        with open(os.path.join(d, "backdrop.json"), "w") as f:
            json.dump({"profile": profile, "intensity": intensity, "speed": 1.0}, f, indent=2)
            f.write("\n")
        print(f"  -> {name}/backdrop ({profile})")


def main():
    global VARIANT, LOGO
    args = sys.argv[1:]
    out_root = args[0]
    if "--variant" in args:
        VARIANT = VARIANTS[args[args.index("--variant") + 1]]
        LOGO = os.path.join(SITE, "src/assets", VARIANT["logo"])
    print(f"variant: {VARIANT['prefix']} ({VARIANT['logo']})")
    mask = logo_mask()
    penta = pentagram()
    write_fog_plates(out_root)

    for suffix, t in THEMES.items():
        name = f"{VARIANT['prefix']}-{suffix}"
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
        cov = place(mask, VARIANT["mark_h"], 0.5, 0.46)
        canvas = over(canvas, cov, ink, alpha_for_contrast(canvas, cov, ink, t["sigil"]))
        canvas += grain(t["grain"], 5)
        save(canvas, os.path.join(d, f'{VARIANT["names"][0]}-{suffix}.webp'))

        canvas = base(0.62, flip=True, vignette=1.2)
        canvas = over(canvas, radial(W * 0.5, H * 0.40, W * 0.34, 2.6), accent, 0.05)
        canvas += grain(t["grain"], 19)
        save(canvas, os.path.join(d, f'{VARIANT["names"][1]}-{suffix}.webp'))

        canvas = base(0.31)
        if VARIANT["third_scale"]:
            # The old mark IS a pentagram, so a drawn one would just repeat it.
            # Oversize the sigil instead until it bleeds off the frame.
            third = place(mask, VARIANT["mark_h"] * VARIANT["third_scale"], 0.5, 0.46)
        else:
            third = penta
        canvas = over(canvas, third, ink, alpha_for_contrast(canvas, third, ink, t["penta"]))
        canvas += grain(t["grain"], 43)
        save(canvas, os.path.join(d, f'{VARIANT["names"][2]}-{suffix}.webp'))


if __name__ == "__main__":
    main()
