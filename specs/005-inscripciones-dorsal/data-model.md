# Data Model: Inscripciones y Dorsal Solidario (005)

Migración `0005_inscripciones` (sobre `0004_evento_carreras`).

## Edicion (ampliación de `ediciones`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `inscripciones_abiertas` | boolean | NOT NULL, por defecto `false` |
| `mensaje_inscripciones` | text | NOT NULL, por defecto `''`; en escritura 1–2000 caracteres (CHECK `length ≤ 2000`) |
| `url_dorsal_solidario` | varchar(2200) | NOT NULL, por defecto `''`; vacío o `https://` con host sin credenciales |

## CarreraEdicion (regla nueva, sin cambio de columna)

| Campo | Regla |
|---|---|
| `url_inscripcion` | Vacío o `https://` con host sin credenciales (antes: regla general de referencias) |

## Contrato

| `settings` | Origen |
|---|---|
| `registrationsOpen` | `Edicion.inscripciones_abiertas` (actual) |
| `registrationMessage` | `Edicion.mensaje_inscripciones` |
| `solidarityRegistration` | `Edicion.url_dorsal_solidario` |
| `eventVersion` (admin) | `Edicion.version` (compartida con el evento) |
