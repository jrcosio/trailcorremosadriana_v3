# Estado real, comprobaciones y pendientes

## Implementado

- Pantallas públicas con URLs diferenciadas y vistas de detalle.
- Panel con login real, sesión de servidor, límite de intentos y logout.
- Gestión de noticias, resultados, álbumes, pruebas, entidades y configuración.
- Persistencia D1 y subida R2; estados borrador/publicado y revisión de guardado.
- Enlace solidario compartido, condicionado a apertura y URL válida.
- Cuenta atrás configurable, rutas Wikiloc y GPX, imágenes ampliables y conservación de álbumes históricos.
- Cambios de diseño solicitados en la conversación, hasta el commit de `PROCEDENCIA.json`.

## Referencia o funcionamiento acotado

| Área | Situación |
|---|---|
| Edición 2027 | Anunciada, sin fecha confirmada en los datos exportados |
| Pruebas y precios | Referencia de 2026; necesitan confirmación para cada nueva edición |
| Resultados | Importación CSV y tabla de participantes implementadas. No se han publicado resultados ficticios; falta importar los CSV reales del cronometraje |
| Patrocinadores | Ocho logotipos heredados; enlaces no confirmados se mantienen vacíos |
| Colaboradores | Sección preparada; no se asignan entidades arbitrariamente |
| Álbumes históricos | Enlaces externos a 2026, 2025 y 2024; portadas reutilizadas no acreditan el año de la foto |
| Reglamento | Referencia resumida de 2026; falta incorporar texto definitivo vigente |
| Inscripciones y pago | Enlaces externos, sin formularios de alta ni cobro propios |
| Contacto | Mailto explícito, no entrega por servidor |
| Acceso administrador | Una cuenta configurada en entorno; sin pantalla de cambio/recuperación de contraseña |
| SEO | Metadatos generales; revisar estados HTTP 404 y metadatos de detalles, que usan un catch-all |
| Código | Funcional pero concentrado en archivos de interfaz grandes y con tipos amplios |
| Medios retirados | Retirar un registro no implica borrar físicamente su objeto R2; definir mantenimiento |

## Validación histórica de la propuesta

Se realizaron compilaciones y comprobación de tipos; 23 pruebas de funciones de servidor y 10 peticiones reales al despliegue en la fase inicial; después, 15 comprobaciones específicas del dorsal solidario. Hubo revisión visual de páginas públicas y vistas del panel. Los cambios visuales posteriores se compilaron antes de publicarse.

Estos resultados describen el trabajo previo. No equivalen a haber probado cada dispositivo ni a certificar una futura migración. La exportación incorpora su propia verificación en `VALIDACION_PAQUETE.md`.

## Verificación de la actualización CSV

`npm run test:clasificaciones` ejecuta 32 comprobaciones: delimitadores, comillas, BOM, límites, mapeo, dorsales repetidos, estados DNF, representación segura, persistencia con sesión y validación de la carrera. También se comprobó en el navegador la carga de la plantilla, la vista previa y su confirmación en el modo de diseño, sin guardar datos ficticios en producción. El CSV real del proveedor todavía no se ha facilitado.

## Pruebas heredadas

- `scripts/check-solidarity.tsx`: 15 comprobaciones de disponibilidad, enlace, render y guardado, ejecutadas por `npm run test:solidario` en esta copia.
- `scripts/check-server.mjs`: handlers de autenticación, persistencia y archivos con entorno simulado; requiere recibir una contraseña de desarrollo por stdin.
- `scripts/check-api.mjs`: pruebas contra un servidor en la dirección local que contiene el script; revisar esa dirección antes de usarlo fuera del entorno original.
- `scripts/test-env.mjs`: SQLite en memoria y R2 simulado; lee las derivaciones de `.dev.vars`.

## Pendientes prioritarios

1. Confirmar datos reales de la próxima edición y completar reglamento, enlaces y entidades.
2. Arrancar y probar de extremo a extremo en el entorno elegido para continuar.
3. Modularizar pantallas, formularios, tipos y validaciones sin alterar lo aprobado.
4. Definir despliegue independiente, secretos, copias de seguridad y recuperación del acceso.
5. Revisar accesibilidad del visor y modales, foco, estados HTTP, metadatos y rendimiento de imágenes.
6. Si se desea entrega de mensajes por servidor o integración de cronometraje, definir esos contratos y proveedor antes de implementarlos como si ya existieran.

## Arquitectura aprobada pendiente de implementación

El propietario ha elegido FastAPI, PostgreSQL, SQLAlchemy/Alembic, almacenamiento R2/S3 y Docker Compose. [La especificación](14_BACKEND_FASTAPI_POSTGRESQL.md) describe el modelo, la API, autenticación, CSV, migración y aceptación. El código actual no se ha modificado en esta actualización documental. La implementación corresponde al siguiente agente.
