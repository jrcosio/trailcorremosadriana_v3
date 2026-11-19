# Feature Specification: Base del proyecto

**Feature Branch**: `001-base-proyecto`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "Base del proyecto (short-name: base-proyecto). Crear la base ejecutable de la nueva web de «Trail Peñasagra — Corremos por Adriana» fuera de datos_iniciales: la web pública y las vistas existentes de la propuesta aprobada se sirven desde la nueva infraestructura con exactamente la misma apariencia, rutas y textos; existe un servicio de API propio con comprobaciones de salud (viva) y disponibilidad (base de datos accesible y esquema al día); existe una base de datos PostgreSQL persistente con migraciones versionadas aplicadas como paso explícito; todo arranca en local con Docker Compose con un solo flujo documentado y sin credenciales de producción; la web sigue mostrando el contenido público actual (carreras de referencia 2026, noticia, álbumes históricos, patrocinadores, reglamento, contacto) obtenido de la API mediante el contrato transitorio de contenido; las rutas públicas estáticas tienen título y descripción propios; el proyecto compila y funciona sin la carpeta datos_iniciales; se conservan procedencia y licencias de fuentes, imágenes y código reutilizado. Fuera de alcance: login real (002), subida de archivos (003) y edición persistente de contenidos (004-010)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visitar la web pública con la apariencia aprobada (Priority: P1)

Una persona que visita la web (corredor, familia, colaborador) abre cualquiera de las páginas
públicas documentadas y ve exactamente las mismas pantallas, textos, fotografías, tipografías y
comportamientos que la propuesta aprobada, ahora servidas por la nueva infraestructura del
proyecto.

**Why this priority**: Es el producto visible. Sin esta base no hay nada que conectar en las
features siguientes, y la constitución exige preservar el diseño aprobado.

**Independent Test**: Arrancar el entorno local, abrir cada URL del mapa de pantallas
directamente y comparar con la referencia visual aprobada a 360, 768, 1024 y 1440 px.

**Acceptance Scenarios**:

1. **Given** el entorno local en marcha, **When** se abre `/`, **Then** se ve el título literal
   «TRAIL PENASAGRA» (TRAIL blanco, PENASAGRA naranja), la frase «Corremos por Adriana.» ampliada
   con la silueta naranja, el contador sin rótulo encima y el botón superior «INSCRIPCIONES».
2. **Given** el entorno en marcha, **When** se abre directamente o se recarga cualquiera de las
   rutas públicas de la tabla de FR-001, **Then** la página correspondiente se muestra sin error.
3. **Given** el entorno en marcha, **When** se abre `/recorridos`, **Then** se muestra la misma
   pantalla que `/carreras` (URL histórica de producción).
4. **Given** el entorno en marcha, **When** se abre una ruta que no existe, **Then** se muestra la
   pantalla «Este sendero no está en el mapa.».
5. **Given** la próxima edición sin fecha confirmada, **When** se abre `/`, **Then** el contador
   muestra guiones y «Fecha por confirmar», sin ninguna fecha inventada.

---

### User Story 2 - Arrancar y comprobar el entorno local (Priority: P1)

La persona responsable técnica clona el repositorio (sin la carpeta de referencia
`datos_iniciales`), sigue un único flujo documentado para construir los servicios, aplicar el
esquema de datos como paso explícito y arrancar, y comprueba que el servicio está vivo y
disponible.

**Why this priority**: Todas las features posteriores dependen de un entorno reproducible con
base de datos real; sin él no se puede verificar persistencia ni integración.

**Independent Test**: En una copia limpia del repositorio sin `datos_iniciales`, ejecutar los
pasos documentados y consultar las comprobaciones de salud y disponibilidad.

**Acceptance Scenarios**:

1. **Given** una copia limpia sin `datos_iniciales` ni archivo de configuración real, **When** se
   siguen los pasos documentados, **Then** los servicios se construyen y arrancan usando solo
   valores de desarrollo del archivo de ejemplo.
2. **Given** los servicios arrancados pero el esquema sin aplicar, **When** se consulta la
   disponibilidad, **Then** responde «no disponible» indicando que hay migraciones pendientes.
3. **Given** el esquema aplicado con el paso explícito, **When** se consulta la disponibilidad,
   **Then** responde «disponible».
