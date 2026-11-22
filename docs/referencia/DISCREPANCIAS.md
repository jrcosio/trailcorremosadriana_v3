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
| P3 (2026-11-20) | El CSV real de la 27K tiene una participante «Sin salida» sin dorsal; DOC 13 exige dorsal en todas las filas | **Dorsal obligatorio solo para clasificados**; los no clasificados pueden no tenerlo y la unicidad se aplica a dorsales no vacíos. Se importan los 63. |
| P4 (2026-11-20) | Los botones naranjas (#dc6537, 3,52:1) y dos textos del bloque solidario no cumplen WCAG AA | **Corregir a AA**: botones en el naranja oscuro de la paleta (#b64b24, hover #9a3d1c), textos del bloque solidario en blanco y enlace del pie «JR BLANCO» subrayado. *(Desde P9 la frase del pie no tiene enlace. P4 se aplica también al panel con la sesión iniciada desde la feature 012, US9: cabeceras de tabla y pie del panel en `--muted`.)* |
| P5 (2026-11-20) | ¿`/pantallas` (índice de revisión y vistas de diseño) se conserva en el lanzamiento público? (U6) | **Retirar en producción** mediante configuración (404); disponible en desarrollo y revisión local. |
| P6 (2026-11-20) | Capturas del propietario: la foto de Adriana sale con la cabeza cortada (portada y `/solidaridad`) | **Las fotos se ven siempre completas**: ninguna foto se recorta para rellenar su marco (feature 012). |
| P7 (2026-11-21) | Logotipo nuevo del propietario (`datos_iniciales/new_logo.png`): «sustituir el logo de la parte superior izquierda y el texto que está en dos filas» | **La cabecera pública muestra el logotipo nuevo** en lugar de la silueta y del texto «TRAIL PEÑASAGRA / CORREMOS POR ADRIANA», sin cambiar su altura ni mover el resto. El pie y el panel, con fondo oscuro, conservan la marca blanca; el título «TRAIL PENASAGRA» de la portada no cambia (feature 012, US3). El pie cambia después con la P8. |
| P8 (2026-11-21) | «Pon también el logo en el pie» | **El pie muestra el logotipo nuevo en negativo**: texto y montañas en blanco, naranja conservado, derivado del original. Ocupa el ancho de la marca anterior (233 px) y crece en alto unos 23 px; las demás columnas del pie no se mueven. La barra lateral del panel y el favicon no cambian (feature 012, US4). *(Desde P11 el panel también lleva el logotipo.)* |
| P9 (2026-11-21) | Cambiar la frase del pie «Hecho con pasión por JR BLANCO · Hackers Cosío» por «Hecho por la Escuela Hacker Cosío» | **El pie dice «Hecho por la Escuela Hacker Cosío»**, como texto y con el estilo de la línea. Sin enlace: la frase nueva no nombra a JR BLANCO y no hay dirección de la Escuela (no se inventan enlaces). El aviso de copyright no cambia (feature 012, US5). |
| P10 (2026-11-21) | En la clasificación, que los 3 primeros se diferencien con un color suave cada uno, además de la negrita («lo que tú decidas que queda más visual para el podio») | **Podio en oro, plata y bronce suaves**: fondo de la fila, franja a la izquierda y medalla con el número. Es el puesto publicado; no se calculan podios por sexo ni por categoría. Las demás filas y el alto de todas no cambian (feature 012, US6). *(Ampliado por P12: podio por sexo y por categoría, con etiqueta junto al nombre.)* |
| P11 (2026-11-21) | «El logo, es cierto que hay que poner el oficial también aquí», sobre la barra lateral del panel | **El panel muestra el logotipo oficial en negativo** en la barra lateral, con «ADMINISTRACIÓN» debajo, y en la pantalla de acceso. Ocupa el ancho de la marca anterior y nada se mueve en horizontal. El favicon no cambia (feature 012, US8). |
| P12 (2026-11-21) | «Si cambio a femenino no me identifica a las tres campeonas»: identificar a las 3 primeras chicas y a los 3 primeros chicos de todas las pruebas, y también por categoría | **Podio por sexo y por categoría**: sin filtros, 3 chicos y 3 chicas; con el filtro de sexo, el de ese sexo; con el de categoría, el de la categoría. Lo calcula el servidor (la búsqueda no lo cambia). «Pos.» conserva la posición general, y junto al nombre aparece una etiqueta de oro, plata o bronce («1.ª mujer», «1.º Vet A M») en lugar de la medalla. Presentación elegida por el propietario (feature 012, US10). |
| P13 (2026-11-22) | «En la home, como título principal en grande, pone PENASAGRA y es PEÑASAGRA; repasa para que todo esté bien escrito». La constitución (I) y la referencia aprobada pedían el literal «TRAIL PENASAGRA» | **El título de la portada dice «TRAIL PEÑASAGRA»**, con Ñ, con la misma fuente, tamaño, color y caja. Se enmienda la constitución (1.0.1) y se anotan `12_DECISIONES_APROBADAS.md`, `02_ESTILO_VISUAL.md`, `09_CRITERIOS_ACEPTACION.md` y `screens/publica/01-inicio.md`. Las demás menciones del literal antiguo en la referencia quedan sustituidas por esta decisión. La revisión ortográfica de 56 vistas y de los mensajes del código corrige textos del panel formados con el nombre interno de la sección, los nombres accesibles de las subidas, los errores del CSV con el campo en inglés, dos preguntas sin signos en el contacto y las comillas de la descripción de un álbum. Los contenidos de la organización no tienen faltas y no se tocan. Feature 012, US11 (`specs/012-ajustes-revision/research.md` R11). |

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
| M1 | PROP guarda todo en un documento JSON; DOC 14 exige tablas relacionadas | Tablas PostgreSQL por recurso. `GET /api/content` se mantiene como adaptador de solo lectura. **Transición completada (010)**: todas las secciones guardan por recurso, el 501 transitorio se retira y `PUT /api/content` no existe (405). |
| M2 | PROP tiene `settings` globales; DOC 14 asocia contador, apertura, mensaje y URL del dorsal a la edición | Se guardan en `ediciones`. Una edición se marca como actual. |
| M3 | DOC 14 menciona «estado del evento» sin valores | No se crea un enum: la fase se deriva de apertura, fecha (vacía/futura/pasada) y contador, como en DOC 06. Se documenta como supuesto. |
| M4 | Exclusión del Dorsal Solidario por heurística `/solidari/` | El dorsal es configuración de la edición, no una carrera. El servidor rechaza además cualquier carrera cuyo slug/título coincida con la heurística en clasificaciones. |
| M5 | Vista previa/confirmación CSV: huella o importación temporal | **Resuelta (006)**: importación temporal en `importaciones_csv`, ligada a la sesión, con huella SHA-256 de las filas, caducidad de 30 min y un solo uso. La confirmación sustituye las filas en una transacción. |
| M6 | `color` de carrera existe en datos pero no en formularios | Se conserva como dato de carrera; su edición se decide en la feature 004. |
| M7 | `fotografias.alt` y `entidades.tipo` son nuevos | Se añaden; `alt` vacío por defecto se completa con el título del álbum. |
| M8 | Credenciales PBKDF2 del prototipo | No se migran: Argon2id y CLI de creación/recuperación del administrador. |

## URLs y pantallas

| # | Diferencia | Resolución |
|---|---|---|
| U1 | PROD usa `/recorridos`; PROP usa `/carreras` con alias `/recorridos` | Se conservan ambos (alias). |
| U2 | PROD usa `/clasificaciones/{año}`; PROP solo `/clasificaciones` con filtros | Se añade `/clasificaciones/{año}` como vista prefiltrada (feature 006). |
| U3 | Navegación de PROD (Inicio, Carreras, Reglamento, Galería, Clasificaciones, Contacto) frente a PROP (Carreras, Noticias, Galería, Clasificaciones, Contacto + INSCRIPCIONES) | Prevalece PROP (decisiones aprobadas). |
| U4 | Rutas inexistentes devuelven NotFound con HTTP 200 en PROP | **Resuelta (011)**: 404 HTTP real para rutas inexistentes y para detalles inexistentes o no publicados (plantilla de Caddy + `/api/meta`). |
| U5 | PROD tiene títulos y metadatos OG por página; PROP solo metadatos genéricos | **Resuelta (011)**: los detalles publicados (noticias, álbumes, pruebas y clasificaciones por año) llevan título, descripción, imagen y canónica propios en el HTML inicial. |
| U6 | `/pantallas` y `/pantallas/admin` (vistas de diseño) | **Resuelta (011, decisión P5)**: retiradas en producción (`PANTALLAS=no` → 404); disponibles en la revisión local (`PANTALLAS=si`). |

## Contenido

| # | Diferencia | Resolución |
|---|---|---|
| C1 | Precio infantil: «5 € / Gratis» (PROD recorridos) frente a «Niños < 8 años gratis» (PROD reglamento) y «12 € / 5 €» (PROP) | Se conserva el valor de la semilla de PROP («12 € / 5 €»), que es dato de referencia 2026 editable. |
| C2 | Contacto «Imanol» y «Plaza de Cosío» fijos en PROP | **Resuelta (010)**: siguen fijos, como en PROP, porque no hay decisión que los convierta en campos y añadirlos cambiaría el panel aprobado. Correo, teléfono e Instagram son editables; el usuario de Instagram se deriva del enlace. |
| C3 | Noticia «gracias-trail-2026» existe en PROD y no en EXP | Se importa en la feature 007 con su imagen real (PROD, MIT). |
| C4 | Fuentes con extensión `.woff2` y datos TTF | **Resuelta (011)**: conversión a WOFF2 real con fontTools; −66 % de peso y capturas idénticas píxel a píxel. |
| C5 | CSV de PROD con cabeceras `Pos, Meta, Genero, Pos Categoria, Pos Genero` | **Resuelta (006)**: alias `meta` → tiempo en el cliente y en el servidor; `Pos Categoria` y `Pos Genero` no se importan. Los CSV reales no se versionan (datos personales): se importan con `importar-clasificacion` desde el archivo original. |
