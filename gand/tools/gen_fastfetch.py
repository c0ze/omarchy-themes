#!/usr/bin/env python3
"""Rebrand Omarchy's stock fastfetch config for Gand.

Only the section headers, key colors, logo color and a tagline change; every
module, icon and box width is taken verbatim from the stock config so the
About window still fits its content.
"""
import json, os, re, sys

STOCK = os.path.join(os.environ.get("OMARCHY_PATH",
                     os.path.expanduser("~/.local/share/omarchy")),
                     "etc/fastfetch/config.jsonc")
ESC = chr(27)
raw = open(STOCK, encoding="utf-8").read()
cfg = json.loads(re.sub(r"^\s*//.*$", "", raw, flags=re.M))

BRONZE, SAGE, STONE = "blue", "green", "cyan"   # accent-primary / -secondary / -stone

def head(label, width=54):
    pad = width - 2 - len(label)
    left = pad // 2
    return ESC + "[90m┌" + "─" * left + label + "─" * (pad - left) + "┐"

SECTIONS = [
    ("Hardware",              "The Stone · Hardware", BRONZE),
    ("Software",              "The Staff · Software", SAGE),
    ("Age / Uptime / Update", "The Vigil · Age / Uptime / Update", STONE),
]

cfg["logo"]["color"] = {"1": BRONZE}

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
            "format": ESC + "[" + colour + "m" + " " * max(0, (54 - len(text)) // 2) + text}

# BRONZE is the ANSI name; the escape is its code, so the link picks up the
# active theme's accent the same way the section keys do.
cfg["modules"].append(footer("Craft. Culture. Code."))
cfg["modules"].append(footer("gand.tr", "34"))
cfg["modules"].append("break")

path = (sys.argv[1] if len(sys.argv) > 1
        else os.path.expanduser("~/.config/fastfetch/config.jsonc"))
with open(path, "w", encoding="utf-8") as f:
    f.write("// Gand — fastfetch / Omarchy About.\n"
            "// Logo: ~/.config/omarchy/branding/about.txt (the gand.tr sigil).\n"
            "// Key colors are ANSI names so they track the active Omarchy theme:\n"
            "//   blue = accent-primary (the staff), green = accent-secondary, cyan = accent-stone.\n")
    json.dump(cfg, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("wrote", path)
