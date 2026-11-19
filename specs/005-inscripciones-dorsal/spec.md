# Feature Specification: Inscripciones y Dorsal Solidario

**Feature Branch**: `005-inscripciones-dorsal`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Inscripciones y Dorsal Solidario (short-name: inscripciones-dorsal): apertura/cierre, enlaces externos por carrera y enlace específico de pago solidario, con su disponibilidad compartida. Las inscripciones y los pagos se completan en la plataforma externa enlazada. El Dorsal Solidario usa su URL específica y solo se activa con las inscripciones abiertas y un destino HTTPS válido; mientras no esté disponible muestra «Próximamente disponible» sin desviar a Contacto. Su comportamiento es idéntico en Inicio, Solidaridad e Inscripciones."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Abrir y cerrar inscripciones (Priority: P1)

La organización, desde `/admin/inscripciones`, abre o cierra las inscripciones de la edición
actual, escribe el mensaje para participantes y guarda el enlace de pago del Dorsal Solidario y
los enlaces de inscripción de cada prueba. No puede abrir las inscripciones sin ningún destino
válido.

**Why this priority**: es lo que convierte la web en canal de inscripción y de colaboración
solidaria.

**Independent Test**: guardar cada combinación en el panel y comprobar la respuesta del servidor
y los datos tras recargar y reiniciar.

**Acceptance Scenarios**:

1. **Given** las inscripciones cerradas sin enlaces, **When** se intenta abrirlas, **Then** el
   servidor lo rechaza con un mensaje claro y siguen cerradas.
2. **Given** solo el enlace del Dorsal Solidario configurado, **When** se abren, **Then** se
   aceptan (se puede abrir solo el dorsal).
3. **Given** una prueba publicada con enlace de inscripción, **When** se abren, **Then** se
   aceptan.
4. **Given** las inscripciones abiertas con enlaces, **When** se cierran, **Then** los enlaces se
   conservan en el panel y desaparecen de la web pública.
5. **Given** un enlace que no es HTTPS, contiene credenciales o es un esquema peligroso
   (`javascript:`), **When** se guarda, **Then** se rechaza y no cambia nada.
6. **Given** dos personas editando a la vez, **When** la segunda guarda una versión obsoleta,
   **Then** recibe un aviso de conflicto sin sobrescribir.

---

### User Story 2 - Dorsal Solidario coherente en tres páginas (Priority: P1)

Una persona que quiere colaborar ve en Inicio, en «Corremos por Adriana» y en Inscripciones el
mismo estado del Dorsal Solidario. Si está disponible, el botón «Pagar dorsal solidario» lleva
exactamente a la URL configurada en una pestaña nueva. Si no, aparece «Próximamente disponible»,
sin enlace y sin desviar a otra página.

**Why this priority**: es una decisión aprobada del propietario (12_DECISIONES_APROBADAS.md) y el
canal de la causa solidaria.

**Independent Test**: para cada combinación de la matriz (apertura × URL), abrir las tres páginas
y comprobar el botón, su destino y el mensaje.

**Acceptance Scenarios** (matriz de 09_CRITERIOS_ACEPTACION.md):

1. **Given** cerradas y sin URL, **When** se abren las tres páginas, **Then** muestran
   «Próximamente disponible» y «Disponible cuando se abran las inscripciones», sin enlace.
2. **Given** cerradas con URL válida, **When** se abren, **Then** muestran lo mismo que en el
   escenario 1 y la URL se conserva en el panel.
3. **Given** abiertas sin URL, **When** se abren, **Then** muestran «Próximamente disponible» y
   el aviso de enlace pendiente, sin navegación alternativa.
4. **Given** abiertas con URL HTTPS válida, **When** se abren, **Then** muestran «Pagar dorsal
   solidario» con un enlace exacto a la URL, en pestaña nueva.

---

### User Story 3 - Inscribirse en una prueba (Priority: P2)

Con las inscripciones abiertas, `/inscripciones` muestra una tarjeta por prueba con su precio.
Cada tarjeta tiene el botón «Inscribirme» hacia el enlace externo de esa prueba o, si no tiene
enlace, «Inscripción pendiente para esta prueba.». Con las inscripciones cerradas, la página
muestra el estado cerrado y el mensaje de la organización.

**Why this priority**: completa el recorrido de inscripción. Depende de US1.

**Independent Test**: con las inscripciones abiertas y una prueba con enlace y otra sin él,
comprobar las tarjetas; cerrar y comprobar el estado cerrado.

**Acceptance Scenarios**:

