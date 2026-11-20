# Feature Specification: Clasificaciones CSV

**Feature Branch**: `006-clasificaciones-csv`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Clasificaciones CSV (short-name: clasificaciones-csv): importación por carrera/edición, asignación de columnas, vista previa, validación del backend, confirmación transaccional y consulta pública. Las clasificaciones proceden de un CSV por carrera y edición; sustituir un CSV reemplaza sus resultados dentro de una transacción y un error conserva la clasificación anterior. El Dorsal Solidario no tiene clasificación. Se importan como publicadas las clasificaciones reales de 2026 y se conserva la URL histórica /clasificaciones/{año}."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Importar una clasificación desde CSV (Priority: P1)

La organización crea en `/admin/clasificaciones` una clasificación para una carrera y una edición
y elige el CSV del cronometraje. Revisa la asignación de columnas propuesta, ve una vista previa,
pulsa «Usar estos resultados» y guarda. El servidor valida de nuevo todo el archivo antes de
aceptarlo.

**Why this priority**: es la única vía de publicar resultados oficiales.

**Independent Test**: importar la plantilla y un CSV real en el panel, guardar, recargar y
comprobar los participantes en el panel y en la base de datos.

**Acceptance Scenarios**:

1. **Given** un CSV válido con cabeceras, **When** se selecciona, **Then** se detectan el
   separador y las columnas y se muestran las 5 primeras filas.
2. **Given** columnas obligatorias sin asignar (posición, dorsal, nombre, tiempo), **When** se
   intenta usar el CSV, **Then** se indica qué columna falta y no se puede continuar.
3. **Given** un CSV con un dorsal repetido, un clasificado sin tiempo, una posición no válida, un
   número de columnas distinto o comillas sin cerrar, **When** se valida, **Then** se rechaza
   indicando la fila y el motivo.
4. **Given** una vista previa válida, **When** se pulsa «Usar estos resultados» y se guarda,
   **Then** la clasificación queda guardada con todos sus participantes, el nombre del archivo y
   la fecha de importación.
5. **Given** filas no clasificadas (NC, DNF, DNS, DSQ, retirado…), **When** se importan, **Then**
   conservan su estado, no reciben posición inventada y aparecen al final.

---

### User Story 2 - Sustituir sin perder datos (Priority: P1)

Al importar otro CSV para una clasificación existente, todos sus participantes se reemplazan en
una sola operación. Si algo falla, se mantiene íntegra la clasificación anterior.

**Why this priority**: lo exigen las reglas innegociables del producto.

**Independent Test**: sustituir el CSV de una clasificación y comprobar que ya no queda ningún
participante anterior; provocar un fallo y comprobar que no cambia nada.

**Acceptance Scenarios**:

1. **Given** una clasificación con 3 participantes, **When** se sustituye por un CSV de 1,
   **Then** queda exactamente 1 participante, sin mezclar.
2. **Given** una sustitución que falla en la validación final del servidor o en la escritura,
   **When** termina, **Then** la clasificación anterior sigue intacta.
3. **Given** una vista previa preparada por otra sesión o caducada, **When** se intenta guardar
   con ella, **Then** se rechaza y no cambia nada.

---

### User Story 3 - Consultar resultados en la web (Priority: P1)

Cualquier visitante abre `/clasificaciones`, filtra por edición y carrera y consulta la tabla de
participantes. Puede buscar por nombre, dorsal o club (sin distinguir mayúsculas ni tildes),
filtrar por categoría y sexo y paginar de 50 en 50. La URL histórica `/clasificaciones/2026`
muestra directamente la edición 2026.

**Why this priority**: es la consulta pública que hoy ofrece producción.

**Independent Test**: tras importar los CSV de 2026, buscar un participante, filtrar y paginar en
la web, y abrir `/clasificaciones/2026`.

**Acceptance Scenarios**:

1. **Given** las clasificaciones 2026 publicadas, **When** se abre `/clasificaciones/2026`,
   **Then** aparecen las tres clasificaciones de 2026 con su número de participantes.
