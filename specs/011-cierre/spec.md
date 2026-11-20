# Feature Specification: Cierre para el lanzamiento

**Feature Branch**: `011-cierre`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Cierre para el lanzamiento, sin funcionalidades nuevas de contenido: 404 reales y metadatos de detalle; accesibilidad AA y móvil (decisión P4); copias, restauración y ensayo de despliegue independiente con documentación de operación; cabeceras de seguridad y retirada de /pantallas en producción (decisión P5); rendimiento de fuentes; limpieza de archivos sin referencias, código sin uso y avisos de dependencias. Sin desplegar ni tocar producción."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Páginas que no existen y vistas previas al compartir (Priority: P1)

Un visitante o un buscador que abre una dirección que no existe recibe la página «Este sendero no
está en el mapa.» con un estado «no encontrado» real. Lo mismo pasa con una noticia, un álbum,
una prueba o un año de clasificaciones que no existe o no está publicado. Quien comparte una
noticia, un álbum o una prueba en una red social o una aplicación de mensajería ve una vista
previa con su título, su descripción y su imagen, no los generales de la web.

**Why this priority**: evita que los buscadores indexen páginas vacías como válidas (U4) y
completa los metadatos por página que tenía la web de producción (U5).

**Independent Test**: pedir rutas inexistentes y detalles existentes, no publicados e
inexistentes, y comprobar el estado y los metadatos del HTML inicial, sin ejecutar la página.

**Acceptance Scenarios**:

1. **Given** una ruta que no existe, **When** se pide, **Then** responde «no encontrado» y la
   página muestra «Este sendero no está en el mapa.».
2. **Given** una noticia, un álbum o una prueba publicados, **When** se pide su página, **Then** el
   HTML inicial incluye su título, su descripción, su imagen y su dirección canónica.
3. **Given** un borrador o un identificador inexistente, **When** se pide su página, **Then**
   responde «no encontrado» y no revela el contenido del borrador.
4. **Given** `/clasificaciones/2026` con clasificaciones publicadas, **When** se pide, **Then**
   responde con éxito; **Given** un año sin clasificaciones publicadas, **Then** «no encontrado».
5. **Given** el servicio de datos detenido, **When** se pide una página de detalle, **Then** se
   sirve la web con los metadatos generales y su aviso de respaldo, no un error.
6. **Given** una petición a una dirección o un método inexistentes de la interfaz de datos,
   **When** responde, **Then** el mensaje de error está en español.

---

### User Story 2 - Accesibilidad y móvil (Priority: P1)

Cualquier visitante, también quien usa lector de pantalla, teclado, zoom o un móvil pequeño, puede
leer y usar la web y el acceso al panel. Los botones principales y el bloque del Dorsal Solidario
tienen contraste suficiente (decisión P4) y la cabecera cabe en móviles de 320 px.

**Why this priority**: es un criterio de aceptación del proyecto (DOC 09) y, con P4, el propietario
ha aprobado los ajustes de color necesarios.

**Independent Test**: revisión automática WCAG 2.1 A/AA de todas las páginas públicas y del acceso
al panel a 360 y 1440 px, comprobación de desbordamiento a 320, 340, 360, 768, 1024 y 1440 px,
y recorrido con teclado.

**Acceptance Scenarios**:

1. **Given** cualquier página pública o el acceso al panel, **When** se revisa automáticamente a
   360 y 1440 px, **Then** hay 0 incumplimientos WCAG 2.1 A/AA.
