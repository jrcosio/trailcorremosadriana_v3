# Research: Evento y carreras (004)

## R1. Persistencia del panel sin reescribir `Admin.tsx`

- **Decision**: nuevo `frontend/src/lib/persistencia.ts` con `guardarCambios(anterior, siguiente)`.
  `Admin.save()` lo llama en lugar de `PUT /api/content`. El módulo compara secciones y envía cada
  cambio al endpoint de su recurso:
  - `settings.edition`, `settings.date` y `settings.countdown` → `PUT /api/admin/evento`.
  - Cada prueba creada o modificada en `races` → `PUT /api/admin/carreras/{id}`.
  - Cada prueba borrada → `DELETE /api/admin/carreras/{id}`.
  - Cualquier otro cambio (secciones aún no migradas) → `PUT /api/content`, que responde 501 con
    «Esta sección del panel todavía no guarda cambios.».

  Después de las escrituras se recarga `GET /api/content?admin=1` para mostrar los datos y las
  versiones que confirma el servidor. Las features 005–010 añaden aquí sus recursos.
- **Rationale**: todo el panel guarda con `save({...d, [clave]: siguiente})`. Interceptar ese
  único punto conserva las pantallas sin cambios (constitución I) y permite migrar sección a
  sección.
- **Alternatives considered**: un `PUT /api/content` que reparta el documento en tablas
  (contradice M1 y mezcla todos los recursos en una transacción opaca); reescribir los
  formularios del panel (riesgo visual alto en un archivo minificado).

## R2. Modelo relacional

- **Decision**: tres tablas.
  - `ediciones`: `anio` único, `fecha_hora` timestamptz nula, `mostrar_contador`, `es_actual` (con
    índice único parcial `WHERE es_actual`) y `version`.
  - `carreras`: `slug` único (identificador de la URL), `nombre`, `etiqueta`, `color`, `orden`.
  - `carreras_edicion`: UNIQUE(`carrera_id`, `edicion_id`), con los datos por edición,
    `publicada` y `version`.

  La prueba que ve el panel (un `Item` de `races`) corresponde a la carrera más su
  `carreras_edicion` de año más alto. Al guardarla con otra edición se hace un upsert de esa
  ficha y la anterior queda como histórico.
- **Rationale**: lo pide la DOC 14, y las clasificaciones (006) necesitan la ficha
  (`trail-27k`, 2026).

## R3. Fechas

- **Decision**: la API acepta ISO 8601 con zona (el panel envía UTC) o una hora local sin zona,
  que se interpreta en `Europe/Madrid` con `zoneinfo` (`fold=0`: una hora inexistente avanza y
  una ambigua toma la primera ocurrencia). Devuelve ISO UTC con milisegundos y `Z`, igual que el
  prototipo (`2027-07-10T07:00:00.000Z`). Vacío equivale a sin fecha.

## R4. Versiones y conflictos

- **Decision**: `version` entero en `ediciones` y `carreras_edicion`, devuelto en la variante
  privada del contenido como `settings.eventVersion` y `races[].version`. Las escrituras envían
  `version`; si no coincide, responden `409 {"error":"Otra persona ha modificado estos datos.
  Recarga la página antes de guardar."}`. La creación de una prueba usa `version` ausente o 0;
  si el identificador ya existe con otra versión, responde 409 sin duplicar.

## R5. Borrado

- **Decision**: `DELETE /api/admin/carreras/{id}?version=N` borra la carrera y sus fichas
  (CASCADE). La 006 añadirá una FK RESTRICT desde las clasificaciones; mientras tanto el servicio
  ya traduce `IntegrityError` a 409 con «No se puede borrar una prueba con clasificaciones.».

## R6. Importación

- **Decision**: `python -m app.cli importar-inicial [--reemplazar]`.
  - Lee `backend/seed/contenido_inicial.json` y además la edición 2026 con
    `fecha_hora = 2026-07-11 09:00 Europe/Madrid` (dato real de producción).
  - Crea la edición 2027 como actual, sin fecha y con contador, y la 2026 sin contador.
  - Crea las tres pruebas con sus fichas de 2026, publicadas y en el orden de la semilla.
  - Solo actúa si `ediciones` y `carreras` están vacías; si no, informa y no cambia nada.
  - `--reemplazar` exige confirmación escrita (`REEMPLAZAR`) y nunca se usa en el flujo normal.

## R7. Contrato de contenido

- **Decision**: `GET /api/content` monta `settings.edition`, `settings.date` y
  `settings.countdown` con la edición actual, y `races` con las pruebas. En la vista pública solo
  aparecen las fichas publicadas, tomando la de año más alto entre las publicadas. Los demás
  campos siguen saliendo de la semilla hasta sus features. Si no existe ninguna edición ni prueba
  (base sin inicializar), se usan los valores de la semilla y se registra un aviso.

## R8. Representación numérica

- **Decision**: `km` numeric(6,2) ≥ 0 y `desnivel` integer ≥ 0. En el contrato se devuelven como
  texto sin ceros sobrantes (`"27"`, `"7.5"`, `"1700"`), igual que la semilla, porque las
  pantallas los pintan tal cual.