4. **Given** la base de datos detenida, **When** se consultan las comprobaciones, **Then** la de
   salud sigue respondiendo «viva» y la de disponibilidad responde «no disponible» sin exponer
   detalles internos ni credenciales.
5. **Given** el esquema aplicado, **When** se reinician todos los servicios, **Then** la
   disponibilidad vuelve a «disponible» sin repetir el paso de esquema (los datos persisten).

---

### User Story 3 - Contenido público servido por el servicio propio (Priority: P2)

Las pantallas públicas obtienen el contenido publicado (edición, carreras de referencia 2026,
noticia, álbumes históricos, patrocinadores, reglamento y contacto) del servicio propio mediante
el contrato transitorio de contenido que ya consumen, de modo que las features siguientes puedan
sustituir cada sección por datos persistentes sin tocar la apariencia.

**Why this priority**: Conecta frontend y servicio desde el primer día y fija el contrato que
irán rellenando las features 004–010.

**Independent Test**: Consultar el contrato público de contenido y comprobar que la web lo
muestra; detener el servicio y comprobar el comportamiento de respaldo.

**Acceptance Scenarios**:

1. **Given** el servicio disponible, **When** se consulta el contenido público, **Then** devuelve
   solo elementos publicados con la forma que consumen las pantallas, la edición 2027 sin fecha y
   las inscripciones cerradas.
2. **Given** el servicio disponible, **When** se revisa el contenido público, **Then** no aparece
   ninguno de los datos de prueba detectados (edición «2028», silueta como foto de la 27K,
   colaborador «boc», párrafo «PRUEBA» del reglamento).
3. **Given** el servicio de contenido no responde, **When** se abre cualquier página pública,
   **Then** se muestra el contenido de referencia con el aviso existente «No se han podido
   comprobar las últimas novedades» y nunca una página en blanco.
4. **Given** una petición de contenido privado (borradores) sin sesión, **When** se realiza,
   **Then** se rechaza como no autorizada.

---

### User Story 4 - Títulos y descripciones propios por página (Priority: P2)

Quien comparte un enlace o encuentra la web en un buscador ve un título y una descripción
específicos de cada página pública estática, como en la web actual de producción.

**Why this priority**: Conserva una capacidad existente de producción (metadatos por página) que
la propuesta había perdido.

**Independent Test**: Solicitar cada ruta pública estática sin ejecutar scripts y leer su título,
descripción y metadatos para compartir.

**Acceptance Scenarios**:

1. **Given** el entorno en marcha, **When** se solicita `/reglamento` sin ejecutar scripts,
   **Then** el documento devuelto ya contiene un título y una descripción propios de esa página y
   metadatos para compartir con imagen.
2. **Given** dos rutas públicas estáticas distintas, **When** se comparan sus títulos, **Then**
   son diferentes.

---

### User Story 5 - Vistas de revisión y acceso al panel (Priority: P3)

Una persona revisora abre `/pantallas` y las vistas de diseño `/pantallas/admin/...`, que muestran
las pantallas del panel con datos de referencia sin guardar nada; y `/admin` muestra la pantalla
de acceso, que todavía no concede acceso porque el servicio de autenticación llega en la feature
002.

**Why this priority**: Conserva las vistas de revisión existentes; el panel real se completa más
adelante.

**Independent Test**: Abrir las vistas de diseño, intentar guardar y comprobar que no se persiste
nada; abrir `/admin` e intentar acceder.

**Acceptance Scenarios**:

1. **Given** `/pantallas/admin/noticias/nuevo`, **When** se pulsa guardar, **Then** se informa de
   que es una vista de diseño en la que no se guardan cambios reales y no se envía ninguna
   escritura al servicio.
2. **Given** `/admin` sin servicio de autenticación, **When** se intenta acceder con cualquier
   usuario y contraseña, **Then** se muestra un error claro y nunca se concede acceso ni se simula
   éxito.

---

### Edge Cases

- El servicio de contenido devuelve un error o tarda: la web muestra el contenido de referencia y
  el aviso, sin bloquearse.
- La base de datos está caída o con esquema pendiente: la disponibilidad lo indica; la salud no
  depende de la base de datos.
- Se intenta arrancar sin archivo de configuración real: se usan los valores de desarrollo del
  ejemplo; en ningún caso se requieren credenciales de producción.
