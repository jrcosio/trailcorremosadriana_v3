# Research: Inscripciones y Dorsal Solidario (005)

## R1. Dónde se guardan

- **Decision**: migración `0005_inscripciones` con tres columnas nuevas en `ediciones`:
  `inscripciones_abiertas` (bool, por defecto false), `mensaje_inscripciones` (text, por defecto
  `''`) y `url_dorsal_solidario` (varchar(2200), por defecto `''`). La versión de la edición es
  compartida con el evento (004). Los enlaces por prueba siguen en
  `carreras_edicion.url_inscripcion`.
- **Rationale**: la DOC 14 asocia apertura, mensaje y URL del dorsal a la edición.

## R2. Endpoint

- **Decision**: `GET` y `PUT` en `/api/admin/inscripciones` con
  `{registrationsOpen, registrationMessage, solidarityRegistration, version}` (versión de la
  edición actual). La regla de FR-003 se comprueba al abrir: dorsal válido o alguna prueba con su
  ficha publicada más reciente con `url_inscripcion` no vacía. Si no se cumple:
  `400 {"error":"No puedes abrir las inscripciones sin ningún enlace de inscripción ni de pago
  del Dorsal Solidario."}`.

## R3. Validación de destinos

- **Decision**: `app/core/referencias.py` incorpora `url_externa_segura(valor)`: vacío, o
  `https` con host y sin usuario ni contraseña, de como máximo 2200 caracteres y sin espacios.
  Se aplica a `solidarityRegistration` y a `races[].registration`. Antes, `registration` admitía
  la regla general de referencias, que también acepta `/reused/` y `/media/`; ahora se restringe.
  Equivale a `isRegistrationUrl` del frontend.

## R4. Panel

- **Decision**: `persistencia.ts` reparte los campos `registrationsOpen`, `registrationMessage` y
  `solidarityRegistration` a `PUT /api/admin/inscripciones`. El orden de las operaciones es:
  1. Pruebas, para que un enlace nuevo de prueba exista antes de abrir.
  2. Evento.
  3. Inscripciones.
  4. Resto.

  La pantalla `/admin/inscripciones` guarda en una sola acción los enlaces por prueba (`races`) y
  los ajustes.

## R5. Importación

- **Decision**: `importar-inicial` rellena en la edición actual los valores de la semilla (cerradas,
  mensaje de preparación y dorsal vacío) solo si las tres columnas siguen en sus valores por
  defecto. Así se completa también una base importada antes de la 005 sin pisar datos editados.

## R6. Verificación de la matriz

- **Decision**: `frontend/scripts/verificar-inscripciones.mjs` fija los cuatro estados por la API,
  con una URL de ejemplo claramente de prueba (`https://example.com/dorsal-solidario-prueba`), y
  comprueba Inicio, `/solidaridad` e `/inscripciones`: botón, `href` exacto, `target="_blank"`,
  mensajes y ausencia de `/contacto` en el bloque. Al terminar restaura cerradas y sin enlaces.
