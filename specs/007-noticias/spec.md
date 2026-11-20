# Feature Specification: Noticias

**Feature Branch**: `007-noticias`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Noticias (short-name: noticias): creación, edición, publicación, borradores, imágenes y detalle público. La organización redacta noticias en el panel (título, categoría, fecha opcional, imagen de portada, resumen y cuerpo en texto plano). Las nuevas empiezan como borrador y los borradores no aparecen en la API pública. La web muestra la lista en /noticias, el detalle en /noticias/{id} y las últimas en la portada."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Redactar y publicar (Priority: P1)

La organización crea una noticia en `/admin/noticias/nuevo` con título y cuerpo (obligatorios),
categoría, fecha opcional, imagen de portada subida y resumen. Se guarda como borrador. Cuando la
publica, aparece en la web.

**Why this priority**: es el canal de comunicación de la organización.

**Independent Test**: crear una noticia, comprobar que no aparece en la web, publicarla, verla en
`/noticias` y en su detalle, retirarla y borrarla.

**Acceptance Scenarios**:

1. **Given** una noticia nueva, **When** se guarda, **Then** queda como borrador y no aparece en
   `/noticias`, ni en la portada, ni en su detalle (pantalla de no encontrado).
2. **Given** un borrador, **When** se publica, **Then** aparece en `/noticias`, en la portada y en
   `/noticias/{id}` tras recargar.
3. **Given** una noticia publicada, **When** se retira o se borra (con confirmación), **Then**
   desaparece de la web.
4. **Given** el cuerpo con párrafos separados por una línea en blanco y texto con etiquetas HTML,
   **When** se muestra, **Then** aparecen los párrafos y el HTML como texto, sin ejecutarse.
5. **Given** título o cuerpo vacíos, una imagen no válida o una fecha no válida, **When** se
   guarda, **Then** se rechaza con un mensaje claro.
6. **Given** dos sesiones editando la misma noticia, **When** la segunda guarda con una versión
   obsoleta, **Then** recibe un aviso de conflicto.

---

### User Story 2 - Conservar las noticias existentes (Priority: P1)

Las noticias aprobadas («Peñasagra 2027 ya está en el horizonte», de la propuesta) y la publicada
en la web actual («¡Gracias por un Trail 2026 inolvidable!», del 13 de julio de 2026, con su
imagen) se cargan una sola vez como publicadas, sin sobrescribir cambios posteriores.

**Why this priority**: evita perder contenido real al migrar.

**Independent Test**: importar en una base vacía y repetir; comprobar la lista y el detalle de
ambas.

**Acceptance Scenarios**:

1. **Given** una base sin noticias, **When** se importa, **Then** existen las 2 noticias publicadas
   con sus textos e imágenes originales.
2. **Given** noticias ya editadas, **When** se repite la importación, **Then** no cambia nada.

---

### Edge Cases

- Noticia sin fecha: se muestra sin fecha y, como anuncio vigente, se ordena por delante de las
  fechadas. Las fechadas van de más reciente a más antigua.
- Noticia sin imagen: se usa el paisaje de portada como imagen de reserva.
- Noticia sin categoría: se muestra «Actualidad».
- Identificador inexistente o de un borrador en `/noticias/{id}`: pantalla de no encontrado.
- Doble envío de una noticia nueva: no se duplica.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cada noticia MUST tener un identificador estable (su URL), un título de 1–200
  caracteres, una categoría opcional (≤ 60), una fecha opcional (día), una imagen opcional (regla
  de referencias de la 003), un resumen opcional (≤ 500), un cuerpo de texto plano de 1–50 000
  caracteres y su estado de publicación.
- **FR-002**: Las noticias nuevas MUST crearse como borrador salvo que se marque su publicación.
- **FR-003**: La web y el contrato público MUST mostrar solo noticias publicadas, ordenadas: sin
  fecha primero y después por fecha descendente (a igualdad, la más reciente en alta).
- **FR-004**: El cuerpo MUST mostrarse como texto, en párrafos separados por una línea en blanco,
  sin interpretar HTML.
- **FR-005**: Crear, editar, publicar, retirar y borrar MUST tener control de versión (409),
  protección de administración, no duplicar ante un doble envío y persistir tras reiniciar.
- **FR-006**: Un comando de operador MUST importar las 2 noticias existentes (la semilla aprobada
  y la de producción con su imagen) solo si no hay noticias.
- **FR-007**: El panel `/admin/noticias` MUST guardar en la base de datos sin cambios visuales.

### Key Entities *(include if feature involves data)*

- **Noticia**: identificador, título, categoría, fecha, imagen, resumen, cuerpo, publicación,
  versión y fechas de alta y modificación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 borradores visibles en la web o en el contrato público.
- **SC-002**: Las 2 noticias existentes se muestran con su texto original íntegro (párrafos
  idénticos).
- **SC-003**: El 100 % de los cambios persisten tras reiniciar los servicios.
- **SC-004**: El 100 % de las escrituras con una versión obsoleta se rechazan sin cambios.

## Assumptions

- La noticia de producción no tiene categoría y no se inventa: se muestra «Actualidad», el valor
  por defecto de la propuesta. Su subtítulo pasa a ser el resumen.
- La imagen `gracias_2026.webp` procede de la web de producción (material del propietario) y se
  sirve como recurso estático en `/reused/noticias/`.
- El cuerpo es texto plano: no hay editor enriquecido (DOC 06).
