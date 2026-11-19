# Índice de revisión

| Propiedad | Definición |
|---|---|
| Ruta | `/pantallas` |
| Área | Web pública |
| Referencia de código | `components/Site.tsx · ScreenIndex; components/admin/Admin.tsx con previewOnly` |

## Objetivo

Revisar por separado las páginas y vistas de diseño del panel.

## Composición y contenido

- Directorio de pantallas públicas y de administración.
- Los enlaces del panel de diseño usan `/pantallas/admin…`.
- No aparece como sección principal de la navegación de visitantes.

## Datos

Mapa estático de URLs de referencia; las fichas dinámicas usan los registros de ejemplo existentes.

## Acciones y navegación

- Abrir una pantalla pública o una vista de diseño del administrador.
- Desde una vista de diseño se puede ir al acceso real `/admin`.

## Estados

- Vistas de diseño basadas en seed, sin guardado de datos reales.
- Si se elimina un registro de ejemplo, actualizar el enlace del índice.

## Criterios específicos

- No confundir índice de diseño con CMS autenticado.
- Conservar o retirar este índice del lanzamiento público mediante decisión explícita.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