1. **Given** las inscripciones abiertas y la Trail con enlace, **When** se abre `/inscripciones`,
   **Then** la tarjeta de la Trail tiene «Inscribirme» hacia su enlace externo y las demás
   muestran «Inscripción pendiente para esta prueba.».
2. **Given** las inscripciones cerradas, **When** se abre `/inscripciones`, **Then** aparece
   «Inscripciones aún cerradas» con el mensaje configurado y ningún enlace de inscripción.

---

### Edge Cases

- URL con espacios alrededor: se recortan antes de validarla.
- Mensaje vacío: se rechaza, porque el panel lo exige y la página lo muestra.
- Abrir las inscripciones cuando la única prueba con enlace no está publicada: se rechaza, igual
  que sin destinos.
- Una prueba retirada con enlace no cuenta como destino válido.
- Cambiar la edición actual (feature 004): la apertura, el mensaje y el enlace del dorsal son
  propios de cada edición. Una edición nueva empieza cerrada y sin enlaces.
- Los enlaces se guardan solo para redirigir. La web nunca procesa pagos ni inscripciones.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cada edición MUST guardar si las inscripciones están abiertas, el mensaje para
  participantes (obligatorio, 1–2000 caracteres) y el enlace de pago del Dorsal Solidario.
- **FR-002**: El enlace del Dorsal Solidario y los enlaces de inscripción por prueba MUST ser
  vacíos o URLs `https://` con host y sin usuario ni contraseña (máximo 2200 caracteres).
  Cualquier otra forma MUST rechazarse.
- **FR-003**: Abrir las inscripciones MUST rechazarse si no hay un enlace del dorsal válido ni
  ninguna prueba publicada con enlace de inscripción.
- **FR-004**: Cerrar las inscripciones MUST conservar los enlaces guardados.
- **FR-005**: El Dorsal Solidario MUST estar disponible solo si las inscripciones están abiertas
  y el enlace es válido. El mismo comportamiento (botón, destino exacto, pestaña nueva y
  mensajes) MUST mostrarse en Inicio, Solidaridad e Inscripciones.
- **FR-006**: Si el Dorsal Solidario no está disponible, MUST mostrarse «Próximamente disponible»
  sin enlace y sin redirigir a Contacto ni a otra página.
- **FR-007**: Con las inscripciones abiertas, cada prueba publicada MUST mostrar «Inscribirme»
  hacia su enlace o «Inscripción pendiente para esta prueba.»; con las inscripciones cerradas,
  ningún enlace de inscripción.
- **FR-008**: Las modificaciones MUST usar control de versión (409 en conflicto) y la protección
  de administración (feature 002).
- **FR-009**: Los datos MUST persistir entre recargas y reinicios, y el contrato de contenido MUST
  servirlos desde la base de datos con su forma actual.
- **FR-010**: Los datos actuales aprobados (cerradas, mensaje de preparación de la próxima
  edición, sin enlaces) MUST cargarse en la edición actual sin sobrescribir datos ya modificados.
- **FR-011**: La web MUST NOT procesar pagos ni inscripciones: solo enlaza a la plataforma
  externa.

### Key Entities *(include if feature involves data)*

- **Edición (ampliada)**: inscripciones abiertas, mensaje para participantes y enlace de pago del
  Dorsal Solidario.
- **Datos de prueba por edición (existente)**: enlace de inscripción, ahora con validación de
  destino HTTPS.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Las 4 combinaciones de la matriz se comportan como se especifica en las 3 páginas
  (12 de 12 comprobaciones).
- **SC-002**: El 100 % de los destinos peligrosos de prueba (`http`, `javascript:`, con
  credenciales, sin host) se rechazan en el servidor.
- **SC-003**: El 100 % de los intentos de abrir sin destino válido se rechazan.
- **SC-004**: En ninguna página aparece un enlace del dorsal hacia Contacto u otra página interna
  (0 apariciones).
- **SC-005**: Los cambios persisten tras reiniciar los servicios.

## Assumptions

- Los enlaces reales (plataforma de inscripción y pago del dorsal) los facilitará el propietario.
  No se inventan: los datos importados quedan cerrados y sin enlaces. Las pruebas usan URLs de
  ejemplo y se restauran al terminar.
- La regla de FR-003 se comprueba al abrir. Si después se retiran todos los destinos con las
  inscripciones abiertas, el dorsal y las pruebas muestran sus estados de «pendiente» (FR-005 y
  FR-007). No se cierran automáticamente.
- La versión de la edición es compartida por el evento (004) y las inscripciones (005).
