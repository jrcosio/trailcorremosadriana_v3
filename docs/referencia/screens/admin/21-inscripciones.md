# Inscripciones

| Propiedad | Definición |
|---|---|
| Ruta | `/admin/inscripciones` |
| Área | Administración |
| Referencia de código | `components/admin/Admin.tsx · SettingsScreen` |

## Objetivo

Configurar la apertura y los destinos externos.

## Composición y contenido

- Interruptor «Inscripciones abiertas».
- Mensaje al participante.
- Sección específica del dorsal solidario y su URL de pago HTTPS.
- URL de inscripción por prueba y guardar cambios.

## Datos

`settings.registrationsOpen`, `registrationMessage`, `solidarityRegistration`, `races[].registration`.

## Acciones y navegación

- Abrir/cerrar; guardar enlaces y mensaje.
- Ver web para comprobar portada, causa e inscripciones.

## Estados

- Sin ningún destino válido, el servidor rechaza la apertura.
- Puede abrirse solo el dorsal solidario.
- Cerrar conserva los enlaces, pero elimina su disponibilidad pública.

## Criterios específicos

- Los tres bloques solidarios usan exactamente la URL configurada.
- No reemplazar el destino solidario por Contacto o por una prueba distinta.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
