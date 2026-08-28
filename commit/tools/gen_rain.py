#!/usr/bin/env python3
"""Generate Commit's glyph-rain plates: the waterfall behind the pulse cursor.

Three plates per theme, scrolled downward by the shell at three different
rates. Columns are partitioned between the plates -- column 0 is on plate a,
column 1 on plate b, column 2 on plate c -- so no column is drawn twice and
neighbouring columns fall at different speeds, which is what makes rain read
as rain rather than as a sliding texture.

Each plate tiles seamlessly end to end. A column's brightness is a function of
`(row - phase) mod period`, and every period divides ROWS, so the pattern that
leaves the bottom of the plate is the one arriving at the top.

The glyphs are half-width katakana, mirrored as the film's are, salted with
digits that are not -- a mirrored numeral just reads as a broken glyph. They do
not re-roll while falling: the plate is a static image the shell translates, so
the flicker of the original is traded for a backdrop that costs one texture and
no per-frame work.

    ./gen_rain.py themes/
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 3840, 2160
CELL_W, CELL_H = 40, 54          # 2160 / 54 = 40 rows exactly, so the plate tiles
COLS, ROWS = W // CELL_W, H // CELL_H

FONT = ("/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc", 5)   # Sans Mono CJK JP
KATAKANA = [chr(c) for c in range(0xFF66, 0xFF9E)]
DIGITS = list("0123456789")

# Drop lengths, in rows. Every one divides ROWS or the plate would not tile.
PERIODS = (10, 20, 20, 40, 40)
TAIL = 10.0                      # e-folding rows of the trail behind a head
PLATES = ("a", "b", "c")
COLUMN_DENSITY = 0.62            # fraction of columns that carry a drop at all

# head is the leading glyph, body the trail. On the light theme the CRT ground
# becomes the ink, exactly as the cursor plate does -- pale rain on pale paper
# would not be there at all. head sits only a little above body: further apart
# and the trails stop reading as trails and the field becomes loose confetti.
#
# These alphas carry the whole dimming. backdrop.json's intensity is a group
# opacity over every layer, so the value that used to hold the rain back was
# also holding the cursor back; it is 1.0 now and the per-theme dimming it used
# to apply (0.55 / 0.50 / 0.45) is folded in here.
INK = {
    "commit-late-night": {"head": "#F1F1F0", "body": "#5AF78E", "body_a": 0.48, "head_a": 0.52},
    "commit-evening":    {"head": "#FFF4E0", "body": "#FFB454", "body_a": 0.41, "head_a": 0.46},
    "commit-morning":    {"head": "#0B0F14", "body": "#00793B", "body_a": 0.38, "head_a": 0.41},
}

SEED = 0xC0DE


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def glyph_masks():
    """Every glyph pre-rendered once, cell-sized; katakana mirrored."""
    font = ImageFont.truetype(FONT[0], int(CELL_H * 0.74), index=FONT[1])
    out = []
    for g in KATAKANA + DIGITS:
        im = Image.new("L", (CELL_W, CELL_H), 0)
        d = ImageDraw.Draw(im)
        box = d.textbbox((0, 0), g, font=font)
        d.text(((CELL_W - (box[2] - box[0])) / 2 - box[0],
                (CELL_H - (box[3] - box[1])) / 2 - box[1]), g, font=font, fill=255)
        out.append(im.transpose(Image.FLIP_LEFT_RIGHT) if g in KATAKANA else im)
    return out


def columns(rng):
    """Assign each column a plate, a drop length and a starting phase."""
    out = []
    for c in range(COLS):
        if rng.random() > COLUMN_DENSITY:
            continue
        out.append({
            "col": c,
            "plate": c % len(PLATES),
            "period": rng.choice(PERIODS),
            "phase": rng.randrange(ROWS),
            # A little per-column dimming, so the field has depth.
            "gain": rng.uniform(0.72, 1.0),
        })
    return out


def build(plate_index, cols, masks, rng):
    """Two coverage maps for one plate: the trails, and the leading glyphs."""
    body = Image.new("L", (W, H), 0)
    head = Image.new("L", (W, H), 0)
    for spec in cols:
        if spec["plate"] != plate_index:
            continue
        x = spec["col"] * CELL_W
        for row in range(ROWS):
            step = (row - spec["phase"]) % spec["period"]
            if step == 0:
                a = 1.0
            else:
                a = math.exp(-step / TAIL)
                if a < 0.04:
                    continue
            a *= spec["gain"]
            mask = masks[rng.randrange(len(masks))]
            target = head if step == 0 else body
            cell = mask.point(lambda v, a=a: int(v * a))
            box = (x, row * CELL_H)
            target.paste(cell, box, cell)
    return body, head


def main():
    out_root = sys.argv[1]
    masks = glyph_masks()

    for theme, ink in INK.items():
        # Same seed per theme: the three variants are the same rain in three
        # inks, so a theme switch does not reshuffle the field.
        rng = random.Random(SEED)
        cols = columns(rng)
        d = os.path.join(out_root, theme, "backdrop")
        os.makedirs(d, exist_ok=True)
        for i, tag in enumerate(PLATES):
            body, head = build(i, cols, masks, rng)
            plate = Image.new("RGBA", (W, H), rgb(ink["body"]) + (0,))
            plate.putalpha(body.point(lambda v: int(v * ink["body_a"])))
            crown = Image.new("RGBA", (W, H), rgb(ink["head"]) + (0,))
            crown.putalpha(head.point(lambda v: int(v * ink["head_a"])))
            plate = Image.alpha_composite(plate, crown)
            plate.save(os.path.join(d, f"{i + 2}-rain-{tag}.png"))
        print(f"  -> {theme}/backdrop ({len(PLATES)} rain plates, "
              f"{len(cols)}/{COLS} columns)")


if __name__ == "__main__":
    main()
