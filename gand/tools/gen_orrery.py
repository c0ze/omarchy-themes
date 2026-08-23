#!/usr/bin/env python3
"""Generate Gand's orrery plates: concentric celestial rings for the backdrop.

The Gand mark is an astronomical device -- a serif G inside a ticked ring, with
laurel, crescents, an eight-point crown star and dotted orbits. Drifting fog
would be the wrong register for it; rings that turn are the right one. Each ring
ships as its own plate so the shell can spin them at different rates and in
opposing directions.

Plates carry their colour in RGB and their shape in alpha, so only the linework
draws -- an opaque plate would veil the wallpaper. Light themes get a dark ink
for the same reason Pagan's mist does: pale linework on pale ground is invisible.

    ./gen_orrery.py themes/
"""
import json, math, os, sys

from PIL import Image, ImageDraw

N = 2048                     # plate side, square: these rotate about the centre
C = N / 2
SS = 2                       # supersample factor for clean curves

# Ink per theme. Dark and earth take the bronze accent; light takes the burnt
# umber the site uses as its own light-mode accent.
INK = {
    "gand-dark": "#D49A64",
    "gand-earth": "#D6A06B",
    "gand-light": "#7A4F30",
}
INTENSITY = {"gand-dark": 0.22, "gand-earth": 0.20, "gand-light": 0.24}


def canvas():
    img = Image.new("L", (N * SS, N * SS), 0)
    return img, ImageDraw.Draw(img)


def at(d, angle_deg, r):
    a = math.radians(angle_deg)
    return C * SS + r * math.cos(a) * SS, C * SS + r * math.sin(a) * SS


def ring(d, r, width):
    r *= SS
    d.ellipse([C * SS - r, C * SS - r, C * SS + r, C * SS + r],
              outline=255, width=int(width * SS))


def finish(img):
    return img.resize((N, N), Image.LANCZOS)


def plate_outer():
    """The ticked ring, closest to the one the mark itself sits in."""
    img, d = canvas()
    r = N * 0.455
    ring(d, r, 3)
    for i in range(72):
        a = i * 5
        long_tick = (i % 6 == 0)
        x0, y0 = at(d, a, r)
        x1, y1 = at(d, a, r - (N * 0.022 if long_tick else N * 0.011))
        d.line([x0, y0, x1, y1], fill=255, width=int((3 if long_tick else 2) * SS))
    return finish(img)


def plate_mid():
    """A dotted orbit carrying eight four-point stars."""
    img, d = canvas()
    r = N * 0.355
    for i in range(160):
        a = i * (360 / 160)
        x, y = at(d, a, r)
        dot = 2.2 * SS
        d.ellipse([x - dot, y - dot, x + dot, y + dot], fill=255)
    for i in range(8):
        a = i * 45 + 22.5
        x, y = at(d, a, r)
        sr, sw = N * 0.020 * SS, N * 0.0045 * SS
        d.polygon([(x, y - sr), (x + sw, y), (x, y + sr), (x - sw, y)], fill=255)
        d.polygon([(x - sr, y), (x, y - sw), (x + sr, y), (x, y + sw)], fill=255)
    return finish(img)


def plate_inner():
    """A hairline ring with crescents at the poles, turning the other way."""
    img, d = canvas()
    r = N * 0.255
    ring(d, r, 2)
    for a in (0, 180):
        cx, cy = at(d, a, r)
        cr = N * 0.030 * SS
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], outline=255, width=int(3 * SS))
        ox = cr * 0.5 * (1 if a == 0 else -1)
        d.ellipse([cx - cr + ox, cy - cr, cx + cr + ox, cy + cr], fill=0, outline=0)
    for a in (90, 270):
        cx, cy = at(d, a, r)
        dr = N * 0.012 * SS
        d.ellipse([cx - dr, cy - dr, cx + dr, cy + dr], fill=255)
    return finish(img)


PLATES = (("1-outer", plate_outer), ("2-mid", plate_mid), ("3-inner", plate_inner))


def main():
    out_root = sys.argv[1]
    built = {name: fn() for name, fn in PLATES}

    for theme, ink in INK.items():
        d = os.path.join(out_root, theme, "backdrop")
        os.makedirs(d, exist_ok=True)
        rgb = tuple(int(ink[i:i + 2], 16) for i in (1, 3, 5))
        for name, shape in built.items():
            plate = Image.new("RGBA", (N, N), rgb + (0,))
            plate.putalpha(shape)
            plate.save(os.path.join(d, name + ".png"))
        with open(os.path.join(d, "backdrop.json"), "w") as f:
            json.dump({"profile": "orrery", "intensity": INTENSITY[theme],
                       "speed": 1.0}, f, indent=2)
            f.write("\n")
        print(f"  -> {theme}/backdrop (orrery, intensity {INTENSITY[theme]})")


if __name__ == "__main__":
    main()