2. **Given** una tabla, **When** se busca «gonzalez» (sin tilde), **Then** aparecen los
   participantes cuyo nombre, dorsal o club lo contienen con o sin tilde.
3. **Given** más de 50 participantes, **When** se pagina, **Then** se muestran 50 por página con
   «Página N de M» y la posición general original.
4. **Given** filtros por categoría y sexo, **When** se aplican, **Then** se combinan con la
   búsqueda y las posiciones no se recalculan.
5. **Given** una clasificación en borrador, **When** se consulta la web o el contrato público,
   **Then** no aparece.
6. **Given** textos con HTML o fórmulas en el CSV, **When** se muestran, **Then** aparecen como
   texto, sin ejecutarse.

---

### User Story 4 - Dorsal Solidario fuera de clasificaciones (Priority: P2)

El Dorsal Solidario no es una prueba clasificable: no aparece en el selector de carreras del panel
ni en los filtros públicos, y el servidor rechaza cualquier clasificación asociada a él.

**Why this priority**: es una decisión aprobada; no aporta funcionalidad nueva, pero evita errores.

**Independent Test**: intentar crear por la API una clasificación para una prueba solidaria y
comprobar el rechazo; revisar los selectores.

**Acceptance Scenarios**:

1. **Given** una prueba cuyo nombre o identificador corresponde al dorsal solidario, **When** se
   intenta clasificar, **Then** el servidor lo rechaza.
2. **Given** los selectores del panel y de la web, **When** se despliegan, **Then** no incluyen
   la modalidad solidaria.

---

### User Story 5 - Clasificaciones reales de 2026 (Priority: P2)

El operador importa una sola vez los tres CSV oficiales de 2026 de la web actual (27 km → Trail,
14 km → Speed, marcha → Familiar) como clasificaciones publicadas, con el mismo flujo de
validación.

**Why this priority**: conserva el contenido histórico ya público (decisión P2 del propietario).

**Independent Test**: ejecutar la importación de cada CSV y comparar los totales con los
archivos originales.

**Acceptance Scenarios**:

1. **Given** los tres CSV de 2026, **When** se importan, **Then** existen 3 clasificaciones
   publicadas con 63, 205 y 224 participantes.
2. **Given** una clasificación ya existente para esa prueba y edición, **When** se repite la
   importación sin la opción de sustituir, **Then** no cambia nada.

---

### Edge Cases

- CSV en Windows-1252 con tildes: se lee correctamente.
- CSV con BOM, CRLF, comillas dobles y separadores dentro de comillas: se interpreta bien.
- Filas totalmente vacías: se ignoran.
- Más de 60 columnas, celdas de más de 10 000 caracteres, más de 1 MB o más de 5000
  participantes: rechazo claro.
- Dos clasificaciones para la misma prueba y edición: se rechaza la segunda. Hay que editar la
  existente para sustituirla.
- Prueba sin datos para la edición elegida: se pide configurarla antes en «Pruebas y rutas».
- Borrar una prueba que tiene clasificaciones: se rechaza (feature 004).
- Clasificación sin participantes: no puede guardarse.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST permitir una única clasificación por prueba y edición, asociada a
  los datos de esa prueba en esa edición.
- **FR-002**: La lectura del CSV MUST soportar UTF-8 con o sin BOM y Windows-1252, separadores
  `;`, `,` y tabulador (detectando el que da más columnas en la cabecera), comillas, comillas
  dobles escapadas y CRLF, con los límites de 1 MB, 5000 participantes, 60 columnas y 10 000
  caracteres por celda.
- **FR-003**: La asignación de columnas MUST proponerse por alias de cabecera (incluidos «pos» y
  «meta») y ser editable. Posición, dorsal, nombre y tiempo son obligatorios, y cada columna solo
  puede usarse una vez.
