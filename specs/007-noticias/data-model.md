# Data Model: Noticias (007)

Migración `0007_noticias`.

## Noticia (`noticias`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | integer identity | PK |
| `slug` | varchar(100) | NOT NULL, UNIQUE, `^[A-Za-z0-9_-]{1,100}$` |
| `titulo` | varchar(200) | NOT NULL, longitud ≥ 1 |
| `categoria` | varchar(60) | NOT NULL, por defecto `''` |
| `fecha` | date | NULL |
| `imagen` | varchar(2200) | NOT NULL, por defecto `''`; regla de referencias (003) |
| `extracto` | varchar(500) | NOT NULL, por defecto `''` |
| `cuerpo` | text | NOT NULL, 1–50 000 caracteres (CHECK) |
| `publicada` | boolean | NOT NULL, por defecto false |
| `version` | integer | NOT NULL, por defecto 1 |
| `creado_en` / `actualizado_en` | timestamptz | NOT NULL, por defecto `now()` |
