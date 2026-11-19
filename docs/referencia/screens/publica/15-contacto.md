# Contacto

| Propiedad | Definición |
|---|---|
| Ruta | `/contacto` |
| Área | Web pública |
| Referencia de código | `components/Site.tsx · Contact` |

## Objetivo

Resolver dudas y facilitar contacto con la organización.

## Composición y contenido

- Bloque de correo, teléfono, ubicación e Instagram.
- Formulario: nombre, email, asunto y mensaje.
- Explicación de que se prepara el correo en la aplicación del visitante.

## Datos

`settings.email`, `phone`, `instagram`. El nombre Imanol y Plaza de Cosío son referencias de presentación actuales; revisar si se necesitan como campos editables.

## Acciones y navegación

- Mailto, llamada telefónica, Google Maps e Instagram.
- Enviar formulario válido prepara un mailto con asunto y cuerpo; el visitante termina el envío en su correo.

## Estados

- Validación de campos requeridos y formato email.
- Confirmación de preparación, no confirmación falsa de entrega por servidor.
- Si no hay cliente de correo, siguen visibles los datos para copiarlos.

## Criterios específicos

- No enviar comunicaciones automáticas durante pruebas.
- Si se implementa backend de correo, definir proveedor, respuesta y tratamiento de datos antes de anunciar envío real.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
