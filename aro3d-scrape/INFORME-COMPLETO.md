# aro3d / Mi Nube Aro — Informe completo (arquitectura, flujos y migración)

> Documento consolidado del análisis de **aro3d.com** y su panel **Mi Nube Aro**, hecho
> scrapeando datos e **interactuando con la app en modo lectura** (sin editar, agendar ni enviar).
> Objetivo: base para migrar a **C# (ASP.NET Core) + Flutter**.
> Fecha: 2026-06-23 · Cuenta admin observada: EDWIN OMAR RIVERA CORTES (iduser 12190).
> Detalle por tema en `docs/` (ENDPOINTS, APP, FRONTEND, AUTH-FLOW, PROBLEMAS, PLAN-MIGRACION).

## Índice
1. Resumen ejecutivo
2. Negocio y dominio
3. Arquitectura general
4. Stack tecnológico actual
5. Autenticación y los 3 roles
6. Flujo por rol (Admin / Doctor / Paciente)
7. Flujo de negocio end-to-end
8. Modelo de datos
9. Catálogo de estudios y paquetes
10. Endpoints
11. ⚠️ Errores graves → qué se arregla en la migración
12. Datos extraídos (inventario del scrape)

---

## 1. Resumen ejecutivo
ARO ("Apoyo Radiológico Oral 3D") es un **laboratorio de radiología/ortodoncia dental 3D** en
Cuernavaca, Morelos. El sistema tiene **dos front-ends**: un **sitio público** (marketing + receta
digital del paciente) y un **panel interno "Mi Nube Aro"** (gestión de recetarios y citas), sobre un
backend **PHP + MySQL** sin capa de API. Funciona, pero arrastra problemas serios de **seguridad,
rendimiento e integridad de datos** (sin paginación, PII expuesta, tokens en la URL, sin control de
acceso por rol consistente, sin validación de duplicados). La migración a **ASP.NET Core + Flutter**
es la oportunidad para corregirlos (§11).

## 2. Negocio y dominio
- **Recetario**: orden de estudios radiológicos que un **doctor** solicita al laboratorio para un
  **paciente**. Es la entidad central.
- **Cita**: agenda del recetario (fecha/hora, duración). 0..1 por recetario.
- **Receta digital**: vista pública (por token) que recibe el paciente con su receta y desde la que
  puede confirmar/agendar.
- **Actores**: Laboratorio/Admin, Doctor, Paciente.
- Contacto del negocio: Plaza Médica Lomas, Cuernavaca; WhatsApp 777 716 6666.

## 3. Arquitectura general
```
                 ┌───────────────────────────┐   ┌───────────────────────────┐
   Paciente ───► │  Sitio público aro3d.com  │   │  Panel Mi Nube Aro        │ ◄── Admin / Doctor
                 │  (marca teal · marketing) │   │  (plantilla admin navy)   │
                 │  Receta Digital/Agendar   │   │  calendario · recetarios  │
                 └────────────┬──────────────┘   └────────────┬──────────────┘
                              └──────────────┬─────────────────┘
                              ┌──────────────▼───────────────┐
                              │  Auth: control-login.php       │  (email/tel + pass + reCAPTCHA v2)
                              │  cookies: iduser/jwt/jwtbd/php… │
                              └──────────────┬───────────────┘
                              ┌──────────────▼───────────────┐
                              │  Backend PHP: controladores/*  │  (POST, sin capa de servicios)
                              └──────────────┬───────────────┘
                              ┌──────────────▼───────────────┐
                              │  MySQL  (recetarios, citas,    │
                              │  pacientes, doctores, clínicas)│
                              └────────────────────────────────┘
```
Render **server-side con datos embebidos** (no es SPA, no hay API REST). El diagrama visual completo
se entregó aparte (SVG en el chat).

## 4. Stack tecnológico actual
- **Backend**: PHP sobre OpenLiteSpeed/CyberPanel + MySQL/MariaDB. Lógica en `/controladores/*.php`,
  config en `/config/`, vistas en `/mi-nube-aro/`.
