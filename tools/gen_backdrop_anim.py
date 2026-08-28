#!/usr/bin/env python3
"""Render a theme's backdrop animation to an animated webp, for READMEs.

Replicates shell/gand.backdrop/Backdrop.qml offline: same profiles, layer
order, opacity stops and motion math, composited over the theme's first
wallpaper at a small 16:9 size. The shell's real periods are minutes (the
orrery) to tens of seconds (fog), so a demo clip time-lapses: SIM_SECONDS of
animation are compressed into the clip, and a short crossfade at the seam
hides the fact that the opacity cycles do not line up on a perfect loop.

    tools/gen_backdrop_anim.py gand/themes/gand-earth
    tools/gen_backdrop_anim.py pagan/themes/pagan-dark --sim 30

Output lands in <theme>/backdrop/animation.webp, which split-theme.sh then
carries into the standalone repo like any other asset.
"""
import argparse
import json
import math
from pathlib import Path

from PIL import Image

# Keep in sync with shell/gand.backdrop/Backdrop.qml `profiles`.
PROFILES = {
    "fog": {
        "kind": "drift",
        "layers": [
            {"plate": 0, "move": 15000, "cycle": 10000, "stops": [0.10, 0.50, 0.28, 0.40, 0.16], "at": [0, 0.22, 0.40, 0.58, 0.80]},
            {"plate": 1, "move": 13000, "cycle": 21000, "stops": [0.50, 0.20, 0.10, 0.30], "at": [0, 0.25, 0.50, 0.80]},
            {"plate": 1, "move": 13000, "cycle": 21000, "stops": [0.80, 0.20, 0.60, 0.30], "at": [0, 0.27, 0.52, 0.68]},
        ],
    },
    "mist": {
        "kind": "drift",
        "layers": [
            {"plate": 0, "move": 20000, "cycle": 12000, "stops": [0.28, 0.56, 0.42, 0.49], "at": [0, 0.25, 0.50, 0.75]},
            {"plate": 1, "move": 25000, "cycle": 18000, "stops": [0.30, 0.24, 0.42], "at": [0, 0.30, 0.60]},
        ],
    },
    "pulse": {
        "kind": "sweep",
        "layers": [
            {"plate": 1, "kind": "rain", "move": 31000, "cycle": 41000, "stops": [0.62, 0.85, 0.70], "at": [0, 0.35, 0.70]},
            {"plate": 2, "kind": "rain", "move": 43000, "cycle": 33000, "stops": [0.85, 0.60, 0.75], "at": [0, 0.30, 0.65]},
            {"plate": 3, "kind": "rain", "move": 57000, "cycle": 47000, "stops": [0.55, 0.80, 0.62], "at": [0, 0.40, 0.75]},
            {"plate": 0, "span": 0.66, "period": 18000, "cycle": 90000, "stops": [1.0], "at": [0]},
        ],
    },
    "orrery": {
        "kind": "spin",
        "layers": [
            {"plate": 0, "period": 420000, "dir": 1, "scale": 1.00, "cycle": 47000, "stops": [0.62, 0.90, 0.70], "at": [0, 0.35, 0.70]},
            {"plate": 1, "period": 300000, "dir": -1, "scale": 1.00, "cycle": 31000, "stops": [0.90, 0.62, 0.80], "at": [0, 0.30, 0.65]},
            {"plate": 2, "period": 540000, "dir": 1, "scale": 1.00, "cycle": 39000, "stops": [0.75, 0.95, 0.68], "at": [0, 0.40, 0.75]},
        ],
    },
}

W, H = 960, 540
FPS = 15
CLIP_SECONDS = 6
SEAM_SECONDS = 0.6


def opacity_at(stops, at, t):
    """Piecewise-linear across the stops, wrapping last segment to first."""
    n = len(stops)
    for i in range(n - 1, -1, -1):
        if t >= at[i]:
            t0, v0 = at[i], stops[i]
            t1 = at[i + 1] if i + 1 < n else 1.0
            v1 = stops[i + 1] if i + 1 < n else stops[0]
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0
            return v0 + (v1 - v0) * f
    return stops[0]


def cover(img, w, h):
    """Image.PreserveAspectCrop."""
    scale = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    x = (img.width - w) // 2
    y = (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def fit(img, side):
    """Image.PreserveAspectFit into a side x side square."""
    scale = side / max(img.width, img.height)
    return img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)


def with_opacity(img, opacity):
    if opacity >= 1.0:
        return img
    out = img.copy()
    out.putalpha(out.getchannel("A").point(lambda a: round(a * opacity)))
    return out


