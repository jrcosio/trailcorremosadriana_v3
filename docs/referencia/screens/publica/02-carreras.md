# Pruebas y recorridos

| Propiedad | Definición |
|---|---|
| Ruta | `/carreras` |
| Área | Web pública |
| Referencia de código | `components/Site.tsx · Races, RaceCards` |

## Objetivo

Comparar las tres pruebas de referencia y abrir su ficha.

## Composición y contenido

- Cabecera y encabezado de página con introducción.
- Tres tarjetas fotográficas: Trail Peñasagra 27K, Speed Trail 14K y Familiar Peñasagra 7K.
- Aviso de que los datos corresponden a la edición indicada y pueden ser referencia de 2026.
- Bloque de preparación, material y acceso al reglamento.

## Datos

`races[]` publicados: título, etiqueta, distancia, desnivel e imagen. `/recorridos` se conserva como alias de este listado.

## Acciones y navegación

- Cada tarjeta abre `/carreras/:id`.
- Acceso a reglamento e inscripciones mediante navegación común.

## Estados

- Lista alimentada por el CMS; no añadir una prueba no publicada.
- Si la colección queda vacía, mantener una explicación útil en vez de tarjetas inventadas.

## Criterios específicos

- Distancias y desniveles deben proceder de los datos, no de etiquetas rígidas.
- En móvil las tarjetas se apilan y conservan legibilidad sobre la foto.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
