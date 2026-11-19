# Resumen del administrador

| Propiedad | Definición |
|---|---|
| Ruta | `/admin (con sesión)` |
| Área | Administración |
| Referencia de código | `components/admin/Admin.tsx · Dashboard` |

## Objetivo

Orientar a la organización sobre contenido y preparación de la próxima edición.

## Composición y contenido

- Barra lateral, contexto de pantalla, acceso a ver la web y logout.
- Tarjeta de evento, fecha y apertura.
- Conteos de noticias, álbumes, resultados y entidades; no son analítica de visitantes.
- Comprobaciones de fecha/rutas/inscripciones, acciones rápidas y últimos contenidos.

## Datos

Documento privado de `/api/content?admin=1`, incluyendo borradores.

## Acciones y navegación

- Ir a crear noticia, álbum o clasificación.
- Abrir ajustes de evento, recorridos o inscripciones.
- Cerrar sesión.

## Estados

- Cargando, fallo recuperable de contenido y sesión caducada.
- Fecha o rutas pendientes se presentan como tareas, no como confirmación de la nueva edición.

## Criterios específicos

- El contador de entidades suma patrocinadores y colaboradores.
- El logout elimina acceso a la API, no solo oculta el panel.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
