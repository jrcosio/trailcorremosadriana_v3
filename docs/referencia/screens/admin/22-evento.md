# Fecha y contador

| Propiedad | Definición |
|---|---|
| Ruta | `/admin/evento` |
| Área | Administración |
| Referencia de código | `components/admin/Admin.tsx · SettingsScreen` |

## Objetivo

Gestionar la edición, su fecha y la cuenta atrás.

## Composición y contenido

- Edición (año).
- Fecha y hora, expresadas como hora peninsular.
- Interruptor de mostrar contador y explicación del estado sin fecha.
- Guardar y ver web.

## Datos

`settings.edition`, `date`, `countdown`; conversión Europe/Madrid ↔ ISO.

## Acciones y navegación

- Cambiar datos; dejar fecha vacía si no está confirmada.
- Mostrar u ocultar el contador.

## Estados

- Sin fecha confirmada: estado pendiente.
- Cuenta finalizada: no mostrar negativos.
- Respetar cambio horario al convertir fecha y hora.

## Criterios específicos

- No reintroducir el rótulo de marca sobre el reloj.
- No inventar una fecha para que el contador tenga números.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
