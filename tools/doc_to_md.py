"""Convierte la lectura del Claude Doc de transcripciones (JSON con data.xml) a data/transcripciones.md.

Uso:  python3 tools/doc_to_md.py lectura.json data/transcripciones.md
"""
import json
import sys
import xml.etree.ElementTree as ET

root = ET.fromstring(json.load(open(sys.argv[1]))["data"]["xml"])


def txt(e):
    out = ""
    for t in e.iter():
        if t.tag == "text":
            s = "".join(t.itertext())
            if t.find("bold") is not None:
                s = "**" + s + "**"
            if t.find("italic") is not None:
                s = "_" + s + "_"
            out += s
        elif t.tag == "mention":
            out += "@" + t.get("name", "")
        elif t.tag == "date":
            out += t.get("value", "")
    return out


lines = []


def walk(e, prefix=""):
    for c in e:
        if c.tag == "paragraph":
            h = c.get("heading")
            lines.append(("#" * int(h) + " " if h else prefix) + txt(c))
        elif c.tag == "blockquote":
            walk(c, "> ")
        elif c.tag == "list":
            for i, li in enumerate(c):
                for p in li:
                    if p.tag == "paragraph":
                        lines.append(prefix + ("- " if c.get("kind") == "bullet" else f"{i + 1}. ") + txt(p))
        else:
            lines.append(f"[{c.tag}] " + txt(c))


walk(root)
open(sys.argv[2], "w").write("\n".join(lines))
