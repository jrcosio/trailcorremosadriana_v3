# Contacto y ajustes

| Propiedad | Definición |
|---|---|
| Ruta | `/admin/ajustes` |
| Área | Administración |
| Referencia de código | `components/admin/Admin.tsx · SettingsScreen` |

## Objetivo

Mantener los datos de contacto que aparecen en la web.

## Composición y contenido

- Correo de organización.
- Teléfono.
- Enlace de Instagram.
- Nota de acceso y guardar cambios.

## Datos

`settings.email`, `phone`, `instagram`.

## Acciones y navegación

- Guardar datos y comprobar Contacto y pie.
- La pantalla actual no cambia contraseña ni administra varias cuentas.

## Estados

- Email/URL inválidos; sesión caducada y conflictos.
- Revisar referencias de presentación que siguen en código, como nombre del contacto.

## Criterios específicos

- Actualizar todas las ubicaciones que usan los campos.
- No presentar una recuperación de acceso que aún no existe.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
