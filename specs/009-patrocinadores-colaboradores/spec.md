# Feature Specification: Patrocinadores y colaboradores

**Feature Branch**: `009-patrocinadores-colaboradores`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Patrocinadores y colaboradores (short-name: patrocinadores-colaboradores): gestión independiente de ambas secciones, con imagen, enlace, orden y visibilidad. Ambas comparten el mismo modelo funcional. Los patrocinadores mantienen sus imágenes grandes. No se inventan webs ni patrocinadores."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gestionar patrocinadores y colaboradores (Priority: P1)

La organización gestiona por separado, en `/admin/patrocinadores` y `/admin/colaboradores`,
entidades con nombre, logotipo, web opcional, orden de aparición y visibilidad. Cada sección es
independiente: lo que se hace en una no afecta a la otra.

**Why this priority**: patrocinadores y colaboradores sostienen la carrera y deben poder
actualizarse sin tocar código.

**Independent Test**: crear un colaborador con web, publicarlo, cambiar su orden, retirarlo y
borrarlo, y comprobar en cada paso que los patrocinadores no cambian.

**Acceptance Scenarios**:

1. **Given** un colaborador nuevo con logotipo y web HTTPS, **When** se publica, **Then** aparece
   en el bloque de colaboradores de `/patrocinadores` con su logo enlazado en una pestaña nueva.
2. **Given** una entidad sin web, **When** se muestra, **Then** su logo es informativo, sin
   enlace.
3. **Given** varias entidades, **When** se cambia el orden, **Then** la web las muestra en ese
   orden.
4. **Given** una entidad retirada o borrada, **When** se abre la web, **Then** no aparece.
5. **Given** un nombre vacío, un logotipo ausente o una web que no es HTTPS, **When** se guarda,
   **Then** se rechaza con un mensaje claro.
6. **Given** dos sesiones, **When** la segunda guarda con una versión obsoleta, **Then** recibe un
   conflicto.

---

### User Story 2 - Patrocinadores actuales (Priority: P1)

Los 8 patrocinadores reales (Carandía, JV Cosío, Andros, Aljomar, Artipublic, Grupo Choví, Natuber
y Ayuntamiento de Rionansa) se cargan una sola vez con sus logotipos, en su orden y sin web (no
confirmada). Los colaboradores empiezan vacíos.

**Why this priority**: conserva el contenido aprobado sin inventar datos.

**Independent Test**: tras la importación, comprobar la portada y `/patrocinadores`.

**Acceptance Scenarios**:

1. **Given** la importación, **When** se abre `/patrocinadores`, **Then** aparecen los 8 logos en
   orden, grandes y sin enlace, y el aviso de que los colaboradores se anunciarán próximamente.
2. **Given** entidades ya editadas, **When** se repite la importación, **Then** no cambia nada.

---

### Edge Cases

- Mismo identificador en patrocinadores y colaboradores: son entidades distintas. Una entidad no
  cambia de sección sola.
- Orden repetido: se desempata de forma estable por fecha de alta.
- Doble envío de una entidad nueva: no se duplica.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cada entidad MUST tener tipo (patrocinador o colaborador), identificador estable
  dentro de su tipo, nombre (1–150 caracteres), logotipo obligatorio (regla de referencias), web
  opcional (vacía o `https://` sin credenciales), orden (entero ≥ 0) y visibilidad.
- **FR-002**: Las dos secciones MUST gestionarse de forma independiente con el mismo modelo.
- **FR-003**: La web y el contrato público MUST mostrar solo las entidades visibles, por orden.
  Las que tienen web se enlazan en una pestaña nueva y las que no, se muestran sin enlace.
- **FR-004**: Crear, editar, retirar y borrar MUST tener control de versión (409), la protección
  de administración, no duplicar ante un doble envío y persistir tras reiniciar.
- **FR-005**: Un comando de operador MUST importar los 8 patrocinadores aprobados (sin web) solo si
  no hay entidades. MUST NOT inventarse webs ni colaboradores.
- **FR-006**: Los logotipos de patrocinadores MUST conservar el tamaño grande aprobado, sin
  recortar ni deformar (sin cambios visuales).
- **FR-007**: Los paneles `/admin/patrocinadores` y `/admin/colaboradores` MUST guardar en la base
  de datos sin cambios visuales.

### Key Entities *(include if feature involves data)*

- **Entidad**: tipo, identificador, nombre, logotipo, web, orden, visibilidad y versión.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los 8 patrocinadores aparecen en orden y con 0 enlaces inventados.
- **SC-002**: Una operación en una sección no modifica ninguna entidad de la otra (0 cambios).
- **SC-003**: El 100 % de los cambios persisten tras reiniciar.
- **SC-004**: Los logos se muestran completos: el tamaño del elemento respeta la proporción de la
  imagen (`object-fit: contain`).

## Assumptions

- Las webs de los patrocinadores no están confirmadas (DOC 08) y quedan vacías hasta que la
  organización las indique.
- No hay colaboradores confirmados. El colaborador de prueba de la exportación (D3) no se importa.
