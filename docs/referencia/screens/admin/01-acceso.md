# Acceso de administrador

| Propiedad | Definición |
|---|---|
| Ruta | `/admin (sin sesión)` |
| Área | Administración |
| Referencia de código | `components/admin/Admin.tsx · Login` |

## Objetivo

Permitir entrar al panel con una sesión real del servidor.

## Composición y contenido

- Composición dividida en escritorio: foto/marca y formulario; formulario protagonista en móvil.
- Campos de usuario y contraseña, mostrar/ocultar contraseña, acceso y vuelta a la web.
- Estado de entrada, error y nota de acceso de la organización.

## Datos

Variables de entorno del servidor; POST `/api/login`; comprobación `/api/session`.

## Acciones y navegación

- Enviar credenciales y entrar en la sección solicitada.
- Mostrar/ocultar contraseña sin persistirla en el navegador por la aplicación.
- Volver a la web.

## Estados

- Preparando sesión, sin sesión, enviando, credenciales incorrectas, demasiados intentos y error de servicio.
- Sesión válida muestra el panel; caducada exige volver a entrar.

## Criterios específicos

- No incluir credenciales reales en cliente ni validar solo en JavaScript.
- Mantener límite de intentos, cookie y errores sin revelar qué campo acertó.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
