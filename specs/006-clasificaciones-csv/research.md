# Research: Clasificaciones CSV (006)

## R1. Dónde se lee y se valida el CSV

- **Decision**:
  - El panel conserva la lectura, el mapeo y la vista previa en el cliente (`lib/classifications.ts`),
    con la misma interfaz y respuesta inmediata.
  - Al pulsar «Usar estos resultados», envía a `POST /api/admin/clasificaciones/vista-previa` el
    texto decodificado del CSV, el mapeo, el nombre del archivo, la prueba y la edición.
  - El servidor (`app/services/csv_clasificaciones.py`, una adaptación fiel del lector TS)
    vuelve a leer y validar el archivo completo. Guarda las filas normalizadas en
    `importaciones_csv`, ligadas a la sesión, con una caducidad de 30 minutos y la huella SHA-256
    de las filas, y devuelve `{token, participants}`.
  - Al guardar, `PUT /api/admin/clasificaciones/{id}` con `importToken` sustituye las filas en una
    transacción y consume la importación.
- **Rationale**: la DOC 14 pide validación en el servidor y una confirmación ligada a los datos
  revisados. Elegimos la importación temporal en lugar de la huella de contenido (DISCREPANCIAS
  M5) porque no obliga a reenviar el CSV y permite caducidad y un solo uso.
- **Alternatives considered**: mover toda la lectura al servidor (más idas y vueltas y cambio de
  la experiencia aprobada); confiar en las filas que manda el cliente (incumple FR-005).

## R2. Modelo

- **Decision**:
  - `clasificaciones`: `identificador` único (el id que usa el panel), `carrera_edicion_id` UNIQUE
    con FK RESTRICT (impide borrar la prueba; cierra FR-009 de la 004), `titulo`, `publicada`,
    `archivo_origen`, `importada_en`, `participantes` y `version`.
  - `resultados`: `orden`, `posicion` (NULL o 1–100000), dorsal y tiempo como texto, más
    `busqueda`, que se calcula al importar (minúsculas, sin tildes, «dorsal nombre club»). Índice
    único `(clasificacion_id, lower(dorsal))`.
  - `importaciones_csv`: `token` UUID como PK, `sesion_id` con FK CASCADE, filas en JSONB, huella,
    archivo, `carrera_edicion_id` y caducidad.

## R3. Consulta pública

- **Decision**:
  - `GET /api/content` público devuelve en `results` los metadatos con `participants` y
    `rows: []`; el privado incluye las filas para el panel.
  - `GET /api/clasificaciones/{id}/participantes?q=&categoria=&sexo=&pagina=` devuelve:
    - las filas de la página (50) y los totales;
    - las listas de categorías y sexos;
    - las columnas opcionales con datos (calculadas sobre toda la clasificación).
  - La búsqueda usa `busqueda LIKE %q_normalizada%`, con escape de `%` y `_`.
  - `ClassificationTable` y `Results` se adaptan para leer del servidor con el mismo marcado;
    `visibleClassifications` acepta `participants`.
  - `/clasificaciones/{año}` fija el año inicial del filtro en `Results`.
- **Rationale**: la DOC 14 exige búsqueda y paginación en el servidor. El público deja de
  descargar todas las filas.

## R4. Exclusión solidaria

- **Decision**: el servidor rechaza una prueba cuyo slug o nombre coincida con `es_modalidad_solidaria`
  (DISCREPANCIAS M4), además del filtro del cliente.

## R5. Importación de 2026

- **Decision**: `python -m app.cli importar-clasificacion --carrera SLUG --edicion AAAA --titulo T
  [--publicar] [--sustituir] [--archivo NOMBRE] < archivo.csv`.
  - Decodifica UTF-8 y, si falla, Windows-1252, y usa el mapeo automático.
  - Pasa por la misma validación y transacción que el panel.
  - Los CSV reales se leen de `datos_iniciales/…/datos/2026/` con stdin y no se versionan
    (datos personales).

## R6. Alias

- **Decision**: se añaden `meta` (tiempo) al lector TS y al de Python (DISCREPANCIAS C5). `pos` ya
  estaba. Con «Pos Categoria» y «Pos Genero» no hay ambigüedad, porque normalizadas no coinciden
  con ningún alias.