- **Front**: jQuery + Bootstrap 4 (plantilla admin *Skote/Minible*), FullCalendar 5.10.1,
  DataTables 1.12.1, bootstrap-select, chosen, bootstrap-datepicker, parsley, moment.js, jquery.mask.
- **Diseño**: mobile-first responsive. Panel = navy `#182132` + acento ámbar `#FCB92C`, fondo
  `#F1F5F7`, fuente Nunito. Sitio público + receta digital = teal `#8FB4AC`.

## 5. Autenticación y los 3 roles
- **Login** (`controladores/control-login.php`, POST): `Email` (correo **o** teléfono) + `Password`
  + `Token` (CSRF) + `Tipo` (rol) + `Save`. Protegido con **reCAPTCHA v2 "no soy un robot"**
  (sitekey `6Lcg-lsbAAAAAKTKMCaWzwIiTBaBO9UUn9pataM8`). 3 entradas: `/login/` (admin),
  `/login/doctor/`, `/login/paciente/`.
- **Roles** (`Tipo`/`TipoUser`): **1 = Paciente**, **2 = Doctor**, **admin = interno**.
- **Registro** (`control-registro.php`): Nombre, TipoUser (1/2), Email, Phone, Password, ConfirmaPass.
  Crea **cuenta de login Y entrada de catálogo** (Doctor→catálogo Doctor, Paciente→catálogo Paciente).
- **Recuperación**: mismo `control-login.php` con flag `Recovery` + Email.
- **Logout**: `config/user-logout.php`.
- Acceso a recetarios/recetas individuales por **token en query string**: `?JWT=…&Tok=…&Id=…`.

## 6. Flujo por rol

### 6.1 Admin / Laboratorio  (landing: Calendario de Citas)
Menú: **Estatus de Citas · Calendario de Citas · Doctores · Pacientes · Cerrar Sesión**.
- **Calendario** (FullCalendar, vistas Mes/Semana/Día/Agenda): ve **TODAS** las citas (bloques
  salmón). Modales: Detalle de Cita (lectura), **Agregar Cita** (= crear recetario completo:
  fecha/hora + paciente/doctor/clínica con select o "agregar nuevo" + catálogo de estudios +
  observaciones/descuento/total), Editar, Horario (reagendar + avisar por correo), Cancelar (motivo).
- **Estatus de Citas** (`/recetarios/`): **precarga TODOS** los recetarios (~10k, ~60 MB de HTML).
- **Doctores / Pacientes** (`/expediente/*`): hoy **rotas/vacías**.
- **Alcance: global** (ve todo).

### 6.2 Doctor  (landing: Mis Pacientes)
Menú: **Mis Pacientes · Receta Digital · Estatus de Citas · Datos del Doctor · Cerrar Sesión**.
**No tiene Calendario.**
- **Mis Pacientes** (`/mis-pacientes/`): DataTable `Ver Archivos | Nombre | Teléfono | Email | Edad`,
  **scopeado a SUS pacientes**. "Ver Archivos" → estudios del paciente.
- **Receta Digital** → `/receta-digital/` (público): form RECETA VIRTUAL para **crear/enviar** la
  receta al paciente (datos del paciente + paquetes/estudios).
- **Estatus de Citas** (`/recetarios/`): **buscador** (filtros + rango de fechas, default semana
  actual), tabla **vacía hasta buscar** — NO precarga todo como el admin.
- **Datos del Doctor** (`/datos-del-doctor/`): perfil (incluye **Área de Preferencia** y **Clínica**)
  + cambiar contraseña.
- **Alcance: sus pacientes.**

### 6.3 Paciente  (landing: Datos del Paciente)
Menú: **Datos del Paciente · Mis Estudios · Cerrar Sesión**. Portal de **auto-servicio**.
- **Datos del Paciente** (`/datos-del-paciente/`): perfil (Nombre, Email, Teléfono, FecNac, Edad)
  + Actualizar Contraseña.
