"""Sustituye las fotos publicadas por su copia retocada del libro, cuando existe.

Uso:  python3 tools/retocadas.py /mnt/project-files/libro/fotos-retocadas
Solo toca fotos ya publicadas (las de personas no están en img/ y no se añaden).
"""
import json
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
claves = json.load(open(os.path.join(src, "claves.json")))
por_original = {}
for clave, original in claves.items():
    por_original.setdefault(original, clave)
fotos = json.load(open(os.path.join(ROOT, "data/fotos.json")))
for slug, e in fotos["photos"].items():
    for i, original in enumerate(e["original"], 1):
        dest = os.path.join(ROOT, "img", slug, f"{i:02d}.jpg")
        if original in por_original and os.path.exists(dest):
            im = Image.open(os.path.join(src, por_original[original] + ".jpg")).convert("RGB")
            im.thumbnail((1200, 1200))
            im.save(dest, quality=74, optimize=True, progressive=True)
            print(slug, i, por_original[original])
