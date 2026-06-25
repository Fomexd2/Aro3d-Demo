# Front-end de aro3d — cómo está construido (base para reescribir en Flutter)

> Capturado interactuando con la app logueado como **EDWIN OMAR RIVERA CORTES** (`iduser=12190`),
> en viewport **móvil (~400px)**. La app es **mobile-first responsive**, ideal para Flutter.

## 0. Son DOS front-ends distintos

| | Sitio público `aro3d.com` | Panel `Mi Nube Aro` `/mi-nube-aro/` |
|--|--|--|
| Marca | **ARO – Apoyo Radiológico Oral 3D** | "Mi Nube Aro" (logo nube) |
| Color | **Teal/verde salvia** (~`#8FB4AC`) hero | **Navy** `#182132` + acento **ámbar** `#FCB92C` |
| Rol | Marketing + receta digital + agendar cita (paciente) | Gestión interna (lab/admin): calendario, recetarios |
| Tipo | Sitio tipo WordPress | Plantilla admin tipo *Skote/Minible* (Bootstrap 4) |

Negocio: laboratorio de **radiología/ortodoncia dental 3D** en Cuernavaca, Morelos
(Plaza Médica Lomas; WhatsApp 777 716 6666).

## 1. Design tokens

**Panel admin (Mi Nube Aro)**
- Fondo `#F1F5F7` · texto `#505D69` · fuente **Nunito** (base 14.4px)
- Sidebar navy `#182132` (240px en desktop), texto `#D7E4EC`; topbar blanca, alto 70px
- Tarjetas: blancas, `border-radius: 4px`, sombra `0 2px 4px rgba(0,0,0,.08)`
- Botón primario/acento: **ámbar `#FCB92C`**, texto blanco, `radius 4px`
- Eventos del calendario: bloques **rojo salmón** (~`#e15b53`)
- **Móvil:** topbar navy con logo nube + hamburguesa **"MENÚ"**; contenido en una columna
  centrada; título de página **negro, grande, mayúsculas** (~40px, ej. "CALENDARIO DE CITAS")

**Sitio público (ARO)**
- Hero **teal** con logo "ARO / APOYO RADIOLÓGICO ORAL 3D" en blanco + hamburguesa
- Tarjeta blanca con barra de acento verde arriba; labels en **MAYÚSCULAS** (PACIENTE, EDAD…)
- Inputs con relleno gris claro, bordes redondeados; texto de ayuda en gris pequeño

## 2. Navegación

**Panel (menú lateral / hamburguesa):**
`Estatus de Citas` → `/mi-nube-aro/recetarios/` ·
`Calendario de Citas` → `/mi-nube-aro/calendario-de-citas/` ·
`Doctores` → `/mi-nube-aro/expediente/doctores` (roto/vacío) ·
`Pacientes` → `/mi-nube-aro/expediente/pacientes` (roto/vacío) ·
`Cerrar Sesión` → `/config/user-logout.php`

**Público:** `Inicio` · `Servicios`▾ (Tomografía 3D, Radiología 2D, Escáner Intraoral 3D,
Fotografía Clínica, Estudio Ortodóntico Completo, Impresión 3D) · `Receta Digital` ·
`Agendar Cita` (= misma página que Receta Digital) · `Contacto` · `Mi Nube Aro`

## 3. Pantallas del panel

### 3.1 Calendario de Citas (pantalla central)
- **Buscador** arriba: inputs Paciente / Correo / Teléfono / Doctor + botón **Buscar** (ámbar).
- **FullCalendar 5.10.1**: vistas **Mes / Semana / Día / Agenda**; nav Hoy / Día antes / Día siguiente.
  Vista Día = rejilla de 30 min (09:00–19:00) + fila "Todo el día". Citas = bloques salmón
  con `HH:MM - HH:MM` + nombre del paciente.
- Panel lateral "**Ver Todo**" con recetarios **Pendientes** (lista).
- **Modales** (todos embebidos en la página):

| Modal (id) | Título | Contenido |
|--|--|--|
| `ModalOkayView` | **Detalle de Cita** | Solo lectura: Paciente, Edad, Fecha Nac., Correo/Tel. paciente, Doctor, Email/Tel. doctor, Fecha, Hora Inicio/Fin, Aparato, Tiempo, Fecha de Alta, Monto Total, Email Envió, Registrado Por, Folio, Observaciones, Estudios Solicitados. Botones: Regresar / Cancelar Cita / Editar Cita |
| `AddEvento` | **Agregar Cita** | Form grande (ver 3.1.1) |
| `ModalEditForm` | **Editar Cita** | Igual que Agregar, precargado. Guardar |
| `ModalOkHorario` | **Horario de Cita** | Fecha (datepicker) + Hora (select) + checkbox "Enviar correo al paciente" + **Agendar** |
| `ModalCancelCita` | **Cancelar Cita** | Textarea "Motivo de Cancelación" |
| `ModalOkayCita`, `OkayCitaSend` | — | Confirmaciones "Ok" |

