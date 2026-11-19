# Colaboradores · editar

| Propiedad | Definición |
|---|---|
| Ruta | `/admin/colaboradores/:id` |
| Área | Administración |
| Referencia de código | `components/admin/Admin.tsx · Collection, FieldInput` |

## Objetivo

Actualizar un registro de colaborador y decidir su publicación.

## Composición y contenido

- Enlace de vuelta al listado.
- Formulario de contenido con campos y ayudas.
- Panel de publicación, interruptor de visibilidad y guardar cambios.
- Campos: Nombre de entidad, logotipo, web opcional, orden y publicación.

## Datos

Colección `collaborators[]`; ID estable generado para un registro nuevo o leído para editar. Tiene el mismo modelo y comportamiento que Patrocinadores, pero colección y bloque público separados.

## Acciones y navegación

- Subir archivos permitidos o pegar enlaces según el campo.
- Guardar con revisión del documento; el estado publicado determina su presencia pública.
- Volver a `/admin/colaboradores`.
- El resultado publicado aparece en `/patrocinadores`.

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
