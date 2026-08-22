#!/usr/bin/env python3
"""Build the clean, high-contrast Gand sigil used for all ASCII transcoding.

The gand.tr logo's gold linework is too low-contrast to dither cleanly at
terminal resolutions -- every direct transcode comes out as speckle. So this
lifts only the solid serif G out of the artwork and redraws the celestial ring,
tick marks, pole nodes, crown star and base finial as vectors around it.

    ./gen_sigil.py out.png [--logo path/to/gand-logo-1024.webp]

Requires ImageMagick (`magick`) for the connected-component extraction.
"""
import argparse, math, os, subprocess, sys, tempfile

from PIL import Image, ImageDraw

DEFAULT_LOGO = os.path.expanduser(
    "~/projects/gand/gand.tr/public/assets/gand-logo-1024.webp")

# Connected-component bounding box of the serif G inside the 1024px logo.
G_BOX = (450, 450, 291, 305)   # w, h, x, y
N = 1200                       # sigil canvas, px
C = N / 2


def extract_g(logo):
    """Return a mask image: white where the serif G is, black elsewhere.

    Thresholding alone keeps the glyph's engraved texture, which dithers into
    noise, so isolate the G as a connected component and morphologically close
    the etch specks out of it.
    """
    w, h, x, y = G_BOX
    out = os.path.join(tempfile.mkdtemp(prefix="gand-sigil-"), "g.png")
    subprocess.run([
        "magick", logo, "-colorspace", "Gray", "-threshold", "47%", "-negate",
        "-define", "connected-components:area-threshold=20000",
        "-define", "connected-components:mean-color=true",
        "-connected-components", "8",
        "-morphology", "Close", "Disk:4",
        "-morphology", "Open", "Disk:1",
        "-crop", f"{w}x{h}+{x}+{y}", "+repage", out,
    ], check=True)
    return Image.open(out).convert("L")


def build(g_mask):
    gs = int(N * 0.47)
    g_mask = g_mask.resize((gs, gs), Image.LANCZOS)
    g_mask = g_mask.point(lambda v: 255 if v > 128 else 0)

    canvas = Image.new("L", (N, N), 255)
    d = ImageDraw.Draw(canvas)

    def ring(r, width):
        d.ellipse([C - r, C - r, C + r, C + r], outline=0, width=width)

    def at(angle_deg, r):
        a = math.radians(angle_deg)
        return C + r * math.cos(a), C + r * math.sin(a)

    R = N * 0.44
    ring(R, 7)              # outer ring
    ring(R * 0.90, 3)       # inner hairline

    for i in range(48):     # tick marks around the inner ring
        a = i * 360 / 48
        x0, y0 = at(a, R * 0.90)
        x1, y1 = at(a, R * 0.90 - (14 if i % 4 == 0 else 7))
        d.line([x0, y0, x1, y1], fill=0, width=3)

    # Nodes at the horizontal poles. The logo has crescents here, but a
    # crescent is two cells wide in the terminal and reads as a smudge.
    for a in (0, 180):
        cx, cy = at(a, R)
        cr = N * 0.026
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=0)

    sx, sy = at(-90, R)     # four-point star at the crown
    sr, sw = N * 0.062, N * 0.013
    d.polygon([(sx, sy - sr), (sx + sw, sy), (sx, sy + sr), (sx - sw, sy)], fill=0)
    d.polygon([(sx - sr, sy), (sx, sy - sw), (sx + sr, sy), (sx, sy + sw)], fill=0)

    bx, by = at(90, R)      # diamond finial at the base
    br = N * 0.036
    d.polygon([(bx, by - br), (bx + br * 0.62, by), (bx, by + br), (bx - br * 0.62, by)],
              outline=0, width=5)

    canvas.paste(Image.new("L", (gs, gs), 0),
                 (int(C - gs / 2), int(C - gs / 2 + N * 0.012)), g_mask)
    return canvas


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("output")
    p.add_argument("--logo", default=DEFAULT_LOGO)
    args = p.parse_args()

    if not os.path.exists(args.logo):
        sys.exit(f"logo not found: {args.logo}")

    build(extract_g(args.logo)).save(args.output)
    print("wrote", args.output)


if __name__ == "__main__":
    main()
