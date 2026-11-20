# Data Model: Reglamento y contacto (010)

Migración `0010_reglamento_contacto`.

## Edicion (`ediciones`, columna nueva)

| Campo | Tipo | Restricciones |
|---|---|---|
| `reglamento` | text | NOT NULL, por defecto `''`; CHECK `length(reglamento) <= 200000`. Vacío = sin reglamento propio. Entrada: 1–200 000 caracteres tras normalizar |

La versión es la de la edición (`Edicion.version`), compartida con el evento y las inscripciones.

## Configuracion (`configuracion`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | integer | PK; CHECK `id = 1` (fila única) |
| `correo` | varchar(254) | NOT NULL; formato de correo (research R5) |
| `telefono` | varchar(30) | NOT NULL; dígitos y separadores, con entre 6 y 15 dígitos |
| `instagram` | varchar(2200) | NOT NULL; `https://` en `instagram.com` o `www.instagram.com`, sin credenciales |
| `version` | integer | NOT NULL, por defecto 1 |
| `actualizado_en` | timestamptz | NOT NULL, por defecto `now()`, se actualiza al guardar |

## Contrato `SiteData`

- `regulation`: reglamento mostrado (research R2).
- `settings.email`, `settings.phone` y `settings.instagram` salen de `configuracion` (si no hay
  fila, de la semilla).
- `settings.contactVersion` solo en la vista privada (0 si no hay fila).
