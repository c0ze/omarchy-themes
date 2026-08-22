#!/usr/bin/env python3
"""Pagan theme assets: Plymouth unlock logos and the terminal art.

    ./gen_pagan_assets.py themes/ branding/ [--hostname NAME] [--variant old]

The band logo carries the name on its own — a black metal logo is the wordmark,
and its illegibility is the point — so nothing here sets the name in type.
"""
import argparse, os, socket, subprocess, sys, tempfile

from PIL import Image, ImageFilter

SITE = os.environ.get(
    "PAGAN_SITE", os.path.expanduser("~/projects/music/pagan/pagan.tr"))
# The 2019 sigil is square; the current logo is wide. Each needs its own
# transcode geometry or one of them ends up a stripe.
VARIANTS = {
    "current": dict(logo="pagan-logo.jpg", prefix="pagan",
                    about=(54, 26), saver=(74, 24), threshold=30, stroke=None),
    # The 2019 sigil is drawn in ~15px hairlines on a 3307px canvas. Scaled to
    # a terminal grid (30x down) or a Plymouth strip (20x down) they vanish
    # entirely, so its alpha is dilated first -- see thicken().
    "old": dict(logo="PAGAN-old.logo.png", prefix="pagan-old",
                about=(54, 26), saver=(56, 28), threshold=45, stroke=15),
}
VARIANT = VARIANTS["current"]
LOGO = os.path.join(SITE, "src/assets", VARIANT["logo"])

# "In Hoc Signo Vinces" is the band's own first demo, 1995.
MOTTO = "IN HOC SIGNO VINCES"

UNLOCK = {"dark": "#F2F2F2", "light": "#141414"}


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def logo_alpha():
    im = Image.open(LOGO)
    a = im.split()[-1] if im.mode in ("RGBA", "LA") else im.convert("L")
    return a.crop(a.getbbox())


def transcode(src, dest, width, height, threshold=None):
    threshold = VARIANT["threshold"] if threshold is None else threshold
    omarchy = os.path.join(os.environ.get(
        "OMARCHY_PATH", os.path.expanduser("~/.local/share/omarchy")), "bin")
    exe = os.path.join(omarchy, "omarchy-transcode-ascii")
    if not os.path.exists(exe):
        exe = "omarchy-transcode-ascii"
    cmd = [exe, src, dest, "--width", str(width), "--height", str(height),
           "--mode", "braille", "--threshold", str(threshold)]
    if VARIANT.get("stroke"):
        cmd.append("--invert")     # the thickened source is a greyscale alpha
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    return [l.rstrip("\n") for l in open(dest, encoding="utf-8")]


def thicken(mask, target_px):
    """Dilate a hairline mask so its strokes survive a big downscale.

    A stroke `stroke` px wide in a `mask.width` px source lands at
    stroke * target_px / mask.width in the output. Below ~1px it dithers away
    to nothing. Dilating by r widens every stroke by 2r, so solve for the r
    that puts the result at about two pixels.
    """
    stroke = VARIANT.get("stroke")
    if not stroke:
        return mask
    scale = target_px / mask.width
    want = 2.0 / scale
    r = int(round((want - stroke) / 2))
    if r < 1:
        return mask
    # logo_alpha() crops to the bounding box, so dilating in place would push
    # the outermost strokes off the canvas and clip the ring. Pad first.
    padded = Image.new("L", (mask.width + 2 * r, mask.height + 2 * r), 0)
    padded.paste(mask, (r, r))
    return padded.filter(ImageFilter.MaxFilter(2 * r + 1))


def unlock(mask, colour, out):
    W, H = 800, 188
    mask = thicken(mask, H - 16)
    scale = min((H - 16) / mask.height, (W - 60) / mask.width)
    art = mask.resize((max(1, int(mask.width * scale)),
                       max(1, int(mask.height * scale))), Image.LANCZOS)
    tinted = Image.new("RGBA", art.size, rgb(colour) + (0,))
    tinted.putalpha(art)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.alpha_composite(tinted, ((W - art.width) // 2, (H - art.height) // 2))
    img.save(out)


def centred(lines, field):
    pad = (field - max(len(l) for l in lines)) // 2
    return [(" " * pad + l).rstrip() for l in lines]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("themes_dir")
    p.add_argument("branding_dir")
    p.add_argument("--hostname", default=socket.gethostname())
    p.add_argument("--variant", default="current", choices=tuple(VARIANTS))
    args = p.parse_args()

    global VARIANT, LOGO
    VARIANT = VARIANTS[args.variant]
    LOGO = os.path.join(SITE, "src/assets", VARIANT["logo"])
    print("variant:", VARIANT["prefix"], f"({VARIANT['logo']})")

    mask = logo_alpha()
    for suffix, colour in UNLOCK.items():
        theme = f"{VARIANT['prefix']}-{suffix}"
        out = os.path.join(args.themes_dir, theme, "unlock.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        unlock(mask, colour, out)
        print("unlock:", theme)

    tmp = tempfile.mkdtemp(prefix="pagan-assets-")
    os.makedirs(args.branding_dir, exist_ok=True)


    src_about = LOGO
    src_saver = LOGO
    if VARIANT.get("stroke"):
        raw = logo_alpha()
        a = thicken(raw, VARIANT["about"][0] * 2)
        src_about = os.path.join(tmp, "about-src.png")
        a.save(src_about)
        b = thicken(raw, VARIANT["saver"][0] * 2)
        src_saver = os.path.join(tmp, "saver-src.png")
        b.save(src_saver)

    about = os.path.join(args.branding_dir, "about.txt")
    about_lines = transcode(src_about, about, *VARIANT["about"])

    # The screensaver has the whole screen, so give the logo the width it needs
    # to keep its spikes and the pentagram at its centre.
    saver_lines = transcode(src_saver, os.path.join(tmp, "saver.txt"), *VARIANT["saver"])

    field = max(max(map(len, saver_lines)), len(MOTTO))
    panel = (centred(saver_lines, field) + [""] +
             centred([MOTTO], field) + [""] +
             centred([args.hostname], field))

    saver = os.path.join(args.branding_dir, "screensaver.txt")
    with open(saver, "w", encoding="utf-8") as f:
        f.write("\n".join(panel) + "\n")

    print(f"{about}: {len(about_lines)}x{max(map(len, about_lines))}")
    print(f"{saver}: {len(panel)}x{field}")


if __name__ == "__main__":
    main()
