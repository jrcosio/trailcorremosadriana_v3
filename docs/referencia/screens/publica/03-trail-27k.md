# Trail Peñasagra

| Propiedad | Definición |
|---|---|
| Ruta | `/carreras/trail-27k` |
| Área | Web pública |
| Referencia de código | `components/Site.tsx · RaceDetail` |

## Objetivo

Explicar la prueba de 27 km y +1700 m, diferenciando la edición de los datos de la próxima edición anunciada.

## Composición y contenido

- Cabecera fotográfica con nombre, etiqueta y edición.
- Distancia 27 km, desnivel +1700 m y precio de referencia 28 €.
- Descripción, avituallamientos y recordatorio de cuidado del entorno.
- Mapa/perfil Wikiloc bajo demanda y enlace al recorrido; GPX solo si se configura.
- Ficha técnica lateral: edición, Plaza de Cosío, hora, terreno y próxima fecha.

## Datos

Campos completos de `races[]`. En esta exportación: edición 2026, salida de referencia 09:00, ruta https://es.wikiloc.com/rutas-carrera-por-montana/trail-sierra-penasagra-260167031. Los valores deben seguir siendo editables.

## Acciones y navegación

- Volver a todas las pruebas.
- Cargar mapa únicamente al solicitarlo; abrir Wikiloc en otra pestaña.
- Descargar GPX si existe; no mostrar una descarga inexistente.
- Botón de inscripción lleva a `/inscripciones`, donde se resuelve el destino externo por prueba.

## Estados

- ID inexistente/no publicado: vista de página no encontrada; revisar HTTP 404 en la evolución del router.
- Sin GPX: ocultar esa descarga.
- Sin fecha futura: indicar fecha pendiente.
- Si Wikiloc no carga, conservar el enlace externo y la información técnica.

## Criterios específicos

- No presentar los precios históricos como oficiales de 2027.
- El mapa no debe impedir leer la ficha; pedirlo bajo demanda.
- La tarjeta lateral se adapta a una sola columna en móvil.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
