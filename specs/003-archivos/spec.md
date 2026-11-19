# Feature Specification: Archivos

**Feature Branch**: `003-archivos`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Archivos (short-name: archivos). Almacenamiento local/S3, subida, validación, entrega de imágenes y GPX, y reutilización de los recursos existentes. La organización sube fotografías, logotipos, GPX y PDF desde el panel; el servidor valida tipo, tamaño y contenido, genera claves propias, guarda referencias y metadatos, y los entrega a la web pública con caché y sin riesgo de ejecución. Desarrollo local sin credenciales de producción; producción en Cloudflare R2 mediante su API compatible con S3."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Subir archivos desde el panel (Priority: P1)

Una persona de la organización, con sesión iniciada, elige una fotografía, un logotipo, un GPX o
un PDF en un formulario del panel. El servidor la valida y la guarda. El formulario recibe la
referencia del archivo para mostrarlo y asociarlo al contenido.

**Why this priority**: noticias, galería, carreras y entidades necesitan imágenes y GPX propios
(features 004–009).

**Independent Test**: con sesión, subir un archivo de cada tipo admitido y uno de cada tipo
rechazado, y comprobar la respuesta, la referencia y que el archivo se recupera después.

**Acceptance Scenarios**:

1. **Given** una sesión válida, **When** se sube un JPG, PNG o WebP de hasta 10 MB, **Then** se
   devuelve una referencia `/media/…` y el archivo queda guardado.
2. **Given** una sesión válida, **When** se sube un GPX válido o un PDF, **Then** se acepta y se
   devuelve su referencia.
3. **Given** un archivo de más de 10 MB, **When** se sube, **Then** se rechaza como «demasiado
   grande» (413) y no se guarda nada.
4. **Given** un SVG, un ejecutable, un HTML o un archivo cuyo contenido no corresponde a su tipo
   (por ejemplo, texto renombrado a `.jpg`), **When** se sube, **Then** se rechaza (400) y no se
   guarda nada.
5. **Given** ninguna sesión, otro origen o sin comprobante CSRF, **When** se intenta subir,
   **Then** se rechaza con la protección de la feature 002 (401/403).

---

### User Story 2 - Entregar archivos a la web (Priority: P1)

Cualquier visitante ve las imágenes y descarga los GPX o PDF referenciados en la web, con una
dirección estable que se puede guardar en caché. Ningún archivo subido puede ejecutar código en
el navegador ni suplantar una página de la web.

**Why this priority**: sin entrega no hay imágenes ni GPX públicos.

**Independent Test**: pedir las referencias devueltas en US1 sin sesión y comprobar el tipo, la
caché, la validación condicional y que una clave inexistente da 404.

**Acceptance Scenarios**:

1. **Given** una imagen subida, **When** un visitante pide su referencia, **Then** recibe los
   bytes exactos con su tipo de imagen y caché de larga duración.
2. **Given** un GPX subido, **When** se pide, **Then** se descarga como archivo GPX con un nombre
   de archivo descriptivo.
3. **Given** una referencia con clave inexistente o con caracteres no válidos, **When** se pide,
   **Then** se responde «no encontrado» (404) sin revelar rutas internas.
4. **Given** una petición repetida con la misma versión del archivo, **When** se pide de nuevo,
   **Then** el servidor responde «no modificado» (304) sin reenviar los bytes.
5. **Given** cualquier archivo entregado, **When** el navegador lo abre directamente, **Then** no
   puede ejecutar scripts ni interpretarse como un tipo distinto del declarado.

---

### User Story 3 - Almacenamiento configurable (Priority: P2)

El operador elige por configuración dónde se guardan los archivos: un almacenamiento local
persistente para desarrollo o un servicio compatible con S3 (Cloudflare R2 en producción). La web
y el panel se comportan igual en ambos casos y las credenciales del almacenamiento nunca llegan
al navegador.

**Why this priority**: permite desarrollar sin credenciales de producción y desplegar en R2.

**Independent Test**: ejecutar las mismas pruebas de subida y entrega con el almacenamiento local
y con un servicio compatible con S3 de desarrollo.

**Acceptance Scenarios**:

1. **Given** el almacenamiento local, **When** se suben archivos y se reinician los servicios,
   **Then** los archivos siguen disponibles.
2. **Given** un servicio compatible con S3 configurado, **When** se suben y se piden archivos,
   **Then** el comportamiento es idéntico al local.
3. **Given** cualquier configuración, **When** se inspeccionan las respuestas al navegador,
   **Then** no aparecen credenciales ni direcciones internas del almacenamiento.

---

### User Story 4 - Recursos existentes y referencias (Priority: P3)

Las fotografías, logotipos, fuentes y la silueta que ya incluye la web siguen sirviéndose como
recursos estáticos en sus rutas actuales (`/reused/…`, `/images/…`, `/fonts/…`). Las referencias
de contenido pueden apuntar a estos recursos o a archivos subidos (`/media/…`).

**Why this priority**: conserva los recursos aprobados sin duplicarlos. Los recursos de producción
que todavía no tienen uso se incorporan en la feature que los necesite.

**Independent Test**: comprobar que los recursos estáticos existentes responden y que una
referencia `/media/…` válida y una `/reused/…` son aceptadas por las reglas de referencia.

**Acceptance Scenarios**:

1. **Given** la web en marcha, **When** se piden los recursos estáticos existentes, **Then** se
   sirven sin cambios.
2. **Given** las reglas de referencias, **When** una referencia apunta a `/reused/…`, `/media/…`
   o a una dirección `https://`, **Then** se acepta; cualquier otra forma se rechaza.

---

### Edge Cases