- **Mis Estudios** (`/mis-estudios/`): DataTable `Visualizar Estudio | Paciente | Estudio | Fecha`
  con **solo SUS estudios** (acción para ver/descargar).
- **No** agenda dentro del portal: el "Agendar Cita" del paciente vive en el sitio público.
- **Alcance: solo él.**

## 7. Flujo de negocio end-to-end
1. **Doctor** (o admin) crea el **recetario**: elige/da de alta paciente, doctor y clínica, marca los
   **estudios** y observaciones/monto. (`Agregar Cita` / `Receta Digital`).
2. El sistema **envía la receta digital** al paciente por correo (link con token).
3. **Paciente** abre `/receta-digital/?JWT&Tok&Id`, ve su receta y **agenda/confirma** la cita.
4. El laboratorio realiza los estudios; el paciente los consulta en **Mis Estudios**; el doctor en
   **Ver Archivos** de Mis Pacientes.
5. **Estatus del recetario**: Por Confirmar → Con Cita → Completo / Cancelado.

## 8. Modelo de datos (inferido, para normalizar)
```
Usuario(id, rol{admin|doctor|paciente}, email, telefono, passwordHash)
Doctor(id, nombre, email, telefono, areaPreferencia, clinicaId?)
Paciente(id, nombre, email, telefono, fechaNac, edad)
Clinica(id, nombre, email)
Recetario(id, pacienteId, doctorId, clinicaId?, monto, descuento, observaciones,
          estatus{PorConfirmar|ConCita|Completo|Cancelado}, fechaAlta, adminId)
  └─< RecetarioEstudio(recetarioId, estudioId, opciones)
  └─o Cita(id, recetarioId, inicio, fin, duracionMin, estatus)
Estudio(id, nombre)        Paquete(id, nombre, estudios[])
```
Hoy Paciente/Doctor/Clínica viven como **texto libre** dentro del recetario, sin tablas normalizadas
ni FKs. La migración debe extraerlos a entidades propias.

## 9. Catálogo de estudios y paquetes
- **Estudio Ortodóntico ARO**: Ortopantomografía (Panorámica), Lateral de Cráneo con Cefalometría,
  Fotografías Clínicas (intra/extraorales), Escaneo Intraoral.
- **Cefalometrías**: Ricketts · Steiner · Jarabak · Alexander.
- **Fotografías**: Boca Abierta/Cerrada · Visor · Dicom. **Escaneo/Tomografía**: Maxila · Mandíbula ·
  Cone Beam · Visor · Dicom.
- **Paquetes**: PAQ 1 Digital · PAQ 2 ARO Plus · PAQ 3 ARO 3D · PAQ 4 ARO 3D Plus · PAQ 5 ARO-ATM ·
  PAQ 6 ARO Platinum. Otros: Impresión 3D, entrega en USB.

## 10. Endpoints
| Tipo | Ruta | Notas |
|------|------|-------|
| Página | `/mi-nube-aro/calendario-de-citas/` | Calendario (admin/doctor) |
| Página | `/mi-nube-aro/recetarios/` | Recetarios: admin precarga todo; doctor buscador |
| Página | `/mi-nube-aro/mis-pacientes/` | Doctor: sus pacientes |
| Página | `/mi-nube-aro/mis-estudios/` | Paciente: sus estudios |
| Página | `/mi-nube-aro/datos-del-doctor/` · `/datos-del-paciente/` | Perfiles |
| Página | `/receta-digital/?JWT&Tok&Id` | Receta virtual (público por token) |
| Auth | `controladores/control-login.php` | Login (email/tel + pass + reCAPTCHA + Tipo) |
| Auth | `controladores/control-registro.php` | Registro (doctor/paciente) |
| Auth | `config/user-logout.php` | Logout |
| API | `controladores/control-json-citas.php` | Feed calendario — **devuelve TODO, ignora rango** |
| API | `control-crear-cita.php` · `control-crear-cita-calendario.php` | Crear |
| API | `control-editar-cita-calendario.php` · `control-cancel-cita.php` | Editar / cancelar |
| API | `control-get-horarios.php` | Horarios disponibles |

