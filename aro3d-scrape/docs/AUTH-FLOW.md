# Flujo de autenticación — 3 roles (Admin / Doctor / Paciente)

> Mapeado inspeccionando los formularios **sin enviar credenciales** (no puedo teclear
> contraseñas) y **sin cerrar la sesión admin viva** (el logout la invalidaría y no podría
> volver a entrar). Es suficiente para reimplementarlo en la migración.

## Roles

| Rol | Código `Tipo`/`TipoUser` | Entra por | Se crea por |
|-----|--------------------------|-----------|-------------|
| Paciente | **1** (`id=SoyPaciente`) | `/mi-nube-aro/login/paciente/` | Registro público |
| Doctor   | **2** (`id=SoyDoctor`)   | `/mi-nube-aro/login/doctor/`   | Registro público |
| Admin / Laboratorio | (otro, interno) | `/mi-nube-aro/login/` | Internamente (no por registro) |

El registro público solo ofrece **Doctor (2)** o **Paciente (1)**. El admin (ej. EDWIN OMAR
RIVERA CORTES, `iduser=12190`) se da de alta por dentro.

## reCAPTCHA (en TODOS los logins y el registro)

El login del **sitio principal** es el mismo de Mi Nube Aro (la home `aro3d.com` solo enlaza a
`mi-nube-aro/`). Protegido con **Google reCAPTCHA v2 "No soy un robot"** (checkbox visible):

```html
<div class="g-recaptcha d-flex justify-content-center align-items-center"
     id="reCAPTCHA"
     data-sitekey="6Lcg-lsbAAAAAKTKMCaWzwIiTBaBO9UUn9pataM8"
     data-callback="imNotARobot">
```
- Callback JS `imNotARobot` (habilita el envío al marcar el check). `grecaptcha.reset()` ante error.
- Por esto **no se puede automatizar el login** (resolver captchas está prohibido; el usuario lo confirmó).
- La página de login usa la **plantilla del sitio público ARO** (header/footer del sitio), no el
  tema navy del panel. Copy: título "**Bienvenido**", botón "**Entrar**". El login de Doctor añade
  el subtítulo "Aquí encontrarás los estudios de todos tus pacientes".

> Migración: conservar un captcha (reCAPTCHA v2/v3 o hCaptcha/Turnstile) en login y registro;
> verificar el token del lado servidor antes de autenticar.

## Login  — `controladores/control-login.php` (POST, vía AJAX; `action=""` + JS)

Form `#FormLogin` (mismo en los 3, cambia el `Tipo`):
```
Email     (text)     -> "Correo electrónico / Teléfono"  (acepta email O teléfono)
Password  (password) -> "Contraseña"
Token     (hidden)   -> #TokenLogin   (CSRF, lo setea el JS)
Id        (hidden)   -> #IdLogin
Tipo      (hidden)   -> #RegTipo       (rol: 1/2/admin, según la página)
Save      (hidden)   = "Ok"
```
Éxito → el servidor setea las cookies de sesión **`iduser`, `jwt`, `jwtbd`, `phpsessid`**
y redirige al panel correspondiente al rol.

## Recuperar contraseña  — mismo `control-login.php`
Segundo form en las páginas de login:
```
Email     (email)
Recovery  (hidden)   # marca el modo "recuperación"
```

## Registro  — `controladores/control-registro.php` (POST)
```
Nombre        (text)  -> "Nombre Completo"
TipoUser      (radio) -> 1=Paciente / 2=Doctor
Email         (email)
Phone         (text)  -> "Número teléfonico"
Password      (password)
ConfirmaPass  (password)
Token         (hidden, CSRF)
```

