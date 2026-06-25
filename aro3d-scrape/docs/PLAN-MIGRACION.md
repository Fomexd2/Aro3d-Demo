# Plan de migración aro3d → C# (ASP.NET Core) + Flutter

Reemplazar el PHP legacy (`aro3d.com` + panel `Mi Nube Aro`) por **API REST en ASP.NET Core**
+ **app Flutter**, conservando el dominio (recetarios / citas / estudios) y **arreglando** los
problemas detectados. Negocio: laboratorio de radiología/ortodoncia dental 3D (Cuernavaca).

## Dominio (lo que hay que conservar)
- **Recetario** = orden de estudios que un doctor manda al laboratorio para un paciente.
- **Cita** = agenda de ese recetario (fecha/hora, duración). 0..1 por recetario.
- **Estudios/Paquetes**: Estudio Ortodóntico ARO, cefalometrías (Ricketts/Steiner/Jarabak/
  Alexander), fotos (Boca Abierta/Cerrada/Visor/Dicom), escaneo (Maxila/Mandíbula), Cone Beam,
  Impresión 3D; paquetes PAQ1 Digital → PAQ6 ARO Platinum.
- **Roles**: Admin/Laboratorio, Doctor, Paciente.
- **Receta digital**: vista pública por token que recibe el paciente para confirmar/agendar.

## Fases

### 1. Modelo de datos (EF Core, SQL Server/PostgreSQL)
Entidades normalizadas: `Usuario(rol)`, `Doctor`, `Paciente`, `Clinica`, `Recetario`,
`Cita`, `Estudio`, `RecetarioEstudio`, `Paquete`.
- **UNIQUE** en email/teléfono normalizados (arregla el bug de duplicados).
- FKs reales (hoy Doctor/Clínica son texto libre).
- Fechas `DateTime`/ISO-8601; separar datos de presentación (quitar HTML de `Estudios`).

### 2. Migración de datos (one-shot)
- Fuente: `data/citas.json` (9 759) + `data/recetarios.json` (10 058) del scrape.
- **Dedupe**: 220 pacientes y 2 doctores duplicados por nombre+email; 653 combos repetidos.
- **Limpiar**: quitar registros de PRUEBA/TEST de producción.
- Mapear Doctor/Clínica texto libre → entidades (match + merge asistido).

### 3. API REST (ASP.NET Core)
- **Auth**: JWT firmado + refresh token en cookie `HttpOnly`+`Secure`; claim de rol
  (admin/doctor/paciente); login por email **o** teléfono; verificación de **reCAPTCHA** server-side;
  recuperación de contraseña; registro (doctor/paciente).
- **Endpoints** (paginados, filtrables, con autorización por rol/owner):
  recetarios, citas (feed de calendario por rango real), catálogos (doctores/pacientes/clínicas/
  estudios), horarios, receta-digital por token (link de un solo uso/expiración).
- Respuestas `200 application/json` (arreglar el `302`+body).

### 4. App Flutter
- **Theming**: `ColorScheme.fromSeed(Color(0xFFFCB92C))` (ámbar), superficie `#F1F5F7`, Nunito;
  panel navy `#182132`; sitio/receta pública teal `#8FB4AC`. Material 3.
- **Navegación por rol** (`go_router` + Drawer/NavigationRail).
- **Pantallas**: Calendario (`syncfusion`/`table_calendar`), Recetarios (lista paginada
  server-side + búsqueda), Form Agregar Cita (typeahead paciente/doctor que **reutiliza**
  existentes en vez de duplicar; checkboxes de estudios), Receta Digital pública (deep-link).
- Detalle en `docs/FRONTEND.md §7`.

### 5. Hardening (cierra los problemas de `docs/PROBLEMAS.md`)
No sobre-fetch de PII, paginación, tokens fuera de la URL, validación de unicidad,
control de acceso por rol/owner, separación prod/staging, captcha verificado en servidor.

## Mapeo de endpoints legacy → API nueva

| Legacy (PHP)                         | Nuevo (ASP.NET Core)                    |
|--------------------------------------|-----------------------------------------|
| `control-login.php`                  | `POST /api/auth/login` (+recaptcha)     |
| `control-registro.php`               | `POST /api/auth/register`               |
| `config/user-logout.php`             | `POST /api/auth/logout`                 |
| `control-json-citas.php` (todo)      | `GET /api/citas?from&to` (paginado)     |
| `control-crear-cita(.php/-calendario)`| `POST /api/recetarios` / `POST /api/citas` |
| `control-editar-cita-calendario.php` | `PUT /api/citas/{id}`                   |
| `control-cancel-cita.php`            | `POST /api/citas/{id}/cancel`           |
| `control-get-horarios.php`           | `GET /api/horarios?fecha`               |
| `recetario/?JWT&Tok&Id`              | `GET /api/recetarios/{id}` (auth)       |
| `receta-digital/?JWT&Tok&Id`         | `GET /api/receta-digital/{token}` (público, expira) |

## Artefactos del scrape (insumos)
`~/Desktop/aro3d-scrape/` → `data/` (datos), `docs/` (ENDPOINTS, APP, FRONTEND, AUTH-FLOW,
PROBLEMAS, este plan), `scripts/` (scraper re-ejecutable).
