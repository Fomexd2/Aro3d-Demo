# Cómo iniciar sesión (procedimiento — SIN credenciales aquí)

> Este archivo describe los **pasos**. NO contiene usuarios ni contraseñas, a propósito.
> Guarda tus credenciales en tu **gestor de contraseñas** (Keychain, 1Password, Bitwarden…),
> no en un archivo de texto.

## Inicio de sesión manual (lo haces tú, en el navegador)

| Rol | URL |
|-----|-----|
| Admin / Laboratorio | https://aro3d.com/mi-nube-aro/login/ |
| Doctor | https://aro3d.com/mi-nube-aro/login/doctor/ |
| Paciente | https://aro3d.com/mi-nube-aro/login/paciente/ |

Campos: **Email o Teléfono** + **Contraseña** → entra. (Recuperar contraseña: link en la
misma página → solo Email.)

## Para que Claude explore un panel
1. Inicia sesión tú en una pestaña de Chrome con el rol que quieras (doctor/paciente).
2. Avisa a Claude. Claude trabaja **dentro de tu sesión ya abierta** — nunca ve ni teclea
   tu contraseña.

## Refrescar las cookies del scraper (cuando caduquen)
El scraper (`scripts/scrape.sh`) usa cookies de sesión guardadas en `scripts/cookies.env`
(ignorado por git). Si caduca, estando logueado en Chrome:
DevTools (F12) → Application → Cookies → `https://aro3d.com` → copia
`iduser, jwt, jwtbd, phpsessid` a `scripts/cookies.env`.

> Las cookies de sesión son sensibles (dan acceso a la cuenta). Trátalas como una contraseña:
> no las subas a repos, no las compartas.