- Nombre original con rutas, caracteres especiales o muy largo: se conserva solo como dato
  informativo saneado; nunca determina dónde se guarda el archivo.
- Petición sin archivo o con varios campos: se rechaza con un mensaje claro.
- Interrupción a mitad de subida o fallo del almacenamiento: no queda ningún registro que apunte a
  un archivo inexistente y se informa del error (503) sin simular éxito.
- Imagen con extensión distinta de su contenido real (PNG llamado `.jpg`): se acepta según su
  contenido real y se guarda con la extensión correcta.
- GPX con entidades XML externas o expansiones maliciosas: se rechaza sin procesarlas.
- El mismo archivo subido dos veces: se guardan dos copias independientes con claves distintas
  (sin deduplicar).
- Archivo subido pero no asociado a ningún contenido (por ejemplo, porque el guardado falló):
  permanece disponible. El borrado de archivos sin uso queda fuera de esta feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Solo una sesión de administración válida MUST poder subir archivos, con la
  protección de escrituras de la feature 002 (origen, sesión y CSRF).
- **FR-002**: Los tipos admitidos MUST ser JPEG, PNG, WebP, PDF y GPX. El tipo MUST determinarse
  por el contenido real, no por el nombre ni por lo que declare el navegador. SVG, HTML y
  cualquier otro tipo MUST rechazarse.
- **FR-003**: El tamaño máximo por archivo MUST ser 10 MB (configurable); por encima se responde
  413 sin guardar nada.
- **FR-004**: Un GPX MUST ser XML bien formado con raíz `gpx`, sin DTD ni entidades.
- **FR-005**: El servidor MUST generar una clave propia, aleatoria e imposible de adivinar, con la
  extensión del tipo detectado. Ninguna parte de la clave procede del nombre original.
- **FR-006**: Por cada archivo guardado MUST registrarse su clave, tipo, tamaño, huella de
  contenido, nombre original saneado, fecha de alta y cuenta que lo subió.
- **FR-007**: La respuesta a una subida correcta MUST ser la referencia pública `/media/<clave>`,
  compatible con el panel existente.
- **FR-008**: La entrega pública MUST validar el formato de la clave (404 si no es válido o no
  existe), servir el tipo registrado e incluir caché inmutable de larga duración, etiqueta de
  versión y respuesta «no modificado» a peticiones condicionales.
- **FR-009**: Toda entrega MUST impedir la ejecución de scripts y la interpretación con otro tipo
  (política de contenido aislada y prohibición de detección de tipo). Los GPX MUST entregarse
  como descarga con un nombre descriptivo.
- **FR-010**: El almacenamiento MUST ser configurable: local persistente o compatible con S3
  (Cloudflare R2 en producción). Las credenciales MUST permanecer en el servidor.
- **FR-011**: Si el almacenamiento falla, MUST NOT quedar ningún registro que apunte a un archivo
  inexistente y la subida MUST responder un error de servicio (503).
- **FR-012**: Los archivos guardados MUST sobrevivir a reinicios de los servicios.
- **FR-013**: Los recursos estáticos existentes (`/reused/`, `/images/`, `/fonts/`, `/templates/`)
  MUST seguir sirviéndose sin cambios.
- **FR-014**: Las reglas de referencia de contenido MUST aceptar solo valores vacíos, `/reused/…`,
  `/media/<clave válida>` o `https://` sin credenciales, de hasta 2200 caracteres.
- **FR-015**: Los archivos MUST NOT borrarse físicamente en esta feature. Retirar un contenido no
  borra su archivo (DOC 14). La limpieza de archivos sin uso queda para la feature 011.
- **FR-016**: Las copias de seguridad MUST incluir los archivos guardados en el almacenamiento
  local.

### Key Entities *(include if feature involves data)*

- **Archivo**: objeto subido. Tiene clave única (aleatoria más extensión), tipo de contenido,
  tamaño en bytes, huella SHA-256, nombre original saneado, fecha de alta y cuenta que lo subió.
  Los bytes viven en el almacenamiento y la base de datos solo guarda la referencia y los
  metadatos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de los tipos admitidos (5) se aceptan y el 100 % de los tipos de prueba
  rechazados (SVG, HTML, ejecutable, texto renombrado, GPX con entidades) se rechazan sin dejar
  rastro.
- **SC-002**: Un archivo subido se recupera byte a byte idéntico, con el mismo resultado en el
  almacenamiento local y en el compatible con S3.
- **SC-003**: Los archivos siguen disponibles tras reiniciar todos los servicios.
- **SC-004**: Una imagen de 10 MB se sube y queda disponible en menos de 10 segundos en el entorno
  local.
- **SC-005**: Cero credenciales del almacenamiento o rutas internas en respuestas al navegador.
- **SC-006**: La segunda petición condicional de un archivo responde 304 sin cuerpo.

## Assumptions

- Los archivos son públicos por diseño: la web los muestra y su clave es imposible de adivinar.
  Un archivo asociado a un borrador no aparece en ningún contenido público mientras no se
  publique, pero conocer su clave basta para descargarlo. Se acepta porque las claves no se
  pueden enumerar (decisión documentada; DOC 14 pide definir este acceso).
- La entrega se hace a través de la API en el mismo origen (`/media/…`), también con R2. Una
  distribución directa por CDN se puede valorar en la feature 011.
- No hay redimensionado ni conversión de imágenes. Se mantiene el límite de 10 MB del prototipo.
- Los recursos de producción aún sin uso (camiseta, logo de la asociación, imágenes infantiles)
  se incorporan cuando una feature los necesite. La noticia de 2026 y su imagen llegan en la 007.
- Los dos archivos `/media/` de la exportación son datos de prueba (D2, D3) y no se importan.
