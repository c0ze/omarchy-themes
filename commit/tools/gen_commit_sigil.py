#!/usr/bin/env python3
"""Redraw the Commit!!! marks as clean, high-contrast art for ASCII transcoding.

The shipped icon (commit/game/theme/icon.png) is a 256px pixel-art mark: a green
commit node on a branch graph with an amber "!" punched through it. Upscaling
pixel art dithers into mush at terminal resolution, so redraw it as vectors.

    ./gen_commit_sigil.py mark out.png     # the icon alone, wide
    ./gen_commit_sigil.py graph out.png    # the icon inside a commit graph

The graph form fills a square-ish canvas, which is what the About logo's 54x26
cell budget wants; the mark alone is only ~13 rows tall.
"""
import argparse

from PIL import Image, ImageDraw

N = 1200
C = N / 2


def _node(d, cx, cy, r, width=None):
    box = [cx - r, cy - r, cx + r, cy + r]
    if width:
        d.ellipse(box, outline=0, width=width)
    else:
        d.ellipse(box, fill=0)


def mark(scale=1.0, canvas=None, cx=0.5, cy=0.5):
    """The app icon: node + '!' + the two branch stubs."""
    img = canvas or Image.new("L", (N, N), 255)
    d = ImageDraw.Draw(img)
    s = N * scale
    ox, oy = cx * N - s / 2, cy * N - s / 2
    stroke = max(2, int(s * 0.052))

    def line(points):
        d.line([(ox + x * s, oy + y * s) for x, y in points],
               fill=0, width=stroke, joint="curve")

    line([(0.05, 0.325), (0.135, 0.325), (0.235, 0.425), (0.315, 0.425)])
    line([(0.685, 0.545), (0.95, 0.545)])

    mx, my = ox + s / 2, oy + s / 2
    _node(d, mx, my, s * 0.215, width=stroke)

    bw = s * 0.052
    d.rounded_rectangle([mx - bw, my - s * 0.150, mx + bw, my + s * 0.028],
                        radius=bw * 0.5, fill=0)
    dr = s * 0.049
    d.ellipse([mx - dr, my + s * 0.082 - dr, mx + dr, my + s * 0.082 + dr], fill=0)
    return img


def graph():
    """The mark seated in a branch-and-merge commit graph."""
    img = Image.new("L", (N, N), 255)
    d = ImageDraw.Draw(img)
    stroke = int(N * 0.026)
    trunk_x = 0.22
    r = N * 0.030

    def line(points):
        d.line([(x * N, y * N) for x, y in points], fill=0, width=stroke,
               joint="curve")

    # Trunk, top to bottom.
    line([(trunk_x, 0.06), (trunk_x, 0.94)])
    for y in (0.06, 0.25, 0.75, 0.94):
        _node(d, trunk_x * N, y * N, r)

    # A branch that leaves the trunk, carries two commits, and merges back.
    lane = 0.38
    line([(trunk_x, 0.25), (lane, 0.34)])
    line([(lane, 0.34), (lane, 0.66)])
    line([(lane, 0.66), (trunk_x, 0.75)])
    for y in (0.43, 0.57):
        _node(d, lane * N, y * N, r)

    # The icon itself, hung off the branch lane.
    mark(scale=0.68, canvas=img, cx=0.685, cy=0.50)
    return img


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("form", choices=("mark", "graph"))
    p.add_argument("output")
    args = p.parse_args()
    (mark() if args.form == "mark" else graph()).save(args.output)
    print("wrote", args.output)


if __name__ == "__main__":
    main()
