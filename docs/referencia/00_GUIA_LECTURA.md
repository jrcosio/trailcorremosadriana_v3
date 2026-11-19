# Guía de lectura

| Orden | Documento | Pregunta que resuelve |
|---|---|---|
| 1 | [Producto y alcance](01_PRODUCTO_Y_ALCANCE.md) | Qué debe hacer la web |
| 2 | [Estilo visual](02_ESTILO_VISUAL.md) | Cómo debe verse y qué decisiones preservar |
| 3 | [Mapa de pantallas](03_MAPA_PANTALLAS.md) | Qué URLs y vistas hay |
| 4 | [Arquitectura](04_ARQUITECTURA.md) | Cómo está organizada la implementación |
| 5 | [Datos y API](05_DATOS_Y_API.md) | Qué se guarda y con qué contrato |
| 6 | [Flujos](06_FLUJOS_Y_REGLAS.md) | Cómo se comporta cada acción |
| 7 | [Puesta en marcha](07_PUESTA_EN_MARCHA.md) | Cómo instalar y ejecutar localmente |
| 8 | [Estado y pendientes](08_ESTADO_Y_PENDIENTES.md) | Qué es real y qué hay que cerrar |
| 9 | [Aceptación](09_CRITERIOS_ACEPTACION.md) | Cómo saber si el resultado está completo |
| 10 | [Plan de desarrollo](10_PLAN_DESARROLLO.md) | En qué orden continuar |
| 11 | [Recursos](11_RECURSOS_Y_LICENCIAS.md) | Qué imágenes, fuentes y licencias acompañan al código |

Las fichas de pantalla complementan estos documentos con contenido, composición, acciones, datos y estados concretos. Las rutas dinámicas usan `:id` en documentación; el código actual las resuelve con una página catch-all.

La actualización del formato de resultados se especifica en [13_CLASIFICACIONES_CSV.md](13_CLASIFICACIONES_CSV.md).

Para implementar el backend acordado, leer [14_BACKEND_FASTAPI_POSTGRESQL.md](14_BACKEND_FASTAPI_POSTGRESQL.md). Es el objetivo aprobado; `04_ARQUITECTURA.md` describe el código actual.
