#!/usr/bin/env python3
"""
Aplana data/citas.json (respuesta cruda de control-json-citas.php) a data/citas.csv
para abrir en Excel/Sheets. Limpia el HTML embebido del campo Estudios.
"""
import json, csv, os, re, html as htmllib, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC  = os.path.join(ROOT, "data", "citas.json")
OUT  = os.path.join(ROOT, "data", "citas.csv")

def clean(v):
    if not isinstance(v, str):
        return v
    v = re.sub(r'<[^>]+>', ' ', v)
    v = htmllib.unescape(v)
    return re.sub(r'\s+', ' ', v).strip()

def main():
    if not os.path.exists(SRC):
        sys.exit(f"No existe {SRC}. Corre scrape.sh primero.")
    data = json.load(open(SRC, encoding="utf-8"))
    if not data:
        sys.exit("citas.json vacío")
    cols = list(data[0].keys())
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in data:
            w.writerow({k: clean(row.get(k, "")) for k in cols})
    print(f"citas aplanadas: {len(data)}  ->  {OUT}")

if __name__ == "__main__":
    main()
