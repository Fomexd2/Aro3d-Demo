# Qué está mal hoy (y cómo mejorarlo en la migración C# + Flutter)

Hallazgos del scrapeo, ordenados por impacto. Sirven de checklist para el rediseño.

## Seguridad / privacidad

1. **Datos sensibles sin paginar en un solo JSON.** `control-json-citas.php` devuelve
   **los 9 759 registros** (PII de pacientes: nombre, email, teléfono, edad, estudios médicos,
   montos) en **una sola respuesta de ~11 MB**, cada vez que se abre el calendario.
   → *Migración:* API REST paginada + filtrado por rango real de fechas en el servidor;
   exponer solo los campos que la vista necesita.
2. **Tokens en la query string.** `recetario/?JWT=…&Tok=…` y `receta-digital/?JWT=…&Tok=…`
   ponen el JWT/token en la URL → queda en logs, historial, referer y caché; es reenviable.
   → *Migración:* tokens en header `Authorization`/cookie `HttpOnly`+`Secure`, o enlaces
   de un solo uso con expiración.
3. **Auth con cookies solapadas y legacy** (`jwt`, `jwtbd`, `phpsessid`, `iduser`).
   Mezcla sesión PHP + JWT casero. `iduser` en cookie es manipulable.
   → *Migración:* un solo esquema JWT firmado (claims de rol: admin/doctor/paciente) + refresh token.
4. **Sin control de acceso por rol evidente.** Las URLs por token dan acceso directo al recetario.
   → *Migración:* autorización por rol/owner en cada endpoint.

## Correctitud HTTP / API

5. **Responde `302 Found` pero con el body completo** (el JSON de citas y las páginas).
   Semántica HTTP rota; rompe clientes que siguen el redirect (`curl -L` aterriza en login).
   → *Migración:* `200` con `Content-Type: application/json`.
6. **El endpoint ignora sus parámetros.** `start`/`end` no filtran nada.
   → *Migración:* respetar filtros; validar input.

## Rendimiento

7. **Página de recetarios = ~60 MB de HTML.** ~10k filas embebidas server-side aunque usa
   DataTables (que ya pagina en cliente). Descarga y parseo enormes en cada visita.
   → *Migración:* lista virtualizada en Flutter + endpoint paginado/ordenable/buscable server-side.
8. **Sobre-fetch del calendario** (punto 1) también es un problema de performance puro.

## Calidad de datos

9. **`Doctor` y `Clinica` son texto libre** (duplicados, mayúsculas, "A QUIEN CORRESPONDA").
   La tabla de doctores existe pero no se usa de forma consistente.
   → *Migración:* normalizar a entidades Doctor/Clínica con FK; migrar texto → match/merge.
10. **Formatos de fecha inconsistentes:** `"25 / Junio / 2026 10:30:00"` (display, en español)
    conviven con `"2026-06-23 17:23:40"` (ISO-ish). `FechaNac` a veces `" /  / "`.
    → *Migración:* `DateTime`/ISO-8601 en almacenamiento y API; formateo solo en UI.
11. **Campos mezclan datos + HTML** (`Estudios` trae `<strong>`, `<br>`).
    → *Migración:* separar datos de presentación.
12. **Nombres de campos en español e inconsistentes** (`ApartoNam`, `HorInicio`, `MailFecha`).
    → *Migración:* esquema consistente (inglés o español, pero uniforme) + DTOs.

## Validación / integridad de datos (confirmado en vivo)

15. **Sin validación de unicidad al dar de alta** (lo reportó el usuario y se confirmó leyendo
    los catálogos del form "Agregar Cita", sin escribir nada):
    - **Pacientes:** 10 877 entradas en el catálogo, 10 614 distintas → **220 duplicados** por
      `nombre+email` (ej. `CASTAÑEDA ISAAC | …` ×8, `GUTIERREZ MARCOS GRISELDA | …` ×7).
    - **Doctores:** 660 entradas, 658 distintas → **2 duplicados exactos** (`JUAN ABIMAEL GARCIA
      CASTILLO | …` ×2, `SARA |` ×2).
    - **Clínicas:** mismo patrón (el usuario confirma que se puede dar de alta la misma clínica
      N veces). En las citas: **653** combinaciones `Paciente+Email` repetidas.
    - El JS del calendario **no tiene ninguna verificación** ("ya existe / duplicado / unique"
      → 0 coincidencias). El alta crea fila nueva siempre.
    → *Migración:* `UNIQUE` en BD (email/teléfono normalizados) + chequeo en el servicio antes de
      insertar; en el alta, **buscar y reutilizar** (autocomplete que matchea existentes) en vez de
      crear ciegamente; merge de duplicados históricos en la migración de datos.
16. **Datos de prueba mezclados con producción**: hay registros "PRUEBA"/"TEST" en la BB real
    (ej. "ALEJANDRO OLIVARES PRUEBA" ×5, "Oscar Prueba", "prueba página").
    → *Migración:* separar entornos (prod/staging) y semilla de datos de prueba aparte.

### Endpoints del flujo de alta/edición (todos POST, sin validación de duplicados)
`control-crear-cita.php`, `control-crear-cita-calendario.php`, `control-editar-cita-calendario.php`,
`control-cancel-cita.php`, `control-get-horarios.php`. (No ejecutados — solo lectura del JS.)

## Arquitectura

13. **No hay API; el HTML y los datos están acoplados** (server-rendered con datos embebidos).
    → *Migración:* backend ASP.NET Core como **API REST/JSON** + cliente **Flutter** desacoplado.
14. **Lógica repartida en `controladores/*.php` sueltos**, sin capa de servicios/repositorios clara.
    → *Migración:* arquitectura por capas (Controllers → Services → Repositories → EF Core).
