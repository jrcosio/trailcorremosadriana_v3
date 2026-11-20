# Feature Specification: Reglamento y contacto

**Feature Branch**: `010-reglamento-contacto`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Reglamento por edición y datos de contacto persistentes, sin cambios visuales, completando la migración del panel por recursos. El reglamento se edita completo y se conserva íntegro; si la edición actual no lo tiene, se muestra el de la más reciente que lo tenga. Correo, teléfono e Instagram en una configuración única que actualiza todas las ubicaciones públicas. El contacto sigue preparando un mailto. Con estas secciones, todo el panel guarda por recursos y se retira el guardado del documento completo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mantener el reglamento (Priority: P1)

La organización escribe o pega en `/admin/reglamento` el texto completo del reglamento. Separa los
apartados con una línea en blanco y usa la primera línea de cada apartado como título. Al guardar,
`/reglamento` muestra el texto íntegro con esos apartados. El reglamento pertenece a la edición
actual. Mientras la edición actual no tenga uno propio, la web y el editor muestran el de la edición
más reciente que sí lo tenga (hoy, la referencia de 2026), con su aviso de edición histórica.

**Why this priority**: el reglamento es información que el corredor necesita antes de inscribirse
y que la organización debe poder completar sin tocar código (DOC 01, pantallas 12 y 23).

**Independent Test**: editar un apartado, guardar, abrir `/reglamento`, reiniciar el servicio y
comprobar que el texto sigue igual. Cambiar la edición actual a una sin reglamento y comprobar que
se sigue viendo el más reciente.

**Acceptance Scenarios**:

1. **Given** el reglamento de referencia importado, **When** se abre `/reglamento`, **Then** se ve
   el resumen de 2026 sin el párrafo de prueba y con el aviso de edición histórica como primer
   bloque.
2. **Given** un texto con apartados, **When** se guarda, **Then** `/reglamento` muestra cada
   apartado con su título y su contenido, sin perder ni reordenar texto.
3. **Given** la edición actual sin reglamento propio, **When** la organización guarda un texto,
   **Then** ese texto queda asociado a la edición actual y el de ediciones anteriores no cambia.
4. **Given** un texto vacío, **When** se guarda, **Then** se rechaza con un mensaje claro y el
   reglamento publicado no cambia.
5. **Given** que otra persona ha guardado antes el evento, las inscripciones o el reglamento,
   **When** se guarda con datos obsoletos, **Then** se informa del conflicto y no se sobrescribe
   nada.
6. **Given** un visitante sin sesión, **When** intenta guardar, **Then** se rechaza.

---

### User Story 2 - Mantener los datos de contacto (Priority: P1)

La organización actualiza en `/admin/ajustes` el correo, el teléfono y el enlace de Instagram. Los
cambios aparecen en todas las ubicaciones públicas que los usan: la página de contacto (correo,
teléfono, Instagram y destino del formulario), el pie de todas las páginas y la página de
inscripciones. El nombre de usuario de Instagram que se lee en `/contacto` sale del enlace
configurado. El formulario de contacto sigue preparando el mensaje en la aplicación de correo del
visitante, dirigido al correo configurado.

**Why this priority**: son los canales de contacto con la organización y deben ser correctos en
toda la web (pantallas 15 y 24).

**Independent Test**: cambiar los tres datos, comprobar cada ubicación pública y el destino del
formulario, reiniciar y comprobar que persisten; restaurar los originales.

**Acceptance Scenarios**:

1. **Given** los datos importados, **When** se abren `/contacto`, el pie y `/inscripciones`,
   **Then** muestran el correo, el teléfono e Instagram actuales de la asociación, igual que antes.
2. **Given** un correo nuevo, **When** se guarda, **Then** el enlace de correo de `/contacto`, el
   del pie y el destino del formulario usan el correo nuevo.
3. **Given** un enlace de Instagram de otra cuenta, **When** se guarda, **Then** todos los enlaces
   apuntan a él y `/contacto` muestra el usuario de esa cuenta.
4. **Given** un correo sin formato válido, un teléfono con letras o un Instagram que no es
   `https://` de Instagram, **When** se guarda, **Then** se rechaza con un mensaje que nombra el
   campo y no se simula el guardado.
5. **Given** el formulario de contacto válido, **When** el visitante lo envía, **Then** se prepara
   un mensaje en su aplicación de correo y la web no afirma que se haya enviado.
6. **Given** dos sesiones, **When** la segunda guarda con datos obsoletos, **Then** recibe un
   conflicto.

---

### User Story 3 - Panel guardado íntegramente por recursos (Priority: P2)

Con el reglamento y el contacto, todas las secciones del panel guardan en su propio recurso. La
web deja de aceptar el guardado del documento completo y el panel nunca lo envía. Si en el panel
apareciera un cambio que no pertenece a ninguna sección conocida, se rechaza con un aviso claro y
sin simular éxito.

**Why this priority**: cierra la transición acordada (DISCREPANCIAS M1) y elimina un punto de
escritura que ya no se usa.

**Independent Test**: guardar en cada sección del panel y comprobar que ninguna operación usa el
guardado del documento completo; comprobar que ese guardado ya no existe.