> **El registro alimenta los catálogos** (verificado en vivo, solo lectura): dar de alta por
> `control-registro.php` crea la **cuenta de login** Y una **entrada de catálogo**
> (Doctor → catálogo Doctor; Paciente → catálogo Paciente), que luego aparece en el form
> "Agregar Cita". Ejemplo de prueba del usuario: doctor `Edwin Testing | fomemym@gmail.com`
> y paciente `Edwin Testing paciente | edwinrivera9802@gmail.com`.
> **Sin unicidad:** el mismo correo se acepta en varias cuentas/roles (ver `docs/PROBLEMAS.md` #15).

## Logout — `config/user-logout.php` (GET)
Link "Cerrar Sesión" del menú. Destruye la sesión PHP + limpia cookies y redirige al login.
**No ejecutado** para no matar la sesión admin activa (no hay forma de re-loguear sin teclear la contraseña).

## Qué ve cada rol después de entrar (lo confirmado / lo inferido)

- **Admin:** panel completo — Calendario de Citas, Estatus de Citas (recetarios), Doctores,
  Pacientes, Cerrar Sesión. (Confirmado, es la sesión actual.)
- **Paciente:** ✅ CONFIRMADO (sesión `Edwin Testing Paciente`, Id 12199). **Portal de auto-servicio
  mínimo**, login redirige a `/mi-nube-aro/datos-del-paciente/`. Solo 2 secciones + Cerrar Sesión:
  - **Datos del Paciente** (`/datos-del-paciente/`): form de perfil (Nombre, Email, Teléfono,
    FecNac, Edad) + **Actualizar Contraseña** (Password/PasswordOk) + Guardar.
  - **Mis Estudios** (`/mis-estudios/`): DataTable `Visualizar Estudio | Paciente | Estudio | Fecha`
    (solo SUS estudios; acción para ver/descargar el estudio).
  - **No** tiene calendario ni gestión de recetarios. El "Agendar Cita" del paciente vive en el
    **sitio público** (`/receta-digital/`), no en este portal.
- **Doctor:** ✅ CONFIRMADO (sesión `Doctor Edwin Testing`). Panel propio (desktop: sidebar PERFIL
  + avatar), login redirige a `/mi-nube-aro/mis-pacientes/`. Menú: Mis Pacientes · Receta Digital ·
  Estatus de Citas · Datos del Doctor · Cerrar Sesión. **No tiene Calendario.**
  - **Mis Pacientes** (`/mis-pacientes/`): DataTable `Ver Archivos | Nombre | Teléfono | Email | Edad`,
    **scopeado a SUS pacientes** (mostró 3, todos "Edwin Testing"). Acción "Ver Archivos" (estudios).
  - **Receta Digital** → `/receta-digital/` (público): el form RECETA VIRTUAL para **crear/enviar**
    la receta al paciente (datos paciente + paquetes/estudios PAQ1–6).
  - **Estatus de Citas** (`/recetarios/`): **buscador** (Paciente/Correo/Tel/Doctor/Clínica/Estatus
    + rango de fechas, default semana actual), tabla **vacía hasta buscar** — NO precarga los 60 MB
    como el admin.
  - **Datos del Doctor** (`/datos-del-doctor/`): perfil (Nombre, Email, Teléfono, FecNac, Edad,
    **Área de Preferencia** [especialidad], **Nombre/Email de Clínica**) + Actualizar Contraseña.

## Los 3 roles mapeados — comparación (clave para la migración)
| | Admin | Doctor | Paciente |
|--|--|--|--|
| Landing | Calendario de Citas | Mis Pacientes | Datos del Paciente |
| Menú | Estatus de Citas, **Calendario**, Doctores, Pacientes | Mis Pacientes, Receta Digital, Estatus de Citas, Datos del Doctor | Datos del Paciente, Mis Estudios |
| Calendario | ✅ (ve TODO) | ❌ | ❌ |
| Recetarios | precarga TODOS (~60 MB) | buscador, scopeado | — |
| Alcance datos | global | sus pacientes | solo él |

> **Inconsistencia de scoping** (para arreglar): "Mis Pacientes" del doctor sí está scopeado, pero
> `control-json-citas.php` (feed del calendario) devuelve TODO sin filtrar por rol, y la lista lateral
> de pendientes del doctor parece mostrar recetarios de todos. Falta control de acceso uniforme por rol/owner.

## Notas para la migración (auth)
- Unificar a **un solo flujo** con `Tipo`/rol como claim del JWT (admin/doctor/paciente),
  un solo `control-login` → emitir **JWT firmado + refresh token** en cookie `HttpOnly`+`Secure`.
- Login por email **o** teléfono: normalizar identificador.
- Mantener recuperación de contraseña y registro (solo doctor/paciente).
- Quitar `iduser` de cookie (manipulable) → derivarlo del token.
