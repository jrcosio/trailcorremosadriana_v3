# Discrepancias entre fuentes y su resolución

Orden de autoridad aplicado: (1) propietario → (2) decisiones/especificaciones
aprobadas → (3) código de la propuesta → (4) código de producción.

Fuentes: **DOC** = esta carpeta; **PROP** = código de la propuesta
(`Trail_Penasagra_Desarrollo/proyecto`); **EXP** = contenido exportado
(`contenido/contenido-publicado.json`); **PROD** = web en producción (v2).

## Decisiones del propietario (2026-11-19)

| # | Pregunta | Decisión |
|---|---|---|
| P1 | EXP indica edición «2028» con fecha 2027-07-10 09:00; DOC dice «2027 sin fecha confirmada» | Inicializar la próxima edición como **2027 sin fecha**. El propietario la fijará desde el panel. |
| P2 | PROD publica clasificaciones reales 2026 en CSV; DOC dice «no hay resultados publicados» | **Importar los CSV de 2026 como clasificaciones publicadas** mediante el flujo CSV de la nueva web; `/clasificaciones/2026` sigue funcionando. |

## Datos de prueba en la exportación (no se importan)

| # | Hallazgo | Resolución |
|---|---|---|
| D1 | `settings.edition: "2028"`, `date: "2027-07-10T07:00:00.000Z"` | Ver P1: edición 2027, fecha vacía. |
| D2 | `races[trail-27k].image` = `/media/2f25827b-….png` (silueta de Adriana subida por error) | Se usa la foto real `/reused/img/trail_inscripciones.webp` (semilla de PROP). El PNG no se importa. |
| D3 | Colaborador de prueba «boc» con logo `/media/33d2f7cd-….png` y URL a Scribd | No se importa. Colaboradores vacíos (DOC 08). |
| D4 | Reglamento termina con «PRUEBA / Pues eso esto es una prueba.» | Se elimina el párrafo; se conserva el resumen 2026 de la semilla. |

## Diferencias de modelo y contrato

| # | Diferencia | Resolución |
|---|---|---|
| M1 | PROP guarda todo en un documento JSON; DOC 14 exige tablas relacionadas | Tablas PostgreSQL por recurso. `GET /api/content` se mantiene como adaptador de solo lectura durante la transición. No se implementa `PUT /api/content`. |
| M2 | PROP tiene `settings` globales; DOC 14 asocia contador, apertura, mensaje y URL del dorsal a la edición | Se guardan en `ediciones`. Una edición se marca como actual. |
| M3 | DOC 14 menciona «estado del evento» sin valores | No se crea un enum: la fase se deriva de apertura, fecha (vacía/futura/pasada) y contador, como en DOC 06. Se documenta como supuesto. |
| M4 | Exclusión del Dorsal Solidario por heurística `/solidari/` | El dorsal es configuración de la edición, no una carrera. El servidor rechaza además cualquier carrera cuyo slug/título coincida con la heurística en clasificaciones. |
| M5 | Vista previa/confirmación CSV: huella o importación temporal | Importación temporal en servidor ligada a la sesión, con hash del contenido y caducidad (se detalla en la feature 006). |
| M6 | `color` de carrera existe en datos pero no en formularios | Se conserva como dato de carrera; su edición se decide en la feature 004. |
| M7 | `fotografias.alt` y `entidades.tipo` son nuevos | Se añaden; `alt` vacío por defecto se completa con el título del álbum. |
| M8 | Credenciales PBKDF2 del prototipo | No se migran: Argon2id y CLI de creación/recuperación del administrador. |

## URLs y pantallas

| # | Diferencia | Resolución |
|---|---|---|
| U1 | PROD usa `/recorridos`; PROP usa `/carreras` con alias `/recorridos` | Se conservan ambos (alias). |
| U2 | PROD usa `/clasificaciones/{año}`; PROP solo `/clasificaciones` con filtros | Se añade `/clasificaciones/{año}` como vista prefiltrada (feature 006). |
| U3 | Navegación de PROD (Inicio, Carreras, Reglamento, Galería, Clasificaciones, Contacto) frente a PROP (Carreras, Noticias, Galería, Clasificaciones, Contacto + INSCRIPCIONES) | Prevalece PROP (decisiones aprobadas). |
| U4 | Rutas inexistentes devuelven NotFound con HTTP 200 en PROP | 404 HTTP real en la feature 011. |
| U5 | PROD tiene títulos y metadatos OG por página; PROP solo metadatos genéricos | El build genera metadatos por ruta pública estática con los títulos de PROD; los de detalle se completan en la feature 011. |
| U6 | `/pantallas` y `/pantallas/admin` (vistas de diseño) | Se conservan sin escritura y fuera de la navegación (robots `Disallow`). Decisión final de lanzamiento en la feature 011. |

## Contenido

| # | Diferencia | Resolución |
|---|---|---|
| C1 | Precio infantil: «5 € / Gratis» (PROD recorridos) frente a «Niños < 8 años gratis» (PROD reglamento) y «12 € / 5 €» (PROP) | Se conserva el valor de la semilla de PROP («12 € / 5 €»), que es dato de referencia 2026 editable. |
| C2 | Contacto «Imanol» y «Plaza de Cosío» fijos en PROP | Se mantienen como en PROP; la posibilidad de editarlos se decide en la feature 010. |
| C3 | Noticia «gracias-trail-2026» existe en PROD y no en EXP | Se importa en la feature 007 con su imagen real (PROD, MIT). |
| C4 | Fuentes con extensión `.woff2` y datos TTF | Se corrige en la feature 011 (rendimiento) sin cambiar el aspecto. |
| C5 | CSV de PROD con cabeceras `Pos, Meta, Genero, Pos Categoria, Pos Genero` | Se añaden alias (`meta` → tiempo); `Pos Categoria`/`Pos Genero` se descartan según DOC 13 (no se recalculan posiciones). |
