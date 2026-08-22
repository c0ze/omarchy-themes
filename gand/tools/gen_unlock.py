#!/usr/bin/env python3
"""Plymouth unlock logo: Gand sigil + wordmark, transparent, per theme accent."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
LOGO = os.environ.get(
    "GAND_LOGO",
    os.path.expanduser("~/projects/gand/gand.tr/public/assets/gand-logo-1024.webp"))
W, H = 800, 188

_a = np.asarray(Image.open(LOGO).convert("L"), dtype=np.float64)
paper = np.percentile(_a, 99)
mask = np.clip(np.clip((paper - _a) / paper, 0, 1) * 1.35, 0, 1)
MARK = Image.fromarray((mask * 255).astype(np.uint8))

FONT = "/usr/share/fonts/noto/NotoSerif-Regular.ttf"
for cand in (FONT, "/usr/share/fonts/TTF/NotoSerif-Regular.ttf",
             "/usr/share/fonts/noto/NotoSerif[wdth,wght].ttf"):
    if os.path.exists(cand):
        FONT = cand
        break

ACCENTS = {"gand-dark": "#d49a64", "gand-earth": "#d6a06b", "gand-light": "#7a4f30"}

for name, accent in ACCENTS.items():
    rgb = tuple(int(accent[i:i+2], 16) for i in (1, 3, 5))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    font = ImageFont.truetype(FONT, 92)
    probe = ImageDraw.Draw(img)

    tracking = 18
    text_w = sum(probe.textlength(ch, font=font) for ch in "GAND") + tracking * 3
    gap = 46
    total = H + gap + text_w
    x0 = (W - total) / 2

    m = MARK.resize((H, H), Image.LANCZOS)
    sigil = Image.new("RGBA", (H, H), rgb + (0,))
    sigil.putalpha(m)
    img.alpha_composite(sigil, (int(x0), 0))

    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    x = x0 + H + gap
    for ch in "GAND":
        d.text((x, H // 2), ch, font=font, fill=rgb + (255,), anchor="lm")
        x += d.textlength(ch, font=font) + tracking
    img.alpha_composite(txt)

    d2 = os.path.join(OUT, name)
    os.makedirs(d2, exist_ok=True)
    img.save(os.path.join(d2, "unlock.png"))
    print(name, "unlock.png", img.size)
