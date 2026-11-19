# Data Model: Clasificaciones CSV (006)

Migración `0006_clasificaciones` (sobre `0005_inscripciones`).

## Clasificacion (`clasificaciones`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | integer identity | PK |
| `identificador` | varchar(100) | NOT NULL, UNIQUE; `^[A-Za-z0-9_-]{1,100}$` |
| `carrera_edicion_id` | integer | NOT NULL, UNIQUE, FK → `carreras_edicion.id` ON DELETE RESTRICT |
| `titulo` | varchar(200) | NOT NULL, longitud ≥ 1 |
| `publicada` | boolean | NOT NULL, por defecto false |
| `archivo_origen` | varchar(255) | NOT NULL; termina en `.csv` |
| `importada_en` | timestamptz | NOT NULL |
| `participantes` | integer | NOT NULL, 1–5000 |
| `version` | integer | NOT NULL, por defecto 1 |

## Resultado (`resultados`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | bigint identity | PK |
| `clasificacion_id` | integer | NOT NULL, FK → `clasificaciones.id` ON DELETE CASCADE |
| `orden` | integer | NOT NULL; índice (`clasificacion_id`, `orden`) |
| `posicion` | integer | NULL o 1–100000 (CHECK) |
| `dorsal` | varchar(30) | NOT NULL, longitud ≥ 1; único por (`clasificacion_id`, `lower(dorsal)`) |
| `nombre` | varchar(200) | NOT NULL, longitud ≥ 1 |
| `tiempo` | varchar(60) | NOT NULL (vacío solo si no hay posición) |
| `categoria` | varchar(150) | NOT NULL, por defecto `''` |
| `club` | varchar(150) | NOT NULL, por defecto `''` |
| `sexo` | varchar(60) | NOT NULL, por defecto `''` |
| `estado` | varchar(60) | NOT NULL (obligatorio si no hay posición) |
| `busqueda` | text | NOT NULL; «dorsal nombre club» en minúsculas y sin tildes |

## ImportacionCsv (`importaciones_csv`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `token` | uuid | PK |
| `sesion_id` | bigint | NOT NULL, FK → `sesiones.id` ON DELETE CASCADE |
| `carrera_edicion_id` | integer | NOT NULL, FK → `carreras_edicion.id` ON DELETE CASCADE |
| `archivo_origen` | varchar(255) | NOT NULL |
| `filas` | jsonb | NOT NULL; filas normalizadas |
| `sha256` | char(64) | NOT NULL |
| `expira_en` | timestamptz | NOT NULL (creación + 30 min) |

## Contrato (`results[]`)

| Campo | Origen |
|---|---|
| `id` | `Clasificacion.identificador` |
| `title`, `published` | `titulo`, `publicada` |
| `year`, `raceId`, `race` | año de la edición, slug y nombre de la prueba |
| `sourceFile`, `importedAt` | `archivo_origen`, `importada_en` (ISO `…Z`) |
| `participants` | `participantes` |
| `rows` | privado: todas las filas `{position, bib, name, time, category, club, gender, status}`; público: `[]` |
| `version` (admin) | `version` |
