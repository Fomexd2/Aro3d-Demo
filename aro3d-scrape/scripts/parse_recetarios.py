#!/usr/bin/env python3
"""
Parsea pages/recetarios.html (tabla server-rendered, ~10k filas) a:
  - data/recetarios.csv
  - data/recetarios.json

Columnas de la tabla original:
  No. | Paciente | Telefono | Email | Doctor | Clinica | Fecha de Cita | Estatus | Fecha de Alta | (acciones)

Además extrae de la celda de acciones los tokens de las URLs:
  - /mi-nube-aro/recetario/?...     (ver/editar recetario)
  - /receta-digital/?...            (receta digital pública)
"""
import re, csv, json, os, html as htmllib, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC  = os.path.join(ROOT, "pages", "recetarios.html")
OUT_CSV  = os.path.join(ROOT, "data", "recetarios.csv")
OUT_JSON = os.path.join(ROOT, "data", "recetarios.json")

def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s)          # quita tags
    s = htmllib.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def main():
    if not os.path.exists(SRC):
        sys.exit(f"No existe {SRC}. Corre scrape.sh primero.")
    html = open(SRC, encoding='utf-8', errors='replace').read()
    m = re.search(r'<tbody[^>]*>(.*)</tbody>', html, re.S | re.I)
    body = m.group(1) if m else html
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', body, re.S | re.I)
    out = []
    for r in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S | re.I)
        if len(cells) < 9:
            continue
        # tokens de URLs en la celda de acciones (y en toda la fila)
        url_rec = re.search(r'(?:mi-nube-aro/)?recetario/\?([^"\'#\s]+)', r)
        url_dig = re.search(r'receta-digital/\?([^"\'#\s]+)', r)
        paciente = clean(cells[1])
        # la celda Paciente trae el label responsivo "Fecha de Alta: ..." -> recortar
        paciente = re.split(r'\s*Fecha de Alta:', paciente)[0].strip()
        out.append({
            "no":            clean(cells[0]),
            "paciente":      paciente,
            "telefono":      clean(cells[2]),
            "email":         clean(cells[3]),
            "doctor":        clean(cells[4]),
            "clinica":       clean(cells[5]),
            "fecha_cita":    clean(cells[6]),
            "estatus":       clean(cells[7]),
            "fecha_alta":    clean(cells[8]),
            "qs_recetario":     htmllib.unescape(url_rec.group(1)) if url_rec else "",
            "qs_receta_digital":htmllib.unescape(url_dig.group(1)) if url_dig else "",
        })
    # escribir
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    cols = ["no","paciente","telefono","email","doctor","clinica",
            "fecha_cita","estatus","fecha_alta","qs_recetario","qs_receta_digital"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    # resumen
    estatus = {}
    for o in out:
        estatus[o["estatus"]] = estatus.get(o["estatus"], 0) + 1
    print(f"recetarios parseados: {len(out)}")
    print("por estatus:", estatus)
    print("CSV ->", OUT_CSV)
    print("JSON->", OUT_JSON)

if __name__ == "__main__":
    main()
