# Galería · crear

| Propiedad | Definición |
|---|---|
| Ruta | `/admin/galeria/nuevo` |
| Área | Administración |
| Referencia de código | `components/admin/Admin.tsx · Collection, FieldInput` |

## Objetivo

Crear un registro de álbum y decidir su publicación.

## Composición y contenido

- Enlace de vuelta al listado.
- Formulario de contenido con campos y ayudas.
- Panel de publicación, interruptor de visibilidad y guardar cambios.
- Campos: Título, edición, portada, enlace externo opcional, fotografías propias y publicación.

## Datos

Colección `albums[]`; ID estable generado para un registro nuevo o leído para editar. Admite varias subidas; quitar una foto de un álbum no borra automáticamente el objeto de R2.

## Acciones y navegación

- Subir archivos permitidos o pegar enlaces según el campo.
- Guardar con revisión del documento; el estado publicado determina su presencia pública.
- Volver a `/admin/galeria`.
- El resultado publicado aparece en `/galeria/:id`.

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
