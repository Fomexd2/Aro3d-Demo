#!/usr/bin/env bash
# ============================================================================
#  Scraper de aro3d.com / Mi Nube Aro  ->  carpeta aro3d-scrape/
#  Re-ejecutable en local. Requiere: curl + python3.
#
#  Uso:   ./scripts/scrape.sh
#  Auth:  scripts/cookies.env  (refresca las cookies si caducan)
# ============================================================================
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
source "$HERE/cookies.env"

DATA="$ROOT/data"; PAGES="$ROOT/pages"
mkdir -p "$DATA" "$PAGES"

hdr=(-H "Cookie: $ARO_COOKIE" -H "User-Agent: Mozilla/5.0" )

echo "==> [1/4] Citas (control-json-citas.php, todas las fechas)"
# OJO: el endpoint IGNORA start/end y devuelve TODO el histórico. Responde 302
# pero con el body JSON completo, por eso NO usamos -L.
curl -s "${hdr[@]}" -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "start=2000-01-01&end=2100-01-01" \
  "$ARO_BASE/controladores/control-json-citas.php" -o "$DATA/citas.json" \
  -w "    HTTP %{http_code}  %{size_download} bytes\n"

echo "==> [2/4] Recetarios (página server-rendered, ~10k filas, ~60MB)"
curl -s "${hdr[@]}" "$ARO_BASE/mi-nube-aro/recetarios/" -o "$PAGES/recetarios.html" \
  -w "    HTTP %{http_code}  %{size_download} bytes\n"

echo "==> [3/4] Lista de doctores"
curl -s "${hdr[@]}" "$ARO_BASE/mi-nube-aro/lista-de-doctores/" -o "$PAGES/lista-de-doctores.html" \
  -w "    HTTP %{http_code}  %{size_download} bytes\n"

echo "==> [4/4] Parseo a CSV/JSON estructurado"
python3 "$HERE/parse_recetarios.py"
python3 "$HERE/parse_citas.py"

echo "==> Listo. Datos en: $DATA"
ls -lh "$DATA"
