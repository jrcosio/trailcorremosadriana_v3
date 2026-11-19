# Patrocinadores y colaboradores

| Propiedad | Definición |
|---|---|
| Ruta | `/patrocinadores` |
| Área | Web pública |
| Referencia de código | `components/Site.tsx · Partners con full` |

## Objetivo

Reconocer el apoyo a la carrera y permitir visitar las webs confirmadas.

## Composición y contenido

- Encabezado e introducción.
- Bloque de patrocinadores con logotipos mucho mayores que en la propuesta inicial.
- Bloque separado de colaboradores con el mismo tratamiento.
- Invitación a colaborar con acceso a Contacto.

## Datos

`sponsors[]` y `collaborators[]` publicados, ordenados por `order`.

## Acciones y navegación

- Logo con URL: abrir web en otra pestaña.
- Logo sin URL: informativo.
- Quiero colaborar → `/contacto`.

## Estados

- Colaboradores aún no anunciados: estado explicativo.
- No inventar URLs ni convertir una entidad de patrocinador a colaborador arbitrariamente.

## Criterios específicos

- 3/2/1 columnas según anchura y celdas grandes.
- Logos completos con `contain`; no estirar ni recortar.
- Un enlace faltante no afecta a la visibilidad de una entidad publicada.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
