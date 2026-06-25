# aro3d-scrape

Scrapeo de **aro3d.com / Mi Nube Aro** (panel del laboratorio dental 3D) para la
migración a **C# (ASP.NET Core) + Flutter**. Incluye datos, scripts re-ejecutables
y documentación de endpoints / funcionamiento / problemas.

## Contenido

```
aro3d-scrape/
├── README.md
├── data/                      # datos extraídos (datos sensibles de pacientes)
│   ├── citas.json   (9 759)   # respuesta cruda de control-json-citas.php (rica)
│   ├── citas.csv              # misma data aplanada para Excel
│   ├── recetarios.json (10 058)
│   └── recetarios.csv
├── pages/                     # HTML crudo descargado (fuente para los parsers)
│   ├── recetarios.html  (~60MB)
│   └── lista-de-doctores.html
├── scripts/
│   ├── cookies.env            # cookies de sesión (REFRESCAR si caducan)
│   ├── scrape.sh              # descarga todo y parsea  ->  ejecutable
│   ├── parse_recetarios.py
│   └── parse_citas.py
└── docs/
    ├── ENDPOINTS.md           # rutas, controladores, métodos, respuestas
    ├── APP.md                 # cómo funciona, módulos, modelo de datos, auth, stack
    └── PROBLEMAS.md           # qué está mal + cómo mejorarlo en la migración
```

## Re-ejecutar el scrapeo

```bash
cd aro3d-scrape
./scripts/scrape.sh
```

Si empieza a caer en la página de login o trae 0 registros, las cookies caducaron:
edita `scripts/cookies.env` siguiendo las instrucciones de ese archivo.

## Resumen de datos

| Dataset | Registros | Rango / estatus |
|---------|-----------|------------------|
| Citas   | 9 759 | 2022-05-30 → 2026-07-06 |
| Recetarios | 10 058 | Con Cita 9 327 · Por Confirmar 511 · Cancelado 219 · Completo 1 |
| Doctores | 0 | tabla vacía en esta cuenta (Doctor es texto libre en el recetario) |

> ⚠️ `data/` contiene **datos personales de pacientes** (nombres, contacto, estudios médicos,
> montos). Trátalo como información sensible: no lo subas a repos públicos ni lo compartas.
