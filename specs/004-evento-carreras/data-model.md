# Data Model: Evento y carreras (004)

Migración `0004_evento_carreras` (sobre `0003_archivos`).

## Edicion (`ediciones`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | integer identity | PK |
| `anio` | integer | NOT NULL, UNIQUE, CHECK 2000–2099 |
| `fecha_hora` | timestamptz | NULL (sin fecha confirmada) |
| `mostrar_contador` | boolean | NOT NULL, por defecto `true` |
| `es_actual` | boolean | NOT NULL, por defecto `false`; índice único parcial `WHERE es_actual` |
| `version` | integer | NOT NULL, por defecto 1 |
| `creado_en` / `actualizado_en` | timestamptz | NOT NULL, por defecto `now()` |

## Carrera (`carreras`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | integer identity | PK |
| `slug` | varchar(100) | NOT NULL, UNIQUE; patrón `^[A-Za-z0-9_-]{1,100}$`; identificador de la URL |
| `nombre` | varchar(150) | NOT NULL, longitud ≥ 1 |
| `etiqueta` | varchar(60) | NOT NULL, por defecto `''` |
| `color` | varchar(7) | NOT NULL, por defecto `''`; vacío o `#RRGGBB` |
| `orden` | integer | NOT NULL, por defecto 0 |

## CarreraEdicion (`carreras_edicion`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | integer identity | PK |
| `carrera_id` | integer | NOT NULL, FK → `carreras.id` ON DELETE CASCADE |
| `edicion_id` | integer | NOT NULL, FK → `ediciones.id` ON DELETE RESTRICT |
| (par) | | UNIQUE(`carrera_id`, `edicion_id`) |
| `km` | numeric(6,2) | NOT NULL, CHECK ≥ 0 |
| `desnivel` | integer | NOT NULL, CHECK ≥ 0 |
| `precio` | varchar(40) | NOT NULL, longitud ≥ 1 (texto de presentación) |
| `hora_salida` | varchar(5) | NOT NULL, `''` o `HH:MM` |
| `terreno` | varchar(150) | NOT NULL, por defecto `''` |
| `descripcion` | text | NOT NULL, ≤ 5000 caracteres |
| `avituallamientos` | varchar(1000) | NOT NULL, por defecto `''` |
| `imagen` | varchar(2200) | NOT NULL; regla de referencias (003), no vacía |
| `ruta` | varchar(2200) | NOT NULL, `''` o regla de referencias |
| `wikiloc` | varchar(20) | NOT NULL, `''` o solo dígitos |
| `gpx` | varchar(2200) | NOT NULL, `''` o `/media/<clave>.gpx` o https |
| `url_inscripcion` | varchar(2200) | NOT NULL, `''` o regla de referencias (la validación de destino de pago llega en la 005) |
| `publicada` | boolean | NOT NULL, por defecto `false` |
| `version` | integer | NOT NULL, por defecto 1 |
| `actualizado_en` | timestamptz | NOT NULL, por defecto `now()` |

## Correspondencia con el contrato (`SiteData`)

| Contrato | Origen |
|---|---|
| `settings.edition` | `Edicion.anio` (actual), como texto |
| `settings.date` | `Edicion.fecha_hora` (ISO UTC `…Z`) o `''` |
| `settings.countdown` | `Edicion.mostrar_contador` |
| `settings.eventVersion` (solo admin) | `Edicion.version` |
| `races[].id`, `title`, `label`, `color` | `Carrera.slug`, `nombre`, `etiqueta`, `color` |
| `races[].edition` | `Edicion.anio` de la ficha mostrada |
| `races[].km`, `elevation`, `price`, `start`, `terrain`, `description`, `aid`, `image`, `route`, `wikiloc`, `gpx`, `registration`, `published` | `CarreraEdicion.km`, `desnivel`, `precio`, `hora_salida`, `terreno`, `descripcion`, `avituallamientos`, `imagen`, `ruta`, `wikiloc`, `gpx`, `url_inscripcion`, `publicada` |
| `races[].version` (solo admin) | `CarreraEdicion.version` |
