#!/usr/bin/env python3
"""Rebrand Omarchy's stock fastfetch config for Pagan.

Only the section headers, key colors, logo color and a tagline change; every
module, icon and box width is taken verbatim from the stock config so the
About window still fits its content.

    ./gen_pagan_fastfetch.py out.jsonc
"""
import json, os, re, sys

STOCK = os.path.join(os.environ.get("OMARCHY_PATH",
                     os.path.expanduser("~/.local/share/omarchy")),
                     "etc/fastfetch/config.jsonc")
ESC = chr(27)

# ANSI names, so the panel tracks whichever Pagan theme is active rather than
# pinning one theme's hexes into a config that is global to the machine.
# The band's palette is monochrome plus ice blue and blood red; these are it.
ICE, FROST, BLOOD = "blue", "cyan", "red"

SECTIONS = [
    ("Hardware",              "The Vessel · Hardware", ICE),
    ("Software",              "The Rites · Software", FROST),
    ("Age / Uptime / Update", "The Cycle · Age / Uptime / Update", BLOOD),
]
TAGLINE = "In Hoc Signo Vinces"


def head(label, width=54):
    pad = width - 2 - len(label)
    left = pad // 2
    return ESC + "[90m┌" + "─" * left + label + "─" * (pad - left) + "┐"


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
        "~/.config/fastfetch/config.jsonc")
    cfg = json.loads(re.sub(r"^\s*//.*$", "", open(STOCK, encoding="utf-8").read(),
                            flags=re.M))

    cfg["logo"]["color"] = {"1": ICE}

    colour = None
    for m in cfg["modules"]:
        if isinstance(m, dict) and m.get("type") == "custom" and "┌" in m.get("format", ""):
            for stock, label, c in SECTIONS:
                if stock in m["format"]:
                    m["format"] = head(label)
                    colour = c
                    break
        elif isinstance(m, dict) and "keyColor" in m and colour:
            m["keyColor"] = colour

    cfg["modules"].append({"type": "custom",
                           "format": ESC + "[90m" + " " * ((54 - len(TAGLINE)) // 2) + TAGLINE})
    cfg["modules"].append("break")

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("// Pagan — fastfetch / Omarchy About.\n"
                "// Logo: ~/.config/omarchy/branding/about.txt (the band logo).\n"
                "// Key colors are ANSI names so they track the active Omarchy theme:\n"
                "//   blue = ice, cyan = frost, red = blood.\n")
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
