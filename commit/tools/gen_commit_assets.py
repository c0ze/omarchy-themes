#!/usr/bin/env python3
"""Commit!!! theme assets: Plymouth unlock logos and the terminal art.

    ./gen_commit_assets.py themes/ branding/ [--hostname NAME]

Writes themes/<theme>/unlock.png for each theme, plus branding/about.txt and
branding/screensaver.txt.
"""
import argparse, os, socket, subprocess, sys, tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TAGLINE = "Push code. Pull requests. Merge a life."

MONO = ("/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/liberation/LiberationMono-Bold.ttf")

# Body colour per theme; the "!!!" always keeps the game's AMBER.
UNLOCK = {
    "commit-late-night": "#7CFFB2",
    "commit-evening": "#FFCE86",
    "commit-morning": "#0F8A4B",
}
AMBER = "#FFB454"


def mono(size):
    for cand in MONO:
        if os.path.exists(cand):
            return ImageFont.truetype(cand, size)
    sys.exit("no monospace font found")


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def sigil(form, path):
    subprocess.run([sys.executable, os.path.join(HERE, "gen_commit_sigil.py"),
                    form, path], check=True, stdout=subprocess.DEVNULL)
    return path


def transcode(src, dest, width, height, mode="braille", threshold=50):
    omarchy = os.path.join(os.environ.get(
        "OMARCHY_PATH", os.path.expanduser("~/.local/share/omarchy")), "bin")
    exe = os.path.join(omarchy, "omarchy-transcode-ascii")
    if not os.path.exists(exe):
        exe = "omarchy-transcode-ascii"
    subprocess.run([exe, src, dest, "--width", str(width), "--height", str(height),
                    "--mode", mode, "--threshold", str(threshold)],
                   check=True, stdout=subprocess.DEVNULL)
    return [l.rstrip("\n") for l in open(dest, encoding="utf-8")]


def unlock(mark_path, body, out):
    W, H = 800, 188
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # The mark: black-on-white art becomes an alpha mask in the body colour.
    art = Image.open(mark_path).convert("L")
    art = art.point(lambda v: 255 - v)                 # ink -> opaque
    art = art.crop(art.getbbox())
    # The mark is ~3:1, so height alone would size it wider than the strip.
    scale = min((H - 24) / art.height, (W * 0.30) / art.width)
    art = art.resize((max(1, int(art.width * scale)),
                      max(1, int(art.height * scale))), Image.LANCZOS)
    tinted = Image.new("RGBA", art.size, rgb(body) + (0,))
    tinted.putalpha(art)

    d = ImageDraw.Draw(img)
    word, bangs = "commit", "!!!"
    gap = 40
    for size in range(96, 39, -2):
        font = mono(size)
        word_w = d.textlength(word, font=font)
        bang_w = d.textlength(bangs, font=font)
        total = art.width + gap + word_w + bang_w
        if total <= W - 40:
            break

    x = (W - total) / 2
    img.alpha_composite(tinted, (int(x), (H - art.height) // 2))
    x += art.width + gap
    d.text((x, H / 2), word, font=font, fill=rgb(body) + (255,), anchor="lm")
    d.text((x + word_w, H / 2), bangs, font=font, fill=rgb(AMBER) + (255,), anchor="lm")

    img.save(out)
    return out


def wordmark(path, size=220):
    font = mono(size)
    txt = "commit!!!"
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    w = int(probe.textlength(txt, font=font)) + 40
    img = Image.new("L", (w, int(size * 1.36)), 255)
    ImageDraw.Draw(img).text((20, img.height // 2), txt, font=font, fill=0, anchor="lm")
    img.save(path)
    return path


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

    tmp = tempfile.mkdtemp(prefix="commit-assets-")
    mark = sigil("mark", os.path.join(tmp, "mark.png"))
    graph = sigil("graph", os.path.join(tmp, "graph.png"))

    for theme, body in UNLOCK.items():
        out = os.path.join(args.themes_dir, theme, "unlock.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        unlock(mark, body, out)
        print("unlock:", theme)

    os.makedirs(args.branding_dir, exist_ok=True)
    about = os.path.join(args.branding_dir, "about.txt")
    graph_lines = transcode(graph, about, 54, 26)

    word_lines = transcode(wordmark(os.path.join(tmp, "word.png")),
                           os.path.join(tmp, "word.txt"), 70, 9)

    field = max(max(map(len, graph_lines)), max(map(len, word_lines)))
    panel = (centred(graph_lines, field) + [""] +
             centred(word_lines, field) + [""] +
             centred([TAGLINE], field) + [""] +
             centred([args.hostname], field))

    saver = os.path.join(args.branding_dir, "screensaver.txt")
    with open(saver, "w", encoding="utf-8") as f:
        f.write("\n".join(panel) + "\n")

    print(f"{about}: {len(graph_lines)}x{max(map(len, graph_lines))}")
    print(f"{saver}: {len(panel)}x{field}")


if __name__ == "__main__":
    main()
