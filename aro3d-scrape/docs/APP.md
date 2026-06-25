# Mi Nube Aro — Cómo funciona la app (para migración a C# + Flutter)

`aro3d.com` es el sitio de un **laboratorio de radiología / ortodoncia dental 3D**.
`Mi Nube Aro` (`/mi-nube-aro/`) es el **panel interno** donde se gestionan **recetarios**
(órdenes de estudio que un doctor manda al laboratorio para un paciente) y sus **citas**.

## Stack actual (legacy)

- **Backend:** PHP sobre OpenLiteSpeed / CyberPanel + MySQL/MariaDB.
  Lógica en `/controladores/*.php`, config en `/config/`, vistas en `/mi-nube-aro/`.
- **Frontend:** jQuery + Bootstrap (plantilla admin tipo "Minible/Skote"), con:
  FullCalendar 5.10.1, DataTables 1.12.1, bootstrap-select, bootstrap-datepicker,
  chosen, parsley (validación), moment.js, jquery.mask, easyAutocomplete.
- **Render:** HTML server-rendered con datos **embebidos** (no es SPA, no hay API REST limpia).

## Autenticación

- Por **cookies**: `iduser`, `jwt`, `jwtbd`, `phpsessid` (mezcla de sesión PHP + JWT propios).
- Acceso a recetarios/recetas individuales por **token en query string**:
  `?JWT=<base64>&Tok=<token>` → URLs compartibles/cacheables (ver PROBLEMAS).
- Hay 3 tipos de actor: **admin/laboratorio**, **doctor** y **paciente** (3 logins distintos).

## Módulos / dominio

1. **Recetarios** (núcleo). Una orden de estudio. Campos clave:
   `No (id)`, `Paciente`, `Telefono`, `Email`, `Doctor`, `Clinica`,
   `Fecha de Cita`, `Estatus`, `Fecha de Alta`, `Estudios`, `Monto`, `Observaciones`.
   - Estatus observados: **Con Cita** (9 327), **Por Confirmar** (511),
     **Cancelado** (219), **Completo** (1). Total **10 058**.
2. **Citas / Calendario**. Cada recetario puede tener una cita (fecha/hora, duración=`Tiempo`,
   `HorInicio`–`HorFin`). Gestionado con FullCalendar + controladores de cita.
   - **9 759 citas**, rango **2022-05-30 → 2026-07-06**.
   - Por año: 2022→383, 2023→2 120, 2024→3 029, 2025→2 731, 2026→1 496.
3. **Doctores**. Tabla de doctores (Nombre, Clinica, Email, Telefono, Estatus).
   En la cuenta scrapeada está vacía → el campo `Doctor` de los recetarios es **texto libre**
   (p.ej. "A QUIEN CORRESPONDA", "DENTARTE", "Roberto Alonso Peña Ramos").
4. **Estudios** (catálogo). Tipos de estudio radiológico que se piden en el recetario
   (Panorámica, Lateral de Cráneo con Cefalometría, Fotografías Clínicas, Escaneo Intraoral…).
5. **Receta digital**. Vista pública (por token) de la receta para el paciente.

## Modelo de datos inferido (para el rediseño)

```
Doctor (id, nombre, clinica, email, telefono, estatus)
  └─< Recetario (id, paciente{nombre,email,tel,edad,fechaNac}, doctorId|doctorTexto,
                 clinica, monto, observaciones, estatus, fechaAlta, adminId)
        ├─< RecetarioEstudio (recetarioId, estudioId)         # catálogo de estudios
        └─o Cita (id, recetarioId, inicio, fin, duracionMin, estatus)   # 0..1 por recetario
Estudio (id, nombre)
Paciente  # hoy embebido en el recetario; normalizar en la migración
```

> Nota: hoy Paciente/Doctor/Clínica viven como **texto dentro del recetario**, sin tablas
> normalizadas. La migración debería extraer Paciente, Doctor y Clínica a entidades propias.
