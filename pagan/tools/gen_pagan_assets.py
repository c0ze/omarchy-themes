#!/usr/bin/env python3
"""Pagan theme assets: Plymouth unlock logos and the terminal art.

    ./gen_pagan_assets.py themes/ branding/ [--hostname NAME]

The band logo carries the name on its own — a black metal logo is the wordmark,
and its illegibility is the point — so nothing here sets the name in type.
"""
import argparse, os, socket, subprocess, sys, tempfile

from PIL import Image

SITE = os.environ.get(
    "PAGAN_SITE", os.path.expanduser("~/projects/music/pagan/pagan.tr"))
LOGO = os.path.join(SITE, "src/assets/pagan-logo.jpg")

# "In Hoc Signo Vinces" is the band's own first demo, 1995.
MOTTO = "IN HOC SIGNO VINCES"

UNLOCK = {"pagan-dark": "#F2F2F2", "pagan-light": "#141414"}


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def logo_alpha():
    im = Image.open(LOGO)
    a = im.split()[-1] if im.mode in ("RGBA", "LA") else im.convert("L")
    return a.crop(a.getbbox())


def transcode(src, dest, width, height, threshold=30):
    omarchy = os.path.join(os.environ.get(
        "OMARCHY_PATH", os.path.expanduser("~/.local/share/omarchy")), "bin")
    exe = os.path.join(omarchy, "omarchy-transcode-ascii")
    if not os.path.exists(exe):
        exe = "omarchy-transcode-ascii"
    subprocess.run([exe, src, dest, "--width", str(width), "--height", str(height),
                    "--mode", "braille", "--threshold", str(threshold)],
                   check=True, stdout=subprocess.DEVNULL)
    return [l.rstrip("\n") for l in open(dest, encoding="utf-8")]


def unlock(mask, colour, out):
    W, H = 800, 188
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
    args = p.parse_args()

    mask = logo_alpha()
    for theme, colour in UNLOCK.items():
        out = os.path.join(args.themes_dir, theme, "unlock.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        unlock(mask, colour, out)
        print("unlock:", theme)

    tmp = tempfile.mkdtemp(prefix="pagan-assets-")
    os.makedirs(args.branding_dir, exist_ok=True)

    about = os.path.join(args.branding_dir, "about.txt")
    about_lines = transcode(LOGO, about, 54, 26)

    # The screensaver has the whole screen, so give the logo the width it needs
    # to keep its spikes and the pentagram at its centre.
    saver_lines = transcode(LOGO, os.path.join(tmp, "saver.txt"), 74, 24)

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