## 11. ⚠️ Errores graves → qué se arregla en la migración

| # | Severidad | Problema (confirmado) | Fix en la migración (C#/Flutter) |
|---|-----------|------------------------|----------------------------------|
| 1 | **CRÍTICO** | `control-json-citas.php` devuelve **9 759 registros con PII de pacientes en una sola respuesta (~11 MB)** e **ignora el rango de fechas**; lo carga cada vez que se abre el calendario. | API paginada + filtrado real por fecha en servidor; exponer solo campos necesarios. |
| 2 | **CRÍTICO** | **Sin control de acceso por rol consistente**: el feed de citas devuelve **TODO sin filtrar por doctor** (un doctor podría ver pacientes de otros). "Mis Pacientes" sí scopea, pero el feed no. | Autorización por rol/owner en **cada** endpoint; claims en el JWT; pruebas de scoping. |
| 3 | **CRÍTICO** | **Tokens JWT en la query string** (`/receta-digital/?JWT=…&Tok=…`): quedan en logs, historial, referer y caché; reenviables. | Token en cookie `HttpOnly`+`Secure` o link de **un solo uso con expiración**; verificación server-side. |
| 4 | **ALTO** | **Sin validación de unicidad**: 220 pacientes y 2 doctores duplicados por nombre+email; mismo correo reusable en varias cuentas/roles (caso "Edwin Testing" con 4 correos). | `UNIQUE` en BD (email/teléfono normalizados) + buscar-y-reutilizar en el alta + merge de históricos. |
| 5 | **ALTO** | **Página de recetarios = ~60 MB de HTML** (admin precarga ~10k filas sin paginación server-side). | Lista virtualizada + endpoint paginado/ordenable/buscable. |
| 6 | **ALTO** | **Cookies de sesión legacy solapadas** (`iduser`, `jwt`, `jwtbd`, `phpsessid`); `iduser` en cookie es manipulable. | Un solo esquema **JWT firmado + refresh token**; rol como claim; quitar `iduser` de cookie. |
| 7 | **MEDIO** | **Semántica HTTP rota**: endpoints responden **`302` pero con el body completo** (rompe clientes con redirect). | `200 application/json`. |
| 8 | **MEDIO** | **Calidad de datos**: Doctor/Clínica **texto libre**, fechas en formatos inconsistentes (`25 / Junio / 2026` vs ISO), HTML embebido en campos (`Estudios`). | Entidades con FK; `DateTime`/ISO-8601; separar datos de presentación. |
| 9 | **MEDIO** | **Datos de PRUEBA/TEST en producción** ("…OLIVARES PRUEBA" ×5, "Oscar Prueba", etc.). | Separar entornos prod/staging; semilla de prueba aparte. |
| 10 | **MEDIO** | **Sin capa de API ni de servicios**: HTML y datos acoplados; lógica en `controladores/*.php` sueltos. | Arquitectura por capas (Controllers → Services → Repositories → EF Core) + API REST + cliente Flutter desacoplado. |
| 11 | **BAJO** | Secciones `/expediente/doctores` y `/pacientes` **rotas/vacías**. | Rehacer como módulos CRUD reales. |

## 12. Datos extraídos (inventario del scrape)
- `data/citas.json` / `citas.csv` — **9 759 citas** (2022-05-30 → 2026-07-06).
- `data/recetarios.json` / `recetarios.csv` — **10 058 recetarios** (Con Cita 9 327 · Por Confirmar
  511 · Cancelado 219 · Completo 1).
- `scripts/scrape.sh` — scraper re-ejecutable (curl + cookies + parsers). Cookies en `cookies.env`.
- ⚠️ `data/` contiene **PII de pacientes**: tratar como sensible (no repos públicos).

> **Plan de migración detallado** (fases + mapeo de endpoints legacy→API): `docs/PLAN-MIGRACION.md`.