- Se elimina o falta la carpeta `datos_iniciales`: la construcción y el arranque funcionan igual.
- Anchuras de 360 px: «PENASAGRA», la frase solidaria y las URLs largas no desbordan la página.
- Rutas de detalle con identificador inexistente (`/noticias/xyz`, `/galeria/xyz`,
  `/carreras/xyz`): pantalla de no encontrado.
- Un rastreador solicita `/admin`, `/api` o `/pantallas`: quedan excluidos de la indexación.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La web MUST servir todas las pantallas públicas y de revisión del mapa aprobado
  (`docs/referencia/03_MAPA_PANTALLAS.md`): `/`, `/carreras`, `/carreras/trail-27k`,
  `/carreras/speed-14k`, `/carreras/familiar-7k`, `/inscripciones`, `/noticias`,
  `/noticias/{id}`, `/galeria`, `/galeria/{id}`, `/clasificaciones`, `/reglamento`,
  `/solidaridad`, `/patrocinadores`, `/contacto`, `/pantallas`, `/pantallas/admin/...` y `/admin`;
  además del alias histórico `/recorridos` (y `/recorridos/{id}`).
- **FR-002**: Cada ruta de FR-001 MUST funcionar al abrirse directamente y al recargar.
- **FR-003**: Las pantallas MUST conservar los textos, estilos, tipografías, imágenes,
  composición y comportamientos de la propuesta aprobada, incluidas las decisiones de
  `12_DECISIONES_APROBADAS.md`.
- **FR-004**: Las pantallas públicas MUST obtener el contenido publicado del servicio propio
  mediante el contrato transitorio de contenido, con la forma de datos que ya consumen.
- **FR-005**: El contenido público inicial MUST ser el contenido de referencia aprobado: edición
  2027 sin fecha, inscripciones cerradas con su mensaje, tres carreras de referencia 2026, noticia
  «proxima-edicion», tres álbumes históricos con enlace externo, ocho patrocinadores sin web,
  ningún colaborador, reglamento resumen 2026 y datos de contacto; y MUST excluir los datos de
  prueba D1–D4 de `DISCREPANCIAS.md`.
- **FR-006**: El contrato público MUST devolver solo elementos publicados; la variante con
  borradores MUST rechazar peticiones sin sesión de administrador.
- **FR-007**: Si el contrato de contenido no responde o falla, la web MUST mostrar el contenido de
  referencia y el aviso existente, nunca una página vacía.
- **FR-008**: El servicio MUST ofrecer una comprobación de salud que responda mientras el proceso
  esté vivo, sin depender de la base de datos.
- **FR-009**: El servicio MUST ofrecer una comprobación de disponibilidad que responda
  «disponible» solo si la base de datos es accesible y su esquema está en la última versión; en
  otro caso responde «no disponible» con un motivo genérico (base de datos inaccesible o
  migraciones pendientes) sin datos internos ni credenciales.
- **FR-010**: El esquema de datos MUST estar versionado y aplicarse solo mediante un paso
  explícito y documentado; el servicio MUST NOT modificar el esquema al arrancar.
- **FR-011**: Los datos de la base MUST persistir entre reinicios de los servicios.
- **FR-012**: El entorno local MUST arrancar con un único flujo documentado (construir, aplicar
  esquema, arrancar, comprobar) usando solo valores de desarrollo; la configuración MUST
  documentarse por nombre de variable en un archivo de ejemplo sin valores secretos reales.
- **FR-013**: En la configuración por defecto, la base de datos MUST NOT ser accesible desde fuera
  de la red interna de los servicios; solo se publica la entrada web.
- **FR-014**: La web y el servicio MUST servirse bajo el mismo origen público (las rutas del
  servicio y de archivos cuelgan del mismo dominio que la web).
- **FR-015**: El proyecto MUST construirse y funcionar sin la carpeta `datos_iniciales`, que MUST
  quedar excluida del control de versiones y del contexto de construcción de contenedores.
- **FR-016**: Cada ruta pública estática MUST entregar en el documento inicial un título y una
  descripción propios y metadatos para compartir (título, descripción, imagen); para las rutas que
  existen en producción se conservan sus títulos.
- **FR-017**: `/admin`, `/api` y `/pantallas` MUST quedar excluidos de la indexación de buscadores.
- **FR-018**: Las vistas de diseño `/pantallas/admin/...` MUST usar datos de referencia y MUST NOT
  enviar escrituras.
