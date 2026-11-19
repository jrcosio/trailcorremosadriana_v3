# Reglamento

| Propiedad | Definición |
|---|---|
| Ruta | `/admin/reglamento` |
| Área | Administración |
| Referencia de código | `components/admin/Admin.tsx · SettingsScreen` |

## Objetivo

Mantener el texto completo que entregue la organización.

## Composición y contenido

- Editor de texto de varias líneas.
- Ayuda: apartados separados por una línea en blanco, primera línea como título.
- Guardar y ver web.

## Datos

Campo `regulation` del documento.

## Acciones y navegación

- Editar y guardar el reglamento; comprobar la lectura pública.

## Estados

- Referencia histórica inicial frente a texto vigente confirmado.
- Errores o conflicto no deben simular guardado.

## Criterios específicos

- Conservar íntegro el texto definitivo suministrado.
- No sustituirlo por un resumen al modularizar.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
