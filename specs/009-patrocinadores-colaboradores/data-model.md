# Data Model: Patrocinadores y colaboradores (009)

Migración `0009_entidades`.

## Entidad (`entidades`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | integer identity | PK |
| `tipo` | varchar(20) | NOT NULL; CHECK `tipo IN ('patrocinador','colaborador')` |
| `slug` | varchar(100) | NOT NULL; `^[A-Za-z0-9_-]{1,100}$`; UNIQUE(`tipo`, `slug`) |
| `nombre` | varchar(150) | NOT NULL, longitud ≥ 1 |
| `logo` | varchar(2200) | NOT NULL, longitud ≥ 1; regla de referencias |
| `web` | varchar(2200) | NOT NULL, por defecto `''`; vacía o https sin credenciales |
| `orden` | integer | NOT NULL, por defecto 0, CHECK ≥ 0 |
| `publicada` | boolean | NOT NULL, por defecto false |
| `version` | integer | NOT NULL, por defecto 1 |
| `creado_en` | timestamptz | NOT NULL, por defecto `now()` |
