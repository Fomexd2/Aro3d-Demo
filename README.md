# Aro3d-Demo Migration

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
![HTML](https://img.shields.io/badge/HTML-99.9%25-orange)

> **Migración de Aro3d (Plataforma de Laboratorio Dental 3D) a moderna arquitectura con C# ASP.NET Core + Flutter**
>
> ## 📋 Descripción
>
> Este proyecto contiene la estrategia completa de migración de **Aro3d.com** (panel del laboratorio dental 3D "Mi Nube Aro") hacia una arquitectura moderna. Incluye:
>
> - 📊 **Extracción y análisis de datos** mediante web scraping del sistema legado
> - - 📄 **Documentación detallada** de endpoints, funcionamiento y problemas del sistema actual
>   - - 🔄 **Scripts reutilizables** para obtener datos de citas, recetarios y doctores
>     - - 📱 **Especificaciones técnicas** para la nueva implementación en ASP.NET Core + Flutter
>      
>       - ## 🏗️ Estructura del Proyecto
>      
>       - ```
>         aro3d-demo/
>         ├── aro3d-scrape/              # Módulo de web scraping y análisis
>         │   ├── data/                  # Datos extraídos (citas, recetarios, doctores)
>         │   ├── pages/                 # HTML descargado del sistema original
>         │   ├── scripts/               # Scripts de scraping y parsing
>         │   ├── docs/                  # Documentación técnica
>         │   └── README.md              # Guía detallada del scraping
>         ├── LICENSE                    # Apache 2.0
>         └── README.md                  # Este archivo
>         ```
>
> ## 🎯 Objetivo
>
> Migrar **Aro3d** desde su arquitectura monolítica actual a una solución moderna con:
>
> - **Backend:** C# con ASP.NET Core (API REST)
> - - **Frontend:** Flutter (multiplataforma: iOS, Android, Web)
>   - - **Base de datos:** Modernizada y optimizada para escalabilidad
>    
>     - ## 📊 Datos Disponibles
>    
>     - El proyecto incluye un dataset con:
>    
>     - | Dataset | Registros | Periodo |
> |---------|-----------|---------|
> | **Citas** | 9,759 | 2022-05-30 → 2026-07-06 |
> | **Recetarios** | 10,058 | Variado (estados: Confirmado, Por Confirmar, Cancelado) |
> | **Doctores** | 0* | - |
>
> *Tabla vacía en esta cuenta; "Doctor" es campo de texto libre en el recetario
>
> ## 🚀 Guía Rápida
>
> ### Explorar los Datos Extraídos
>
> ```bash
> cd aro3d-scrape
> ls -la data/          # Ver archivos de datos (JSON y CSV)
> ```
>
> ### Re-ejecutar el Web Scraping
>
> ```bash
> cd aro3d-scrape
> ./scripts/scrape.sh   # Descarga todo y parsea los datos
> ```
>
> **⚠️ Nota:** Si el script devuelve 0 registros o cae en login, las cookies de sesión caducaron. Actualiza `scripts/cookies.env` siguiendo las instrucciones del archivo.
>
> ## 📚 Documentación Técnica
>
> Dentro de `aro3d-scrape/docs/`:
>
> - **[ENDPOINTS.md](aro3d-scrape/docs/ENDPOINTS.md)** - Rutas, controladores, métodos y respuestas del sistema original
> - - **[APP.md](aro3d-scrape/docs/APP.md)** - Arquitectura, módulos, modelo de datos, autenticación y stack tecnológico
>   - - **[PROBLEMAS.md](aro3d-scrape/docs/PROBLEMAS.md)** - Issues identificados y recomendaciones de mejora para la migración
>     - - **[README.md](aro3d-scrape/README.md)** - Detalles sobre el proceso de scraping
>      
>       - ## ⚠️ Consideraciones de Seguridad
>      
>       - > **⚠️ IMPORTANTE:** La carpeta `aro3d-scrape/data/` contiene **datos personales sensibles de pacientes**:
>         > > - Nombres completos
>         > > - > - Información de contacto
>         > >   > - > - Estudios médicos y diagnósticos
>         > >   >   > - > - Montos de transacciones
>         > >   >   >   > - >
>         > >   >   >   >   >> **Nunca** los subas a repositorios públicos ni los compartas sin autorización. Este repositorio debe permanecer **privado**.
>         > >   >   >   >   >>
>         > >   >   >   >   >> ## 🛠️ Stack Tecnológico
>         > >   >   >   >   >>
>         > >   >   >   >   >> ### Sistema Actual (a migrar)
>         > >   >   >   >   >> - HTML/PHP (monolítico)
>         > >   >   >   >   >> - - Scraping realizado con: Python, Bash
>         > >   >   >   >   >>   - - Gestión de datos: JSON, CSV
>         > >   >   >   >   >>    
>         > >   >   >   >   >>     - ### Sistema Objetivo
>         > >   >   >   >   >>     - - **Backend:** C# / ASP.NET Core
>         > >   >   >   >   >>       - - **Frontend:** Flutter
>         > >   >   >   >   >>         - - **Persistencia:** Base de datos modernizada
>         > >   >   >   >   >>          
>         > >   >   >   >   >>           - ## 📝 Formatos de Datos
>         > >   >   >   >   >>          
>         > >   >   >   >   >>           - - **JSON:** Respuestas API originales (completas)
>         > >   >   >   >   >>             - - **CSV:** Datos aplanados y procesados (Excel-compatible)
>         > >   >   >   >   >>               - - **HTML:** Páginas descargadas (fuente para parsers)
>         > >   >   >   >   >>                
>         > >   >   >   >   >>                 - ## 🔄 Flujo de Trabajo Recomendado
>         > >   >   >   >   >>                
>         > >   >   >   >   >>                 - 1. Revisar documentación técnica en `docs/`
>         > >   >   >   >   >>                   2. 2. Analizar datos extraídos en `data/`
>         > >   >   >   >   >>                      3. 3. Estudiar endpoints y modelos en ENDPOINTS.md
>         > >   >   >   >   >>                         4. 4. Implementar servicios equivalentes en ASP.NET Core
>         > >   >   >   >   >>                            5. 5. Desarrollar UI en Flutter basado en specs de APP.md
>         > >   >   >   >   >>                              
>         > >   >   >   >   >>                               6. ## 📄 Licencia
>         > >   >   >   >   >>                              
>         > >   >   >   >   >>                               7. Este proyecto está licenciado bajo [Apache 2.0](LICENSE).
>         > >   >   >   >   >>                              
>         > >   >   >   >   >>                               8. ## 👤 Contributor
>
> - **Fomexd2** (Edwin Rivera)
>
> - ---
>
> **Estado del Proyecto:** 🚧 En Migración
>
> Para más detalles, consulta la [documentación en la carpeta aro3d-scrape](aro3d-scrape/README.md).
