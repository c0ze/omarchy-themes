#!/usr/bin/env python3
"""Rebrand Omarchy's stock fastfetch config for Commit!!!

Only the section headers, key colors, logo color and a tagline change; every
module, icon and box width is taken verbatim from the stock config so the
About window still fits its content.

    ./gen_commit_fastfetch.py out.jsonc
"""
import json, os, re, sys

STOCK = os.path.join(os.environ.get("OMARCHY_PATH",
                     os.path.expanduser("~/.local/share/omarchy")),
                     "etc/fastfetch/config.jsonc")
ESC = chr(27)

# ANSI names, so the panel tracks whichever Commit theme is active rather than
# pinning one theme's hexes into a config that is global to the machine.
PHOSPHOR, SIGNAL, PULSE = "green", "blue", "yellow"

SECTIONS = [
    ("Hardware",              "The Rig · Hardware", PHOSPHOR),
    ("Software",              "The Stack · Software", SIGNAL),
    ("Age / Uptime / Update", "The Run · Age / Uptime / Update", PULSE),
]
TAGLINE = "Push code. Pull requests. Merge a life."


def head(label, width=54):
    pad = width - 2 - len(label)
    left = pad // 2
    return ESC + "[90m┌" + "─" * left + label + "─" * (pad - left) + "┐"


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
        "~/.config/fastfetch/config.jsonc")
    cfg = json.loads(re.sub(r"^\s*//.*$", "", open(STOCK, encoding="utf-8").read(),
                            flags=re.M))

    cfg["logo"]["color"] = {"1": PHOSPHOR}

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

    def footer(text, colour="90"):
        """One centred line in the 54-wide box the section headers use."""
        return {"type": "custom",
                "format": ESC + "[" + colour + "m"
                          + " " * max(0, (54 - len(text)) // 2) + text}

    cfg["modules"].append(footer(TAGLINE))
    cfg["modules"].append(footer("commit.gand.tr", "32"))
    cfg["modules"].append(footer("Out now on Steam and Google Play", "90"))
    cfg["modules"].append("break")

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("// Commit!!! — fastfetch / Omarchy About.\n"
                "// Logo: ~/.config/omarchy/branding/about.txt (the commit graph).\n"
                "// Key colors are ANSI names so they track the active Omarchy theme:\n"
                "//   green = phosphor, blue = signal, yellow = the Pulse.\n")
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