#### 3.1.1 Form "Agregar Cita" (= crear recetario) — el flujo de captura clave
Campos (label → name):
- Fecha de Inicio* `FechaInicio` (datepicker, ph `2020-01-01`) · Fecha de Fin* `FechaFin`
- Hora de Inicio* `HoraInicio` (time) · Hora de Fin* `HoraFin` (time)
- **Selecciona un Paciente** `Paciente` (select buscable: existentes `NOMBRE | email`, o
  "Agregar Nuevo Paciente" → `NombrePax`, `FecNac` (dd-mm-yyyy), `EmailPax`, `PhonePax`)
- **Selecciona un Doctor** `Doctor` (select: existentes, o "Agregar Nuevo Doctor" →
  `NombreDoc`, `EmailDoc`, `PhoneDoc`, `ClinicaDoc`)
- **Selecciona una Clínica** `Clinica` (select, o "Agregar Nueva Clínica" → `NombreClin`)
- **Catálogo de Servicios/Estudios** `ListaServicios[]` (checkbox por estudio) con sub-opciones
  `Options[n]` (checkbox) y `TxtServicio[n]` (texto) — ver §5.
- Observaciones · Descuento · Total · botón **Guardar**

### 3.2 Estatus de Citas (`/recetarios/`)
DataTable (DataTables 1.12.1, ES, paginado en cliente). Columnas:
`No. | Paciente | Teléfono | Email | Doctor | Clínica | Fecha de Cita | Estatus | Fecha de Alta | acciones`.
Acciones por fila → `recetario/?JWT&Tok&Id` (ver/editar), `receta-digital/?JWT&Tok&Id`,
y "Eliminar Recetario" (con confirmación). Estatus: **Con Cita / Por Confirmar / Cancelado / Completo**.

### 3.3 Doctores / Pacientes (`/expediente/...`)
DataTables vacías/rotas para esta cuenta (redirigen a login vía curl, error en navegador).
Marcar para rehacer en la migración.

## 4. Pantallas públicas

### 4.1 Receta Virtual / Agendar Cita (`/receta-digital/?JWT&Tok&Id`)
Página **pública por token** (la abre el paciente). Hero teal "RECETA VIRTUAL".
Form (labels en mayúsculas): PACIENTE, EDAD (años), TELÉFONO, FECHA DE NACIMIENTO (dd-mm-yyyy),
CORREO ELECTRÓNICO, DOCTOR(A), CLÍNICA (opcional), CORREO CLÍNICA, FORMATO DE ENTREGA (USB…),
y selección de **paquetes/estudios** (§5). Estado de éxito: "**¡Listo tu receta ha sido enviada!**".

## 5. Catálogo de estudios y paquetes (dominio)

- **Estudio Ortodóntico ARO** incluye: Ortopantomografía (Panorámica), Lateral de Cráneo con
  Cefalometría(s), Fotografías Clínicas (intraorales/extraorales), Escaneo Intraoral.
- **Cefalometrías** (análisis): Ricketts · Steiner · Jarabak · Alexander.
- **Fotografías:** Boca Abierta / Boca Cerrada · Visor · Dicom.
- **Escaneo/Tomografía:** Maxila · Mandíbula · Cone Beam · Visor · Dicom.
- **Paquetes:** PAQ 1 Digital · PAQ 2 ARO Plus (modelos impresos) · PAQ 3 ARO 3D (cone beam) ·
  PAQ 4 ARO 3D Plus · PAQ 5 ARO-ATM · PAQ 6 ARO Platinum (korkhaus + análisis frontal/lateral/dental).
- Otros servicios: Impresión 3D, entrega en USB.

## 6. Stack front actual
jQuery + Bootstrap 4, FullCalendar 5.10.1, DataTables 1.12.1, bootstrap-select, chosen,
bootstrap-datepicker, parsley (validación), moment.js, jquery.mask, easyAutocomplete.
Plantilla admin *Skote/Minible*. Render server-side con datos embebidos (no SPA, no API JSON limpia).

## 7. Mapeo a Flutter (guía para cuando se pida el código — aún NO generado)

- **Tema:** `ColorScheme.fromSeed(seedColor: Color(0xFFFCB92C))`, surface `#F1F5F7`,
  fuente Nunito (`google_fonts`). Sub-tema público teal `#8FB4AC`. Material 3.
- **Navegación:** `NavigationDrawer` (móvil) / `NavigationRail` (tablet), `go_router`.
- **Calendario:** `syncfusion_flutter_calendar` o `table_calendar` (mes/semana/día/agenda).
- **Listas grandes (recetarios):** `ListView.builder` + **paginación server-side** + búsqueda
  (no traer 10k de golpe como hoy).
- **Formularios:** `Form` + `TextFormField`; typeahead para Paciente/Doctor
  (`flutter_typeahead`); `CheckboxListTile` para estudios; `showDatePicker`/`showTimePicker`.
- **Modales:** `showModalBottomSheet` full-screen (móvil) / `showDialog` (tablet).
- **Receta digital:** pantalla read-only con branding teal, accesible por token/deep-link.
- **Feedback:** `SnackBar`/`Dialog` para las confirmaciones "Ok".
- **Estados de recetario** (Por Confirmar→Con Cita→Completo/Cancelado): `enum` + chips de color.