def sine_in_out(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def render_frame(base, prepared, layers, t_ms):
    """One frame at simulated time t_ms. Layers composite onto a shared
    overlay first: the QML applies `intensity` as a group opacity."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for layer, prep in zip(layers, prepared):
        phase = layer["phase"]
        opacity = opacity_at(layer["stops"], layer["at"], (t_ms / layer["cycle"] + phase) % 1)
        if layer["kind"] == "drift":
            x = -W * ((t_ms / layer["move"]) % 1)
            frame_layer = Image.new("RGBA", (W * 2, H), (0, 0, 0, 0))
            frame_layer.paste(prep, (0, 0))
            frame_layer.paste(prep, (W, 0))
            overlay.alpha_composite(with_opacity(frame_layer, opacity).crop((round(-x), 0, round(-x) + W, H)))
        elif layer["kind"] == "rain":
            # The tall stack scrolls upward past the viewport, so the glyphs
            # fall. Cropping at H when the animation starts means the lower
            # copy is on screen first and the seam has already passed.
            y = round(H - H * ((t_ms / layer["move"]) % 1))
            frame_layer = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))
            frame_layer.paste(prep, (0, 0))
            frame_layer.paste(prep, (0, H))
            overlay.alpha_composite(with_opacity(frame_layer, opacity).crop((0, y, W, y + H)))
        elif layer["kind"] == "sweep":
            half = layer["period"] / 2
            tt = (t_ms % layer["period"]) / half
            x = W * layer["span"] * (sine_in_out(tt) if tt <= 1 else sine_in_out(2 - tt))
            overlay.alpha_composite(with_opacity(prep, opacity), (round(x), 0))
        else:  # spin
            angle = -360 * layer["dir"] * ((t_ms / layer["period"]) % 1)
            rotated = prep.rotate(angle, resample=Image.BICUBIC)
            x = (W - rotated.width) // 2
            y = (H - rotated.height) // 2
            overlay.alpha_composite(with_opacity(rotated, opacity), (x, y))
    if overlay.getextrema()[3][1] > 0:
        base = base.copy()
        base.alpha_composite(with_opacity(overlay, render_frame.intensity))
    return base.convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("theme", type=Path, help="theme directory holding backdrop/ and backgrounds/")
    ap.add_argument("--sim", type=float, default=None,
                    help="seconds of animation to compress into the clip (default: per profile)")
    ap.add_argument("--out", type=Path, default=None, help="default: <theme>/backdrop/animation.webp")
    args = ap.parse_args()

    backdrop = args.theme / "backdrop"
    cfg = json.loads((backdrop / "backdrop.json").read_text())
    profile = cfg.get("profile", "fog")
    render_frame.intensity = float(cfg.get("intensity", 0.2))
    speed = float(cfg.get("speed", 1)) or 1

    spec = PROFILES.get(profile, PROFILES["fog"])
    plates = sorted(backdrop.glob("*.png"))
    plates = [p for p in plates if p.name != "animation.webp"]

    layers = []
    for i, layer in enumerate(spec["layers"]):
        if layer["plate"] >= len(plates):
            continue
        entry = dict(layer)
        entry["kind"] = layer.get("kind", spec["kind"])
        entry["phase"] = i / len(spec["layers"])
        if "move" in entry:
            entry["move"] = entry["move"] / speed
        if "period" in entry:
            entry["period"] = entry["period"] / speed
        layers.append(entry)
    if not layers:
        raise SystemExit(f"{args.theme}: no layers (profile={profile}, plates={len(plates)})")

    wallpaper = sorted((args.theme / "backgrounds").glob("*.webp"))[0]
    base = cover(Image.open(wallpaper).convert("RGBA"), W, H)

    side = round(max(W, H) * 1.05)
    prepared = []
    for layer in layers:
        img = Image.open(plates[layer["plate"]]).convert("RGBA")
        if layer["kind"] == "spin":
            prepared.append(fit(img, round(side * layer.get("scale", 1))))
        else:
            prepared.append(cover(img, W, H))

    sim = args.sim or {"pulse": 36, "fog": 20, "mist": 24, "orrery": 120}.get(profile, 20)
    frames_n = CLIP_SECONDS * FPS
    frames = [render_frame(base, prepared, layers, sim * 1000 * i / frames_n) for i in range(frames_n)]

    # Loop seam: blend the last frames toward the first ones.
    k = max(1, round(SEAM_SECONDS * FPS))
    for i in range(k):
        a = (i + 1) / (k + 1)
        frames[-k + i] = Image.blend(frames[-k + i], frames[i], a)

    out = args.out or backdrop / "animation.webp"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=round(1000 / FPS),
                   loop=0, quality=70, method=4)
    size_kb = out.stat().st_size / 1024
    print(f"{out}  {frames_n} frames, {sim:.0f}s simulated, {size_kb:.0f} KiB")


if __name__ == "__main__":
    main()
