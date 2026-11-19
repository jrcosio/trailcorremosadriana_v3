# Noticias · crear

| Propiedad | Definición |
|---|---|
| Ruta | `/admin/noticias/nuevo` |
| Área | Administración |
| Referencia de código | `components/admin/Admin.tsx · Collection, FieldInput` |

## Objetivo

Crear un registro de noticia y decidir su publicación.

## Composición y contenido

- Enlace de vuelta al listado.
- Formulario de contenido con campos y ayudas.
- Panel de publicación, interruptor de visibilidad y guardar cambios.
- Campos: Título, categoría, fecha opcional, portada, resumen, cuerpo y publicación.

## Datos

Colección `news[]`; ID estable generado para un registro nuevo o leído para editar. El cuerpo es texto plano con párrafos. No inventar fechas de publicación ni activar HTML sin una decisión de formato.

## Acciones y navegación

- Subir archivos permitidos o pegar enlaces según el campo.
- Guardar con revisión del documento; el estado publicado determina su presencia pública.
- Volver a `/admin/noticias`.
- El resultado publicado aparece en `/noticias/:id`.

## Estados

- Nuevo: comienza como borrador.
- Editando: conserva el ID y los datos existentes.
- Subiendo, campo inválido, fallo de subida/guardado, sesión caducada y conflicto 409.
- Edición de ID inexistente: aviso y enlace al listado.
- Vista de diseño `/pantallas/admin…`: no guardar cambios reales.

## Criterios específicos

- Guardar repetidamente no duplica un registro recién creado.
- No perder datos del resto de colecciones al guardar esta.
- Errores explicados junto a la acción y publicación verificable después de recargar.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
