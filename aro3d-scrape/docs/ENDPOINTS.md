# Endpoints de aro3d.com / Mi Nube Aro

> Base: `https://aro3d.com` · Área autenticada: `/mi-nube-aro/` · Backend PHP.
> Auth por cookies (ver `docs/APP.md`).

## Páginas (HTML server-rendered)

| Ruta | Qué es | Notas |
|------|--------|-------|
| `/mi-nube-aro/` | Landing / chooser de login | Pública. Links a login doctor/paciente y registro. |
| `/mi-nube-aro/login/`, `/login/doctor/`, `/login/paciente/` | Logins | — |
| `/mi-nube-aro/registro/` | Registro | — |
| `/mi-nube-aro/calendario-de-citas/` | **Calendario (FullCalendar)** | Eventos vía `control-json-citas.php`. Devuelve **302 + body** estando logueado. |
| `/mi-nube-aro/recetarios/` | **Listado de recetarios** (DataTable) | ~10k filas **embebidas en el HTML** (~60 MB). Sin paginación server-side. |
| `/mi-nube-aro/lista-de-recetarios/` | (ruta muerta) | Devuelve 302 sin contenido. |
| `/mi-nube-aro/lista-de-doctores/` | Lista de doctores (DataTable) | Vacía para la cuenta usada (`iduser=12190`). |
| `/mi-nube-aro/recetario/?JWT=…&Tok=…` | Ver/editar un recetario | Acceso por token en query string. ~2 links por fila. |
| `/receta-digital/?JWT=…&Tok=…` | Receta digital (pública por token) | 1 por recetario. |

## Controladores AJAX (`/controladores/*.php`)

| Endpoint | Método | Para qué | Confirmado |
|----------|--------|----------|------------|
| `control-json-citas.php` | POST `start`,`end` | Feed de eventos del calendario | ✅ Probado: devuelve **TODO** el histórico (9 759), **ignora `start`/`end`**. ~11 MB. HTTP 302 + body JSON. |
| `control-get-horarios.php` | (POST) | Horarios disponibles para agendar | Referenciado en calendario |
| `control-crear-cita.php` | POST | Crear cita (form) | Referenciado |
| `control-crear-cita-calendario.php` | POST | Crear cita desde el calendario | Referenciado |
| `control-editar-cita-calendario.php` | POST | Editar cita (drag/resize) | Referenciado |
| `control-cancel-cita.php` | POST | Cancelar cita | Referenciado |
| `config/user-logout.php` | GET | Cerrar sesión | Referenciado |

> Los controladores de creación/edición/cancelación no se ejecutaron (son de escritura).
> Sus parámetros exactos hay que confirmarlos inspeccionando el form/JS de la página
> de calendario o capturando la red al agendar una cita real.

## Rutas extra descubiertas al explorar el front

| Ruta | Qué es | Estado |
|------|--------|--------|
| `/mi-nube-aro/expediente/doctores` | Sección Doctores (menú) | 301/302 → login (curl) / error en navegador. **Roto o vacío** para esta cuenta. |
| `/mi-nube-aro/expediente/pacientes` | Sección Pacientes (menú) | Igual: roto/vacío. |
| `/receta-digital/?JWT&Tok&Id` | **Receta Virtual / Agendar Cita** (pública por token) | ✅ Funciona. Es del **sitio público** (marca teal ARO), no del panel. |
| `/mi-nube-aro/recetario/?JWT&Tok&Id` | Ver/editar recetario | El token scrapeado da "Esta página no funciona" (token caduco/single-use). |

### Sitio público `aro3d.com` (marca ARO, separado del panel)
`/` (Inicio) · `/servicios/` y subpáginas (`radiologia-dental-craneo-2d`, `escaner-intraoral-3d`,
`fotografia-clinica-dental`, `estudio-ortodontico-completo`, `impresion-3d`) ·
`/receta-digital/` (= Agendar Cita) · `/contactanos/` · `/mi-nube-aro/` (link al panel).

> Menú del panel (texto → ruta): Estatus de Citas → `/mi-nube-aro/recetarios/`,
> Calendario de Citas → `/mi-nube-aro/calendario-de-citas/`, Doctores/Pacientes → `/expediente/*`,
> Cerrar Sesión → `/config/user-logout.php`. Usuario logueado: **EDWIN OMAR RIVERA CORTES** (iduser 12190).

## Respuesta de `control-json-citas.php` (campos por evento)

```
id, Id_recetario, Id_recetario_editar (token),
Paciente, Email, Telefono, Edad, FechaNac,
Doctor, TelefonoDoc, EmailDoc,
ApartoNam (tipo de aparato), Tiempo, Token, Monto,
MailFecha, Estudios (HTML), Observaciones, NameAdmin, FechaAlta,
HorInicio, HorFin, FecInicio, FecFin,
start, end, title, backgroundColor, borderColor   <- formato FullCalendar
```
