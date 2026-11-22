# Inicio

| Propiedad | Definición |
|---|---|
| Ruta | `/` |
| Área | Web pública |
| Referencia de código | `components/Site.tsx · Home, Header, Countdown, Partners` |

## Objetivo

Presentar la carrera, su causa y la próxima edición; llevar a pruebas, inscripciones, noticias y dorsal solidario.

## Composición y contenido

- Cabecera blanca con logo y navegación; botón «INSCRIPCIONES».
- Paisaje original; título grande en dos líneas «TRAIL / PEÑASAGRA». *(Decisión P13 del propietario, 2026-11-22: se escribe «PEÑASAGRA», con Ñ; antes, «PENASAGRA».)*
- Frase ampliada «Corremos por Adriana.» y silueta naranja enviada por el propietario.
- Cuenta atrás lateral o apilada, sin el rótulo de marca/edición que se retiró de encima.
- Franja de fecha y ubicación; tres tarjetas fotográficas de pruebas con distancia y desnivel.
- Bloque terracota de dorsal solidario mucho más destacado que la antigua línea gris.
- Sección de causa con foto real; noticia destacada; acceso a galería; patrocinadores de gran tamaño; pie completo.

## Datos

`settings`, `races`, `news`, `sponsors` publicados. Fotos de `public/reused/` y silueta de `public/images/`. La fuente inicial es `lib/data.ts`; después se lee `/api/content`.

## Acciones y navegación

- «Encuentra tu carrera» → `/carreras`.
- «Conoce nuestra causa/historia» → `/solidaridad`.
- Tarjeta de prueba → `/carreras/:id`.
- Dorsal solidario → destino externo específico solo cuando está disponible.
- Noticias, galería y patrocinadores llevan a sus páginas o detalles.

## Estados

- Sin fecha: guiones y «Fecha por confirmar».
- Inscripciones cerradas o dorsal sin enlace: aviso no clicable de próxima disponibilidad.
- Fallo de lectura: aviso de que se muestra información de referencia.
- Solo se muestran registros publicados, sin inventar resultados ni entidades.

## Criterios específicos

- Preservar las últimas decisiones de marca y el tamaño ampliado de patrocinadores.
- No recortar logos ni desbordar el título en móvil.
- Ambas llamadas al dorsal comparten la misma lógica de disponibilidad.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
