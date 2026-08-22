#!/usr/bin/env python3
"""Build the Gand terminal art: the About logo and the screensaver panel.

    ./gen_ascii.py ../branding [--hostname cachyos-desktop]

Writes:
  about.txt        50x26  -- the sigil alone, inside omarchy's 54x26 logo budget
  screensaver.txt  56x38  -- sigil / GAND wordmark / tagline / hostname

Needs `omarchy transcode ascii` on PATH (or OMARCHY_PATH set), plus the sigil
built by gen_sigil.py.
"""
import argparse, os, socket, subprocess, sys, tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TAGLINE = "Craft. Culture. Code."
SERIF_CANDIDATES = (
    "/usr/share/fonts/noto/NotoSerif-Regular.ttf",
    "/usr/share/fonts/TTF/NotoSerif-Regular.ttf",
    "/usr/share/fonts/noto/NotoSerif[wdth,wght].ttf",
)


def transcode(src, dest, width, height, mode="braille", threshold=45):
    omarchy = os.path.join(os.environ.get(
        "OMARCHY_PATH", os.path.expanduser("~/.local/share/omarchy")), "bin")
    exe = os.path.join(omarchy, "omarchy-transcode-ascii")
    if not os.path.exists(exe):
        exe = "omarchy-transcode-ascii"
    subprocess.run([exe, src, dest, "--width", str(width), "--height", str(height),
                    "--mode", mode, "--threshold", str(threshold)],
                   check=True, stdout=subprocess.DEVNULL)
    return [l.rstrip("\n") for l in open(dest, encoding="utf-8")]


def wordmark_source(path, text="GAND", size=300, tracking=52):
    font = None
    for cand in SERIF_CANDIDATES:
        if os.path.exists(cand):
            font = ImageFont.truetype(cand, size)
            break
    if font is None:
        sys.exit("no serif font found; install noto-fonts")

    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    w = int(sum(probe.textlength(c, font=font) for c in text)
            + tracking * (len(text) - 1)) + 40
    img = Image.new("L", (w, int(size * 1.34)), 255)
    d = ImageDraw.Draw(img)
    x = 20
    for c in text:
        d.text((x, img.height // 2), c, font=font, fill=0, anchor="lm")
        x += d.textlength(c, font=font) + tracking
    img.save(path)
    return path


def centred(lines, field):
    pad = (field - max(len(l) for l in lines)) // 2
    return [(" " * pad + l).rstrip() for l in lines]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("outdir")
    p.add_argument("--sigil", default=None,
                   help="sigil PNG; built with gen_sigil.py if omitted")
    p.add_argument("--hostname", default=socket.gethostname())
    args = p.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="gand-ascii-")

    sigil = args.sigil
    if not sigil:
        sigil = os.path.join(tmp, "sigil.png")
        subprocess.run([sys.executable, os.path.join(HERE, "gen_sigil.py"), sigil],
                       check=True, stdout=subprocess.DEVNULL)

    # About: the sigil alone, sized to omarchy's logo budget.
    about = os.path.join(args.outdir, "about.txt")
    sigil_lines = transcode(sigil, about, 54, 26)

    # Screensaver: sigil over the wordmark, tagline and host.
    word_lines = transcode(wordmark_source(os.path.join(tmp, "word.png")),
                           os.path.join(tmp, "word.txt"), 56, 9)

    field = max(max(map(len, sigil_lines)), max(map(len, word_lines)))
    panel = (centred(sigil_lines, field) + [""] +
             centred(word_lines, field) + [""] +
             centred([TAGLINE], field) + [""] +
             centred([args.hostname], field))

    saver = os.path.join(args.outdir, "screensaver.txt")
    with open(saver, "w", encoding="utf-8") as f:
        f.write("\n".join(panel) + "\n")

    print(f"{about}: {len(sigil_lines)}x{max(map(len, sigil_lines))}")
    print(f"{saver}: {len(panel)}x{field}")


if __name__ == "__main__":
    main()
