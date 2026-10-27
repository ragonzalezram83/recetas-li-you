import json, re, sys
lines = open(sys.argv[1]).read().split("\n")
META = {
 "Muslos de pollo guisados": ("muslos-de-pollo", "carnes", [("pdf",1),("pdf",2)], None),
 "Costillas adobadas con patatas": ("costillas", "carnes", [("pdf",3),("pdf",4)], "costillas con patatas"),
 "Patatas a la importancia": ("patatas-importancia", "verdura", [("imp",1),("pdf",15)], "patatas Importancia"),
 "Albóndigas en salsa": ("albondigas", "carnes", [("pdf",5),("pdf",6)], "albondigas"),
 "Macarrones con chorizo y carne picada": ("macarrones", "verdura", [("pdf",7),("pdf",8)], None),
 "Cocido casero": ("cocido", "cocido", [("pdf",9),("pdf",10)], "sopa de cocido"),
 "Conejo al ajillo": ("conejo", "carnes", [("pdf",11),("pdf",12)], None),
 "Croquetas de cocido": ("croquetas", "cocido", [("pdf",13),("pdf",14)], "Croquetas"),
 "Huevos rellenos": ("huevos-rellenos", "verdura", [("pdf",16),("pdf",17)], "Huevos rellenos"),
 "Calamares en su tinta": ("calamares", "verdura", [("pdf",18),("pdf",19)], "Calamares en su tinta"),
 "Arroz con leche": ("arroz-con-leche", "postres", [("pdf",20)], "Arroz con leche"),
}
recipes, cur, sec, sub = [], None, None, None
for ln in lines:
    if ln.startswith("## "):
        t = ln[3:].strip()
        cur = None
        if t in META:
            slug, ch, pages, folder = META[t]
            cur = dict(slug=slug, title=t, chapter=ch, pages=[{"src":s,"page":p} for s,p in pages], photoFolder=folder,
                       transcriptionHeading="", transcription=[], margin=[], intro="", ingredients=[], stepGroups=[],
                       afterSteps=[], notes=[], warnings=[], source="")
            recipes.append(cur)
        continue
    if cur is None: continue
    if ln.startswith("### A."): sec="A"; cur["transcriptionHeading"]=ln[4:].strip(); continue
    if ln.startswith("### B."): sec="B"; sub=None; continue
    if not ln.strip(): continue
    if sec=="A":
        if ln.startswith("> "): cur["transcription"].append(ln[2:])
        else:
            m = re.match(r"_(.+?):_\s*(.*)", ln)
            cur["margin"].append({"label": m.group(1), "text": m.group(2)} if m else {"label":"", "text": ln})
        continue
    # B
    if ln.startswith("**Ingredientes**"): sub="ing"; continue
    if ln.startswith("**Preparación**"): sub="prep"; continue
    if ln.startswith("**Notas de mamá**"): sub="notes"; continue
    if ln.startswith("**Avisos**"): sub="warn"; continue
    if ln.startswith("**Fuente**"): cur["source"]=re.sub(r"^\*\*Fuente\*\*:\s*","",ln); sub=None; continue
    if sub is None and ln.startswith("**"):
        cur["intro"] = ln.replace("**","").strip(); continue
    item = re.sub(r"^(- |\d+\. )","",ln)
    if sub=="ing": cur["ingredients"].append(item)
    elif sub=="prep":
        if re.match(r"^(- |\d+\. )", ln):
            if not cur["stepGroups"]: cur["stepGroups"].append({"label":"", "steps":[]})
            cur["stepGroups"][-1]["steps"].append(item)
        elif ln.endswith(":") and len(ln)<40:
            cur["stepGroups"].append({"label": ln[:-1], "steps": []})
        else:
            cur["afterSteps"].append(ln)
    elif sub=="notes": cur["notes"].append(item)
    elif sub=="warn": cur["warnings"].append(item)
    else: print("UNHANDLED", cur["slug"], ln, file=sys.stderr)
json.dump(recipes, open(sys.argv[2],"w"), ensure_ascii=False, indent=1)
for r in recipes: print(r["slug"], len(r["ingredients"]), [ (g["label"],len(g["steps"])) for g in r["stepGroups"]], r["afterSteps"], r["intro"])