- **FR-019**: Hasta la feature 002, `/admin` MUST mostrar la pantalla de acceso y cualquier
  intento de acceso MUST terminar en un error claro, sin conceder acceso ni simular éxito.
- **FR-020**: Las reglas de negocio ya existentes en la propuesta para el enlace del Dorsal
  Solidario y la lectura de CSV de clasificaciones MUST conservar su comportamiento, verificado
  con sus comprobaciones de aceptación existentes.
- **FR-021**: El repositorio MUST documentar la procedencia y licencia de las fuentes
  tipográficas, imágenes y código reutilizados.

### Key Entities *(include if feature involves data)*

- **Contenido público (transitorio)**: conjunto publicado que consumen las pantallas: ajustes de la
  edición (año, fecha, contador, apertura, mensaje, URL solidaria, contacto), carreras, noticias,
  álbumes, clasificaciones, patrocinadores, colaboradores y reglamento. En esta feature es de solo
  lectura y procede de una semilla curada; las features 004–010 lo trasladan a datos persistentes.
- **Versión del esquema**: identifica qué cambios de estructura de datos están aplicados; la
  disponibilidad la compara con la última versión conocida.
- **Configuración del entorno**: variables con nombre documentado (conexión a la base de datos,
  origen público, cookies, límites, almacenamiento) con valores de desarrollo de ejemplo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de las rutas de FR-001 se abren directamente y al recargar en el entorno
  local sin error.
- **SC-002**: En la comparación visual con la referencia aprobada a 360, 768, 1024 y 1440 px de
  las pantallas Inicio, Carreras, detalle de carrera, Inscripciones, Solidaridad, Patrocinadores y
  Contacto no hay diferencias de textos, imágenes ni composición (salvo las derivadas de excluir
  los datos de prueba D1–D4 de la referencia publicada), y ninguna presenta desplazamiento
  horizontal de página.
- **SC-003**: Partiendo de una copia limpia sin `datos_iniciales`, una persona técnica deja el
  entorno «disponible» siguiendo solo la documentación en menos de 15 minutos (con descargas de
  red disponibles).
- **SC-004**: Tras reiniciar todos los servicios, la disponibilidad vuelve a «disponible» en menos
  de 60 segundos sin repetir el paso de esquema.
- **SC-005**: Con la base de datos detenida, la disponibilidad informa «no disponible» en menos de
  5 segundos y la salud sigue respondiendo.
- **SC-006**: Ninguno de los 4 datos de prueba (D1–D4) aparece en la web pública.
- **SC-007**: Cero archivos de `datos_iniciales`, secretos o archivos de configuración real en el
  control de versiones y en las imágenes de contenedor construidas.
- **SC-008**: Las 11 rutas públicas estáticas (`/`, `/carreras`, `/recorridos`, `/inscripciones`,
  `/noticias`, `/galeria`, `/clasificaciones`, `/reglamento`, `/solidaridad`, `/patrocinadores`,
  `/contacto`) tienen títulos distintos entre sí en el documento inicial.

## Assumptions

- La tecnología la fija la constitución del proyecto (sección «Restricciones técnicas»); esta
  especificación describe solo comportamiento y aceptación.
- En esta feature el contenido público es de solo lectura y procede de una semilla curada
  versionada en el repositorio, derivada de la propuesta aprobada y de la exportación publicada
  sin los datos de prueba; no hay escrituras de contenido hasta las features 004–010.
- La próxima edición es 2027 sin fecha (decisión del propietario P1); las carreras muestran datos
  de referencia 2026.
- Las clasificaciones 2026 se importan en la feature 006; hasta entonces `/clasificaciones`
  muestra su estado vacío aprobado. `/clasificaciones/{año}` se añade en la feature 006.
- La pantalla de no encontrado se muestra para rutas desconocidas; el código HTTP 404 real y los
  metadatos de páginas de detalle se completan en la feature 011 (DISCREPANCIAS U4, U5).
- `/pantallas` se mantiene como índice de revisión fuera de la navegación hasta la decisión de la
  feature 011 (U6).
- Se dispone de un entorno de contenedores local y de acceso a internet para descargar imágenes y
  dependencias; la referencia visual publicada de la propuesta está accesible para comparar.
