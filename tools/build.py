"""Genera la web estática del recetario a partir de data/recetas.json y data/fotos.json.

Uso:  python3 tools/build.py
Crea index.html, una carpeta por receta (<slug>/index.html) y los códigos QR en qr/.
"""
import html
import json
import os
import re

import segno
from jinja2 import Environment, FileSystemLoader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://ragonzalezram83.github.io/recetas-li-you/"

recipes = json.load(open(os.path.join(ROOT, "data/recetas.json"), encoding="utf-8"))
fotos = json.load(open(os.path.join(ROOT, "data/fotos.json"), encoding="utf-8"))


def md(text):
    """Texto de la ficha a HTML: negritas, dudas [POR CONFIRMAR] y notas editoriales entre corchetes."""
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\[POR CONFIRMAR(?::\s*([^\]]+))?\]",
               lambda m: '<span class="doubt">POR CONFIRMAR' + (": " + m.group(1) if m.group(1) else "") + "</span>", t)
    t = re.sub(r"\[([^\]]+)\]", r'<span class="ed">[\1]</span>', t)
    return t


def timers_in(text):
    """Solo los tiempos escritos en el propio paso; no se inventa ninguno."""
    found = []
    for m in re.finditer(r"(\d+)\s*minutos", text):
        n = int(m.group(1))
        found.append({"label": f"{n} min", "seconds": n * 60})
    if re.search(r"\b1 hora\b", text):
        found.append({"label": "1 hora", "seconds": 3600})
    if "media hora" in text:
        found.append({"label": "media hora", "seconds": 1800})
    if "tres cuartos de hora" in text:
        found.append({"label": "tres cuartos de hora", "seconds": 2700})
    return found


def photos_for(slug):
    folder = os.path.join(ROOT, "img", slug)
    if not os.path.isdir(folder):
        return []
    return sorted(f for f in os.listdir(folder) if f.endswith(".jpg"))


def man_file(p):
    return f"img/man/imp-{p['page']}.jpg" if p["src"] == "imp" else f"img/man/pdf-{p['page']:02d}.jpg"


def man_caption(p):
    return f"«Importancia.pdf», hoja {p['page']}" if p["src"] == "imp" else f"Página {p['page']} del cuaderno"


for r in recipes:
    rest = r["intro"][len(r["title"]):].lstrip(", ").strip()
    r["facts"] = [s.strip().rstrip(".") for s in re.split(r"\.\s+", rest) if s.strip()]
    r["facts"] = [f[0].upper() + f[1:] for f in r["facts"]]
    if not r["facts"]:
        r["facts"] = ["Raciones sin indicar"]
    r["pages_html"] = [{"src": man_file(p), "caption": man_caption(p)} for p in r["pages"]]
    nums = [p["page"] for p in r["pages"] if p["src"] == "pdf"]
    r["page_label"] = ("págs. " + "–".join(str(n) for n in nums)) if len(nums) > 1 else (f"pág. {nums[0]}" if nums else "")
    r["photos"] = photos_for(r["slug"])
    hero = fotos["photos"].get(r["slug"], {}).get("hero")
    if hero and f"{hero:02d}.jpg" in r["photos"]:
        r["hero"], r["hero_is_photo"] = f"img/{r['slug']}/{hero:02d}.jpg", True
    else:
        r["hero"], r["hero_is_photo"] = r["pages_html"][0]["src"], False

    steps, n = [], 0
    r["groups_html"] = []
    for g in r["stepGroups"]:
        items = []
        for s in g["steps"]:
            n += 1
            items.append(md(s))
            steps.append({"phase": g["label"], "html": md(s), "timers": timers_in(s)})
        r["groups_html"].append({"label": g["label"], "start": n - len(items) + 1, "items": items})
    for a in r["afterSteps"]:
        steps.append({"phase": "Al final", "html": md(a), "timers": timers_in(a)})
    r["cook_json"] = json.dumps({"slug": r["slug"], "steps": steps}, ensure_ascii=False).replace("</", "<\\/")
    r["url"] = BASE_URL + r["slug"] + "/"

env = Environment(loader=FileSystemLoader(os.path.join(ROOT, "tools/templates")), autoescape=False)
env.filters["md"] = md

chapters = [{"id": cid, "title": t, "recipes": [r for r in recipes if r["chapter"] == cid]} for cid, t in fotos["chapters"]]

with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
    f.write(env.get_template("index.html").render(chapters=chapters, base_url=BASE_URL))

os.makedirs(os.path.join(ROOT, "qr"), exist_ok=True)
for r in recipes:
    d = os.path.join(ROOT, r["slug"])
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(env.get_template("receta.html").render(r=r))
    qr = segno.make(r["url"], error="m")
    qr.save(os.path.join(ROOT, "qr", r["slug"] + ".svg"), scale=10, border=2, dark="#1f2430")
    qr.save(os.path.join(ROOT, "qr", r["slug"] + ".png"), scale=20, border=2, dark="#1f2430")

segno.make(BASE_URL, error="m").save(os.path.join(ROOT, "qr", "portada.svg"), scale=10, border=2, dark="#1f2430")
segno.make(BASE_URL, error="m").save(os.path.join(ROOT, "qr", "portada.png"), scale=20, border=2, dark="#1f2430")
print(f"{len(recipes)} recetas generadas")
