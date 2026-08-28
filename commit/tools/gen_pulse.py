#!/usr/bin/env python3
"""Generate Commit's pulse-cursor plate: the stop cursor, for the backdrop.

The Commit Pulse is the game's core interaction -- pulse_screen.gd opens with
"a cursor ping-pongs across a colored bar and the player times a stop". So the
backdrop for these themes is that cursor, sweeping and reversing.

The plate holds ONLY the cursor, at the bar's left edge, on a canvas with the
same 16:9 geometry the wallpapers use. The shell renders it exactly as the
wallpaper is rendered and translates it by the bar's width, so on 1-pulse the
cursor tracks the real bar it was drawn against. No bar frame is included: on
2-graph and 3-crt there is no bar, and a lone scanning line suits a CRT ground
better than an imported frame would -- and it keeps 3-crt quiet.

    ./gen_pulse.py themes/
"""
import json, os, sys

from PIL import Image, ImageDraw, ImageFilter

W, H = 3840, 2160

# Geometry copied from gen_commit_bg.py's pulse_bar()/pulse_zones(): the plate
# has to line up with the bar those bake into 1-pulse.
BAR_W, BAR_H = 0.66, 0.075
BAR_X, BAR_Y = (1 - BAR_W) / 2, 0.46
OVERHANG = 0.022

# The game's cursor is WHITE (palette.gd). On the light theme white on a pale
# ground is invisible, so it takes the CRT ground colour as ink instead.
INK = {
    "commit-late-night": "#F1F1F0",
    "commit-evening": "#FFF4E0",
    "commit-morning": "#0B0F14",
}
# 1.0, because intensity is a group opacity over every layer in the backdrop
# and the cursor is meant to be solid -- the game draws a hard white line, not a
# ghost of one. The rain carries its own dimming in the plate alphas instead
# (gen_rain.py), so lowering this still fades the whole backdrop as before.
INTENSITY = {"commit-late-night": 1.0, "commit-evening": 1.0, "commit-morning": 1.0}

# Seconds for a full there-and-back. The game's cursor is frantic by design;
# a backdrop that frantic would be unusable, so this is a slow scan. Tunable
# live via backdrop.json's speed.
SWEEP_MS = 18000


def cursor_plate():
    """A hard cursor line with a soft glow, at the bar's left edge."""
    line = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(line)

    x = BAR_X * W
    y0 = (BAR_Y - OVERHANG) * H
    y1 = (BAR_Y + BAR_H + OVERHANG) * H
    half = max(2, int(W * 0.0016))
    d.rectangle([x - half, y0, x + half, y1], fill=255)

    # A wider, softer copy underneath reads as the cursor's own glow, the way
    # the bar lights up around it in game.
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gd.rectangle([x - half * 6, y0 - H * 0.012, x + half * 6, y1 + H * 0.012], fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=W * 0.006))

    out = Image.new("L", (W, H), 0)
    out.paste(glow)
    out.paste(line, mask=line)
    return out


def main():
    out_root = sys.argv[1]
    shape = cursor_plate()

    for theme, ink in INK.items():
        d = os.path.join(out_root, theme, "backdrop")
        os.makedirs(d, exist_ok=True)
        rgb = tuple(int(ink[i:i + 2], 16) for i in (1, 3, 5))
        plate = Image.new("RGBA", (W, H), rgb + (0,))
        plate.putalpha(shape)
        plate.save(os.path.join(d, "1-cursor.png"))
        with open(os.path.join(d, "backdrop.json"), "w") as f:
            json.dump({"profile": "pulse", "intensity": INTENSITY[theme],
                       "speed": 1.0}, f, indent=2)
            f.write("\n")
        print(f"  -> {theme}/backdrop (pulse, intensity {INTENSITY[theme]})")


if __name__ == "__main__":
    main()