- **FR-004**: Las filas MUST validarse con las reglas de `13_CLASIFICACIONES_CSV.md`:
  - posición entera positiva (admite `1.`, `1º`, `1ª`) o un estado de no clasificado;
  - dorsal de hasta 30 caracteres, obligatorio para los clasificados y único entre los no vacíos
    sin distinguir mayúsculas (decisión P3 del propietario);
  - nombre (más apellidos) de hasta 200 caracteres;
  - tiempo obligatorio para los clasificados;
  - estado obligatorio para los no clasificados;
  - categoría y club de hasta 150 caracteres; tiempo, sexo y estado de hasta 60.
  - Los errores MUST indicar la fila.
- **FR-005**: La validación definitiva MUST hacerla el servidor sobre el archivo completo. La
  confirmación MUST usar exactamente los datos revisados, ligados a la sesión que los preparó y
  con caducidad.
- **FR-006**: Confirmar MUST sustituir todos los participantes y los metadatos (archivo y fecha)
  en una única transacción. Cualquier fallo MUST conservar la clasificación anterior.
- **FR-007**: Los participantes no clasificados MUST conservar su estado, sin posición, y
  ordenarse al final. Las posiciones de categoría MUST NOT recalcularse.
- **FR-008**: La consulta pública MUST mostrar solo clasificaciones publicadas, con búsqueda en el
  servidor por nombre, dorsal o club (sin distinguir mayúsculas ni tildes), filtros por categoría
  y sexo, paginación de 50 y las columnas opcionales solo si tienen datos.
- **FR-009**: La URL `/clasificaciones/{año}` MUST mostrar la página de clasificaciones filtrada
  por ese año.
- **FR-010**: El Dorsal Solidario MUST quedar excluido de los selectores y MUST rechazarse en el
  servidor como destino de una clasificación.
- **FR-011**: Publicar, retirar, editar el título y borrar una clasificación MUST tener control de
  versión (409) y la protección de administración. Borrar elimina sus participantes.
- **FR-012**: Borrar una prueba con clasificaciones MUST rechazarse (cierra FR-009 de la 004).
- **FR-013**: Un comando de operador MUST importar un CSV como clasificación (prueba, edición,
  título y publicación) con la misma validación, sin sustituir una existente salvo que se pida
  expresamente.
- **FR-014**: Los datos del CSV MUST mostrarse siempre como texto (sin interpretar HTML ni
  fórmulas). El CSV original MUST NOT publicarse ni conservarse.

### Key Entities *(include if feature involves data)*

- **Clasificación**: identificador, prueba y edición (única por par), título, publicación,
  archivo de origen, fecha de importación, número de participantes y versión.
- **Resultado**: participante de una clasificación con orden, posición (o vacía), dorsal, nombre,
  tiempo, categoría, club, sexo y estado. El dorsal es único dentro de la clasificación.
- **Importación pendiente**: datos ya validados y preparados por una sesión para confirmar, con
  caducidad.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Las 3 clasificaciones reales de 2026 se importan con 63, 205 y 224 participantes,
  como los archivos originales.
- **SC-002**: El 100 % de los CSV no válidos de prueba se rechazan sin alterar los datos
  existentes.
- **SC-003**: Tras una sustitución, quedan 0 participantes del CSV anterior.
- **SC-004**: Una búsqueda devuelve resultados en menos de 1 segundo sobre la clasificación más
  grande.
- **SC-005**: 0 apariciones de clasificaciones en borrador o solidarias en la web y el contrato
  público.
- **SC-006**: `/clasificaciones/2026` muestra las 3 clasificaciones de 2026.

## Assumptions

- Los CSV reales de 2026 contienen datos personales que ya son públicos en la web actual. No se
  versionan en el repositorio: el operador los importa con el comando a partir de los archivos
  originales y solo quedan en la base de datos.
- Las columnas «Pos Categoria» y «Pos Genero» de producción no se importan. La DOC 13 no las
  contempla y las posiciones por categoría no se recalculan.
- La importación temporal en el servidor caduca a los 30 minutos y es de un solo uso.
- La plantilla con datos ficticios nunca se importa como clasificación oficial.