2. **Given** los botones principales, **When** se muestran, **Then** usan el naranja oscuro
   aprobado (#b64b24, #9a3d1c al pasar por encima) con texto blanco.
3. **Given** el bloque del Dorsal Solidario, **When** se muestra, **Then** su antetítulo y su texto
   son blancos sobre el mismo fondo.
4. **Given** el enlace «JR BLANCO» del pie, **When** se muestra, **Then** está subrayado.
5. **Given** un móvil de 320 o 340 px, **When** se abre cualquier página pública, **Then** no hay
   desplazamiento horizontal.
6. **Given** las demás partes de la interfaz, **When** se comparan con las capturas aprobadas,
   **Then** no cambian.

---

### User Story 3 - Copias, restauración y despliegue independiente (Priority: P1)

La persona que opera la web hace una copia de seguridad y la restaura, y los datos y archivos
quedan exactamente como estaban. Con la documentación de operación puede instalar la web en otro
servidor, configurarla, crear el administrador, restaurar una copia, actualizarla y recuperar el
acceso, sin depender del entorno de desarrollo.

**Why this priority**: sin copia y restauración probadas no se puede lanzar con garantías (DOC 08 y
14). La web debe poder desplegarse de forma independiente.

**Independent Test**: hacer una copia, cambiar datos, restaurar y comparar. Clonar el repositorio en
limpio, levantar un proyecto separado en otro puerto, restaurar la copia y comprobar la web.

**Acceptance Scenarios**:

1. **Given** una copia de la base y los archivos, **When** se cambian datos y se restaura la copia,
   **Then** todas las tablas y archivos coinciden con los de la copia.
2. **Given** un clon limpio sin datos de referencia ni secretos, **When** se sigue la documentación
   en un proyecto separado y se restaura la copia, **Then** la web pública, el acceso al panel y
   los archivos funcionan.
3. **Given** la documentación de operación, **When** se consulta, **Then** cubre instalación,
   variables, dominio y HTTPS, almacenamiento R2, administrador, copias, restauración,
   actualización con migraciones y recuperación del acceso.
4. **Given** el ensayo terminado, **When** se retira, **Then** el entorno de desarrollo no ha
   cambiado.

---

### User Story 4 - Cabeceras de seguridad y vistas de revisión (Priority: P2)

El navegador solo carga recursos de la propia web, el mapa de Wikiloc y las imágenes `https`
configuradas. Las vistas de revisión (`/pantallas`) no se publican en producción (decisión P5),
pero siguen disponibles para la revisión local.

**Why this priority**: reduce la superficie de ataque y cumple la decisión de lanzamiento.

**Independent Test**: recorrer todas las páginas y el panel sin ningún bloqueo de la política de
seguridad; pedir `/pantallas` con la configuración de producción y con la local.

**Acceptance Scenarios**:

1. **Given** la política de seguridad activa, **When** se recorren las páginas públicas, una prueba
   con mapa de Wikiloc y el panel (subida incluida), **Then** no hay bloqueos ni errores.
2. **Given** la configuración de producción, **When** se pide `/pantallas` o `/pantallas/admin`,
   **Then** responde «no encontrado».
3. **Given** la configuración local de revisión, **When** se piden, **Then** se muestran como hasta
   ahora, sin guardado.
4. **Given** un archivo subido, **When** se entrega, **Then** conserva su política propia de
   aislamiento.

---

### User Story 5 - Rendimiento (Priority: P2)

Las páginas cargan menos datos sin cambiar su aspecto. Las fuentes se sirven en un formato web
comprimido real (C4).

**Why this priority**: mejora la carga en móvil sin tocar el diseño.

**Independent Test**: medir el peso de las fuentes antes y después y comparar capturas.

**Acceptance Scenarios**:

1. **Given** las fuentes, **When** se sirven, **Then** su formato coincide con su extensión y pesan
   al menos un 40 % menos.
2. **Given** las capturas de referencia, **When** se comparan, **Then** el texto se ve igual.
3. **Given** recursos con huella, textos y fuentes, **When** se piden, **Then** se sirven
   comprimidos cuando procede y con la caché adecuada.

---

### User Story 6 - Limpieza (Priority: P3)

La persona que opera la web puede liberar los archivos subidos que ya no usa ningún contenido sin
riesgo de borrar uno en uso. El código no tiene restos sin uso y las pruebas no muestran avisos de
dependencias obsoletas.

**Why this priority**: mantenimiento; no afecta al visitante.

**Independent Test**: ejecutar el comando en modo listado y en modo borrado con confirmación,
comprobando que no toca archivos referenciados ni recientes.

**Acceptance Scenarios**:

1. **Given** archivos sin referencias con más de 24 horas, **When** se lista, **Then** aparecen sin
   borrarse.
2. **Given** la confirmación explícita, **When** se borra, **Then** desaparecen solo esos archivos
   (registro y contenido).
3. **Given** un archivo referenciado por cualquier contenido (también borradores) o subido hace
   menos de 24 horas, **When** se ejecuta, **Then** no se toca.
4. **Given** las pruebas, **When** se ejecutan, **Then** no aparecen avisos de dependencias
   obsoletas.

---

### Edge Cases

- Rutas con más segmentos de los previstos (por ejemplo, `/noticias/a/b`): «no encontrado».
- Identificadores con caracteres no válidos: «no encontrado», sin errores internos.
- Títulos y descripciones con caracteres especiales (comillas, `<`, `&`): se escapan.
- Detalle sin imagen propia: se usa la imagen general de la web.
- `/admin` y sus subrutas no cambian: siguen sirviendo el panel con `noindex`.
- Archivo referenciado solo desde un borrador: no se borra.
- Restauración sobre una base vacía (servidor nuevo): funciona igual.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Las rutas inexistentes y los detalles inexistentes o no publicados MUST responder con
  estado «no encontrado» (404) y la página «Este sendero no está en el mapa.».
- **FR-002**: Los detalles publicados de noticias, álbumes y pruebas (también por `/recorridos`)
  MUST incluir en el HTML inicial su título, su descripción, su imagen y su URL canónica. Los
  valores se escapan.
- **FR-003**: `/clasificaciones/{año}` MUST responder con éxito solo si hay clasificaciones
  publicadas de ese año.
- **FR-004**: Si el servicio de datos no responde, un detalle MUST servirse con los metadatos
  generales y con éxito, para que la página muestre su aviso de respaldo.
- **FR-005**: Los errores genéricos de la interfaz de datos (ruta o método inexistentes) MUST estar
  en español.
- **FR-006**: Las páginas públicas y el acceso al panel MUST tener 0 incumplimientos WCAG 2.1 A/AA
  en la revisión automática a 360 y 1440 px.
- **FR-007**: Los cambios visuales MUST limitarse a los de P4. Las páginas MUST NOT desbordar
  horizontalmente a 320, 340, 360, 768, 1024 y 1440 px.
- **FR-008**: La copia de seguridad MUST incluir la base de datos y los archivos locales, y la
  restauración MUST dejarlos idénticos. La restauración MUST pedir confirmación explícita.
- **FR-009**: MUST existir documentación de operación para un despliegue independiente que cubra
  los temas de US3/AS3, y MUST verificarse con un ensayo desde un clon limpio en un proyecto
  separado. No se despliega nada.
- **FR-010**: Una política de seguridad de contenido MUST permitir solo la propia web, el mapa de
  Wikiloc y las imágenes `https`, y MUST NOT romper páginas ni el panel. Los archivos entregados
  conservan su política propia.
- **FR-011**: `/pantallas` y sus subrutas MUST responder «no encontrado» con la configuración de
  producción y MUST estar disponibles con la configuración de revisión local.
- **FR-012**: Las fuentes MUST servirse en el formato que indica su extensión, con el mismo aspecto
  y al menos un 40 % menos de peso.
- **FR-013**: Un comando de operador MUST listar los archivos subidos sin referencias y con más de
  24 horas, y MUST borrarlos solo con una confirmación explícita. MUST NOT tocar archivos
  referenciados por cualquier contenido, incluidos los borradores.
- **FR-014**: El código sin uso MUST eliminarse y las pruebas MUST ejecutarse sin avisos de
  dependencias obsoletas.

### Key Entities *(include if feature involves data)*

- **Metadatos de página**: título, descripción, imagen y URL canónica de una página de detalle.
- **Archivo huérfano**: archivo subido que no aparece en ningún contenido y tiene más de 24 horas.
- **Copia de seguridad**: volcado de la base de datos más el paquete de archivos locales, con fecha.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de las rutas inexistentes y de los detalles inexistentes o no publicados
  probados responden 404; el 100 % de los detalles publicados responden con éxito y con sus
  metadatos propios.
- **SC-002**: 0 incumplimientos WCAG 2.1 A/AA en la revisión automática de todas las páginas
  públicas y del acceso al panel a 360 y 1440 px.
- **SC-003**: 0 páginas con desplazamiento horizontal a 320, 340, 360, 768, 1024 y 1440 px.
- **SC-004**: Tras restaurar una copia, el 100 % de las tablas y los archivos coinciden con los de
  la copia.
- **SC-005**: El ensayo de despliegue independiente sirve la web pública, el panel y los archivos
  solo con la documentación y la copia.
- **SC-006**: 0 bloqueos de la política de seguridad en el recorrido completo de la web y del panel.
- **SC-007**: Las fuentes pesan al menos un 40 % menos, sin diferencias visibles en el texto.
- **SC-008**: 0 archivos referenciados o recientes borrados por el comando de limpieza.

## Assumptions

- **Decisiones del propietario (2026-11-20)**:
  - P4: contraste AA con los cambios descritos.
  - P5: `/pantallas` se retira en producción y se mantiene en la revisión local.
- **Configuración de producción**: la del archivo Compose base. La revisión local activa
  `/pantallas` mediante una variable.
- **Antigüedad mínima de 24 horas**: evita borrar un archivo recién subido cuyo contenido aún no se
  ha guardado.
- **R2**: las copias de los archivos en R2 se gestionan en el propio bucket (versionado o réplica);
  se documentan, pero no se automatizan.
- **El ensayo de despliegue** se hace en esta máquina, en otro puerto y con otro nombre de
  proyecto; no se usa ningún servidor ni dominio real.
- **Fuera de alcance**: desplegar, cambiar el dominio o el DNS, tocar producción y rediseñar.