**Acceptance Scenarios**:

1. **Given** cualquier sección del panel, **When** se guarda un cambio, **Then** se envía solo al
   recurso de esa sección.
2. **Given** el guardado del documento completo, **When** se intenta usar, **Then** no existe.
3. **Given** un cambio sin sección conocida, **When** se guarda, **Then** el panel muestra un aviso
   y no comunica éxito.

---

### Edge Cases

- Texto pegado con saltos de línea de Windows o con espacios al principio y al final: se normalizan
  los saltos y se recortan los espacios exteriores; el resto del texto no cambia.
- Reglamento muy largo (un documento real completo): se admite hasta 200 000 caracteres.
- Cambio de la edición actual a un año nuevo: el reglamento anterior sigue visible como referencia
  hasta que se escriba el nuevo.
- Base sin inicializar: la web muestra los datos de referencia, como en el resto de secciones.
- Guardar el reglamento sin edición actual configurada: se rechaza con un mensaje claro.
- Teléfono con prefijo internacional, espacios o guiones: se admite.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El reglamento MUST guardarse asociado a una edición y la organización MUST editar el
  de la edición actual.
- **FR-002**: La web y el editor MUST mostrar el reglamento de la edición actual o, si no tiene, el
  de la edición más reciente que lo tenga.
- **FR-003**: El texto del reglamento MUST conservarse íntegro: solo se normalizan los saltos de
  línea y se recortan los espacios exteriores. MUST admitir hasta 200 000 caracteres y MUST
  rechazar el texto vacío.
- **FR-004**: Guardar el reglamento MUST compartir el control de conflictos de la edición con el
  evento y las inscripciones, exigir la protección de administración y persistir tras reiniciar.
- **FR-005**: Los datos de contacto (correo, teléfono e Instagram) MUST guardarse en una
  configuración única con control de conflictos, protección de administración y persistencia.
- **FR-006**: El correo MUST tener formato válido (hasta 254 caracteres). El teléfono MUST
  contener solo dígitos, espacios, guiones y paréntesis, con un `+` opcional al principio y entre
  6 y 15 dígitos. Instagram
  MUST ser `https://` en `instagram.com` (con o sin `www.`), sin credenciales. Todos son
  obligatorios.
- **FR-007**: Todas las ubicaciones públicas que muestran correo, teléfono o Instagram MUST usar
  los datos configurados, incluido el usuario de Instagram de `/contacto`, que se deriva del
  enlace.
- **FR-008**: El formulario de contacto MUST seguir preparando un `mailto` al correo configurado y
  MUST NOT afirmar un envío por servidor.
- **FR-009**: Un comando de operador MUST importar el reglamento de referencia de 2026 (sin el
  párrafo de prueba) en la edición 2026 solo si ninguna edición tiene reglamento, y los datos de
  contacto de referencia solo si no hay configuración. MUST NOT sobrescribir datos existentes.
- **FR-010**: El panel MUST guardar cada sección en su recurso y MUST NOT enviar el documento
  completo. El guardado del documento completo MUST dejar de existir.
- **FR-011**: Un cambio del panel sin recurso conocido MUST rechazarse con un aviso claro y sin
  simular éxito.
- **FR-012**: Las pantallas `/reglamento`, `/contacto`, `/admin/reglamento` y `/admin/ajustes`
  MUST conservar su aspecto aprobado. «Imanol» y «Plaza de Cosío» siguen siendo textos fijos.

### Key Entities *(include if feature involves data)*

- **Reglamento de la edición**: texto completo asociado a una edición, con la versión de esa
  edición.
- **Configuración de contacto**: correo, teléfono, enlace de Instagram y versión. Hay una sola.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un reglamento de 200 000 caracteres se guarda y se muestra sin perder ni cambiar
  ningún carácter (aparte de la normalización de saltos y espacios exteriores).
- **SC-002**: Tras cambiar los datos de contacto, el 100 % de las ubicaciones públicas que los usan
  muestran los nuevos valores, y 0 conservan los anteriores.
- **SC-003**: El 100 % de los cambios de reglamento y contacto persisten tras reiniciar.
- **SC-004**: 0 operaciones del panel usan el guardado del documento completo.
- **SC-005**: Con los datos importados, `/reglamento`, `/contacto` y el pie muestran exactamente el
  mismo texto que antes de la feature.

## Assumptions

- «Imanol» (persona de contacto) y «Plaza de Cosío» (salida y meta) siguen fijos en la
  presentación, como en la propuesta (DISCREPANCIAS C2). Las pantallas de referencia piden
  revisarlo, pero no hay una decisión que los convierta en campos y añadirlos cambiaría el panel
  aprobado.
- El reglamento definitivo de 2027 aún no existe (DOC 08). La referencia de 2026 se asocia a su
  edición y se muestra mientras la edición actual no tenga uno propio.
- El enlace «Consultar la página original» de `/reglamento` se mantiene tal cual.
- El contacto sigue usando `mailto` (constitución VI); no se envía correo desde el servidor.
- Las ediciones, sus versiones y la edición actual son las de la feature 004.
