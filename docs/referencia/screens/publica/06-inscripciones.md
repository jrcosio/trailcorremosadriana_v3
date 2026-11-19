# Inscripciones

| Propiedad | Definición |
|---|---|
| Ruta | `/inscripciones` |
| Área | Web pública |
| Referencia de código | `components/Site.tsx · Registration; components/DorsalSolidario.tsx` |

## Objetivo

Informar de la apertura y llevar a la plataforma externa de cada prueba o del dorsal solidario.

## Composición y contenido

- Encabezado con edición y fecha.
- Estado global de apertura y mensaje editable al participante.
- Con apertura: tarjetas por prueba, precio de referencia y enlace de alta si existe; bloque adicional de dorsal solidario.
- Con cierre: explicación, acceso a recorridos, noticias, Instagram y contacto.

## Datos

`settings.registrationsOpen`, `registrationMessage`, `date`, `edition`, `solidarityRegistration` y `races[].registration`.

## Acciones y navegación

- «Inscribirme» abre la URL externa de la prueba.
- «Pagar dorsal solidario» abre su URL específica, no la de otra modalidad.
- Con cierre no deben aparecer destinos de alta activos.

## Estados

- Evento cerrado.
- Evento abierto con prueba sin URL: esa inscripción está pendiente.
- Solo dorsal solidario abierto: válido si tiene enlace; no obligar a configurar una carrera.
- No se realiza pago ni alta dentro de esta implementación.

## Criterios específicos

- Comprobar apertura/cierre desde un navegador nuevo tras guardar en el panel.
- No marcar éxito de inscripción ni de pago dentro de la web.
- No modificar importes ni añadir pasarelas sin datos confirmados.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
