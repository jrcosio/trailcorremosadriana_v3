# Feature Specification: Galería

**Feature Branch**: `008-galeria`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Galería (short-name: galeria): álbumes, fotografías, orden y conservación de los enlaces históricos. La organización gestiona álbumes por edición con portada, enlace externo histórico opcional (Google Fotos) y fotografías propias subidas. La web muestra los álbumes filtrables por edición y, en cada álbum, sus fotos con visor ampliado accesible o el enlace al álbum original."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gestionar álbumes y fotografías (Priority: P1)

La organización crea en `/admin/galeria` un álbum con título, edición, portada, enlace externo
opcional y fotografías propias (subida múltiple). Lo guarda como borrador y lo publica cuando está
listo. Puede quitar fotos, reordenarlas al volver a subirlas, retirar el álbum o borrarlo.

**Why this priority**: es la única vía de añadir fotos nuevas sin depender de servicios externos.

**Independent Test**: crear un álbum con dos fotos, publicarlo, verlo en la web, quitar una foto,
retirarlo y borrarlo.

**Acceptance Scenarios**:

1. **Given** un álbum nuevo, **When** se guarda, **Then** queda como borrador y no aparece en
   `/galeria` ni en `/galeria/{id}`.
2. **Given** un álbum con fotos propias publicado, **When** se abre, **Then** se ven las fotos en
   cuadrícula en el orden guardado y cada una con un texto alternativo.
3. **Given** un álbum, **When** se quita una foto y se guarda, **Then** deja de mostrarse. El
   archivo no se borra físicamente.
4. **Given** datos no válidos (sin título, sin portada, edición fuera de rango, enlace externo no
   HTTPS, más de 500 fotos), **When** se guarda, **Then** se rechaza con un mensaje claro.
5. **Given** dos sesiones sobre el mismo álbum, **When** la segunda guarda una versión obsoleta,
   **Then** recibe un aviso de conflicto.

---

### User Story 2 - Álbumes históricos (Priority: P1)

Los tres álbumes de 2024, 2025 y 2026 conservan sus enlaces de Google Fotos. Sin fotos propias, el
álbum muestra su portada y el botón para abrir el álbum original, sin aparentar que las fotos se
han importado.

**Why this priority**: conserva los enlaces históricos (regla del producto).

**Independent Test**: tras la importación, abrir los tres álbumes y comprobar sus enlaces.

**Acceptance Scenarios**:

1. **Given** la importación, **When** se abre `/galeria`, **Then** aparecen los 3 álbumes, del más
   reciente al más antiguo.
2. **Given** `/galeria/edicion-2026`, **When** se abre, **Then** se muestra la portada y «Abrir
   álbum en Google Fotos» con el enlace original.
3. **Given** un álbum con fotos propias y enlace externo, **When** se abre, **Then** se ofrecen
   ambos.

---

### User Story 3 - Visor accesible y filtro por edición (Priority: P2)

Un visitante filtra los álbumes por edición y amplía las fotos en un visor que se maneja con el
teclado: flechas, Escape para cerrar y foco atrapado en el visor. Al cerrar, el foco vuelve a la
miniatura.

**Why this priority**: la DOC 09 pide revisar el foco del visor. Mejora la accesibilidad sin
cambiar el diseño.

**Independent Test**: navegar con el teclado por el visor y comprobar el foco.

**Acceptance Scenarios**:

1. **Given** el filtro «2025», **When** se aplica, **Then** solo aparece el álbum de 2025 y no se
   inventan fotos.
2. **Given** el visor abierto, **When** se pulsa Tab repetidamente, **Then** el foco no sale del
   visor.
3. **Given** el visor abierto, **When** se pulsa Escape, **Then** se cierra y el foco vuelve a la
   miniatura que lo abrió.
4. **Given** el visor abierto, **When** se pulsan las flechas, **Then** cambia la foto (de forma
   circular).

---

### Edge Cases

- Álbum sin portada propia: la portada es obligatoria en el panel. Si falta en los datos, se usa
  el paisaje de reserva.
- Foto rota o con fallo de carga: no bloquea el resto de la cuadrícula.
- Identificador inexistente o de un borrador: pantalla de no encontrado.
- Doble envío de un álbum nuevo: no se duplica.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cada álbum MUST tener identificador estable (URL), título (1–150 caracteres),
  edición (año 2000–2099), portada obligatoria (regla de referencias), enlace externo opcional
  (vacío o `https://` sin credenciales), publicación y orden.
- **FR-002**: Cada álbum MUST poder tener hasta 500 fotografías propias, ordenadas, cada una con
  referencia de imagen válida y texto alternativo (por defecto «{título} · fotografía N»).
- **FR-003**: Los álbumes nuevos MUST crearse como borrador. La web y el contrato público MUST
  mostrar solo los publicados, del año más reciente al más antiguo.
- **FR-004**: Quitar fotos o retirar o borrar un álbum MUST NOT borrar archivos del
  almacenamiento.
- **FR-005**: Crear, editar, publicar, retirar y borrar MUST tener control de versión (409), la
  protección de administración, no duplicar ante un doble envío y persistir tras reiniciar.
- **FR-006**: Un comando de operador MUST importar los 3 álbumes históricos con sus enlaces de
  Google Fotos solo si no hay álbumes.
- **FR-007**: El visor MUST atrapar el foco mientras está abierto, cerrarse con Escape, navegar con
  las flechas y devolver el foco a la miniatura al cerrarse, sin cambios visuales.
- **FR-008**: El panel `/admin/galeria` MUST guardar en la base de datos sin cambios visuales.

### Key Entities *(include if feature involves data)*

- **Álbum**: identificador, título, edición, portada, enlace externo, publicación, orden y versión.
- **Fotografía**: álbum, imagen, texto alternativo y orden.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los 3 enlaces históricos de Google Fotos se conservan exactos.
- **SC-002**: 0 álbumes en borrador visibles en la web o en el contrato público.
- **SC-003**: Con el visor abierto, 10 pulsaciones de Tab mantienen el foco dentro, y al cerrar el
  foco vuelve a la miniatura.
- **SC-004**: El 100 % de los cambios persisten tras reiniciar los servicios.

## Assumptions

- El texto alternativo se genera a partir del título del álbum (DISCREPANCIAS M7); el panel aprobado
  no tiene un campo para editarlo.
- Las portadas reutilizadas de los álbumes históricos no certifican el año de la foto (DOC 06).
- No se descargan fotos de Google Fotos: los álbumes históricos siguen siendo enlaces.
