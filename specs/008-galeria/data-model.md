# Data Model: Galería (008)

Migración `0008_galeria`.

## Album (`albumes`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | integer identity | PK |
| `slug` | varchar(100) | NOT NULL, UNIQUE, `^[A-Za-z0-9_-]{1,100}$` |
| `titulo` | varchar(150) | NOT NULL, longitud ≥ 1 |
| `anio` | integer | NOT NULL, CHECK 2000–2099 |
| `portada` | varchar(2200) | NOT NULL, longitud ≥ 1; regla de referencias |
| `url_externa` | varchar(2200) | NOT NULL, por defecto `''`; vacío o https sin credenciales |
| `publicado` | boolean | NOT NULL, por defecto false |
| `orden` | integer | NOT NULL, por defecto 0 |
| `version` | integer | NOT NULL, por defecto 1 |

## Fotografia (`fotografias`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | bigint identity | PK |
| `album_id` | integer | NOT NULL, FK → `albumes.id` ON DELETE CASCADE |
| `imagen` | varchar(2200) | NOT NULL; regla de referencias, no vacía |
| `alt` | varchar(250) | NOT NULL |
| `orden` | integer | NOT NULL; UNIQUE(`album_id`, `orden`) |

Límite: 500 fotografías por álbum (validación de entrada).
