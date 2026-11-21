# Feature Specification: Ajustes de la revisión del propietario

**Feature Branch**: `012-ajustes-revision`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Ajustes que pide el propietario tras revisar la web; se irán añadiendo historias. Historia 1: «las fotos se tienen que ver completas siempre». La foto de Adriana sale con la cabeza cortada en la portada y en /solidaridad. Historia 3 (P7): logotipo nuevo en la cabecera en lugar de la silueta y el texto en dos filas. Historia 4 (P8): «pon también el logo en el pie»."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Las fotos se ven siempre completas (Priority: P1)

Decisión P6 del propietario. Un visitante ve todas las fotos de la web completas, sin recortes,
en cualquier pantalla. La foto de Adriana, la de la portada («Mucho más que una carrera») y la de
`/solidaridad`, se ve entera, con la cabeza incluida. Lo mismo ocurre con las fotos de las pruebas,
las noticias y los álbumes. Los marcos conservan su tamaño y su posición, así que el diseño no se
mueve. El espacio que sobra alrededor de una foto se rellena con la propia foto muy oscurecida en
el verde de la paleta, de modo que no aparecen barras vacías.

**Why this priority**: es una instrucción directa del propietario sobre la imagen de Adriana, la
causa de la carrera. Un recorte que corta la cara no es aceptable.

**Independent Test**: abrir cada página con fotos a 320, 360, 768, 1024 y 1440 px y comprobar
que ninguna foto pierde ninguna parte de la imagen original, que los marcos siguen en su sitio y
que los textos superpuestos siguen siendo legibles.

**Acceptance Scenarios**:

1. **Given** la portada y `/solidaridad`, **When** se muestran a cualquier ancho, **Then** la foto
   de Adriana se ve completa, con la cabeza y los pies.
2. **Given** las tarjetas de las pruebas, la cabecera del detalle de una prueba, las tarjetas y la
   imagen de una noticia, las tarjetas y la portada de un álbum y la cuadrícula de fotos de un
   álbum, **When** se muestran, **Then** cada foto se ve completa y centrada en su marco.
3. **Given** una foto cuya proporción no coincide con la de su marco, **When** se muestra,
   **Then** el espacio sobrante muestra la misma foto oscurecida en el verde de la paleta, sin
   barras vacías.
4. **Given** los textos sobre las fotos (nombre y distancia de las pruebas, etiquetas de las
   noticias, «CADA PASO SUMA» y «CORREMOS POR ADRIANA»), **When** se muestran, **Then** siguen
   legibles y la revisión automática de accesibilidad AA da 0 incumplimientos.
5. **Given** las miniaturas de las listas del panel y de la cuadrícula de fotos de un álbum en el
   panel, **When** se muestran, **Then** también se ven completas.
6. **Given** cualquier página, **When** se compara con la versión anterior, **Then** los marcos
   ocupan el mismo sitio y la página no desborda horizontalmente.

---

### User Story 2 - Desplegar en la MV de la web anterior (Priority: P1)

El propietario despliega la web nueva en la máquina virtual de la nube donde hoy funciona la web
anterior (v2). Allí, un Caddy propio ocupa los puertos 80 y 443, sirve `trailpeñasagra.com` con
certificado automático y redirige `www` al dominio principal. El cambio debe hacerse:

- con HTTPS válido y renovado automáticamente;
- con la misma redirección de `www`;
- con el panel funcionando con un dominio que lleva «ñ»;
- con una vuelta atrás sencilla a la web anterior.

El propietario también necesita saber cómo entrar al panel una vez desplegada.

**Why this priority**: es el paso que pone la web en producción. Un fallo de certificado o de
acceso al panel la dejaría inservible.

**Independent Test**: ensayo completo en modo producción con HTTPS en esta máquina, desde un clon
limpio y con un dominio con «ñ» de prueba (`.localhost`, certificado de Caddy). Se comprueba:

- redirección de HTTP a HTTPS y de `www`;
- certificado, HSTS y acceso al panel con cookie `Secure`;
- un guardado real en el panel.

**Acceptance Scenarios**:

1. **Given** la configuración de producción con el dominio, **When** arranca, **Then** se sirve por
   HTTPS con certificado automático, HTTP redirige a HTTPS y las respuestas llevan HSTS.
2. **Given** `www.<dominio>`, **When** se visita, **Then** redirige permanentemente al dominio
   principal, conservando la ruta.
3. **Given** el dominio con «ñ», escrito en la configuración con «ñ» o en *punycode*, **When** se
   entra al panel y se guarda un cambio, **Then** funciona, porque el origen se compara siempre en
   *punycode*.
4. **Given** la guía de operación, **When** el propietario la sigue en la MV, **Then** sabe:
   - parar la web anterior y arrancar la nueva;
   - cargar los datos aprobados y las clasificaciones de 2026 desde los CSV de la v2;
   - crear su cuenta;
   - comprobar el despliegue;
   - volver a la web anterior si algo falla.
5. **Given** la web desplegada, **When** el propietario quiere entrar al panel, **Then** la guía le
   indica la dirección (`https://<dominio>/admin`), cómo crear la cuenta y cómo recuperar el
   acceso.

---

### User Story 3 - Logotipo nuevo en la cabecera (Priority: P1)

Decisión P7 del propietario: «en `datos_iniciales/new_logo.png` tienes el nuevo logo, para
sustituir el logo de la parte superior izquierda y el texto que está en dos filas, ya que el logo
es lo mismo y que se vea bien».

En la cabecera de la web pública, el logotipo nuevo sustituye al conjunto actual: la silueta de
Adriana más el texto en dos filas «TRAIL PEÑASAGRA / CORREMOS POR ADRIANA». El logotipo nuevo ya
reúne las montañas de Peñasagra, el nombre, el lema y la silueta. Se ve nítido en cualquier
pantalla y sigue llevando a la portada. El resto de la cabecera no se mueve: navegación, botón
«INSCRIPCIONES» y botón de menú.

**Why this priority**: es la imagen de la carrera en todas las páginas y es una instrucción
directa del propietario.

**Independent Test**: abrir la web a 320, 360, 768, 1024 y 1440 px y en los anchos de cambio de
diseño. Comprobar:

- que el logotipo nuevo aparece completo y nítido en la cabecera, en lugar de la silueta y el texto;
- que lleva a la portada;
- que el resto de la cabecera ocupa el mismo sitio que antes;
- que no hay desbordamientos.

**Acceptance Scenarios**:

1. **Given** cualquier página pública, **When** se muestra a cualquier ancho entre 320 y 1440 px,
   **Then**:
   - la cabecera muestra el logotipo nuevo completo, sin recortes ni deformación;
   - ya no aparecen la silueta ni el texto en dos filas.
2. **Given** la cabecera, **When** se compara con la versión anterior, **Then**:
   - la altura de la cabecera es la misma;
   - la navegación, el botón «INSCRIPCIONES» y el botón de menú están en el mismo sitio;
   - el logotipo no ocupa más ancho que la marca anterior.
3. **Given** una pantalla de alta densidad (retina), **When** se muestra el logotipo, **Then** se
   ve nítido, sin pixelado.
4. **Given** un lector de pantalla o la navegación por teclado, **When** llega al logotipo,
   **Then** lo anuncia como enlace a la portada de Trail Peñasagra, y la revisión automática de
   accesibilidad AA da 0 incumplimientos.
5. **Given** la barra lateral del panel (fondo verde oscuro), **When** se muestra, **Then**
   conserva su marca actual en blanco. El pie, que en esta historia también la conservaba, pasa a
   mostrar el logotipo con la US4 (decisión P8).

---

### User Story 4 - Logotipo nuevo también en el pie (Priority: P1)

Decisión P8 del propietario: «pon también el logo en el pie».

El pie de la web pública muestra el logotipo nuevo en lugar de la silueta y el texto en dos filas,
igual que la cabecera. El pie tiene fondo verde oscuro, así que se usa una versión en negativo del
mismo logotipo:

- el texto y las montañas, en blanco;
- la niña y las rayas, en su naranja original.

Sigue llevando a la portada y se ve nítido en cualquier pantalla.

**Why this priority**: es una instrucción directa del propietario, y la marca queda igual en la
cabecera y en el pie de todas las páginas.

**Independent Test**: abrir la web a 320, 360, 768, 1024 y 1440 px y en los anchos de cambio de
diseño del pie. Comprobar:

- que el pie muestra el logotipo completo y legible sobre el verde, en lugar de la silueta y el
  texto;
- que lleva a la portada;
- que las demás columnas del pie siguen en su sitio;
- que la cabecera no cambia y no hay desbordamientos.

**Acceptance Scenarios**:

1. **Given** cualquier página pública, **When** se muestra a cualquier ancho entre 320 y 1440 px,
   **Then**:
   - el pie muestra el logotipo nuevo completo, sin recortes ni deformación;
   - ya no aparecen en el pie la silueta ni el texto en dos filas.
2. **Given** el fondo verde oscuro del pie, **When** se muestra el logotipo, **Then**:
   - el texto y las montañas se ven en blanco;
   - la niña y las rayas conservan su naranja, con un contraste de al menos 3:1 con el fondo.
3. **Given** el pie, **When** se compara con la versión anterior, **Then**:
   - el logotipo no ocupa más ancho que la marca anterior ni que su columna;
   - las demás columnas conservan su posición horizontal y su ancho;
   - el resto de la primera columna solo baja lo que el logotipo es más alto que la marca anterior.
4. **Given** una pantalla de alta densidad, **When** se muestra el logotipo del pie, **Then** se
   ve nítido, sin pixelado.
5. **Given** un lector de pantalla o la navegación por teclado, **When** llega al logotipo del pie,
   **Then** lo anuncia como enlace a la portada de Trail Peñasagra, y la revisión automática de
   accesibilidad AA da 0 incumplimientos.
6. **Given** la cabecera, la barra lateral del panel y el icono del navegador, **When** se
   comparan con la versión anterior, **Then** no han cambiado.

### Edge Cases

- **Foto con la misma proporción que su marco**: se ve igual que antes, sin relleno visible.
- **Foto horizontal en un marco vertical, y al revés**: se ve completa; el relleno aparece arriba y
  abajo o a los lados.
- **Contenido sin foto propia**: la imagen de reserva (paisaje de la sierra) también se ve completa.
- **Foto que no carga**: el marco muestra el color de fondo de la paleta, sin errores.
- **Visor de fotos y vista previa de subida**: ya muestran la foto completa y no cambian.
- **Logotipo que no carga**: el enlace a la portada sigue funcionando y conserva su nombre
  accesible; la cabecera no cambia de altura. En el pie, el hueco del logotipo conserva su tamaño.
- **Pantallas muy estrechas (320 px)**: el logotipo se reduce lo necesario para que el botón
  «INSCRIPCIONES» y el de menú quepan sin desbordar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Ninguna foto de contenido MUST recortarse en ningún ancho entre 320 y 1440 px:
  foto de la causa, tarjetas y cabecera de las pruebas, tarjetas e imagen de las noticias,
  tarjetas y portada de los álbumes, cuadrícula de fotos de los álbumes y miniaturas del panel.
- **FR-002**: Cada marco MUST conservar su tamaño y su posición. La foto MUST verse completa y
  centrada dentro de él.
- **FR-003**: El espacio sobrante de un marco MUST rellenarse con la misma foto muy oscurecida en
  el verde de la paleta, nunca con barras vacías.
- **FR-004**: Los textos superpuestos MUST seguir legibles. Las páginas MUST tener 0
  incumplimientos WCAG 2.1 A/AA en la revisión automática y 0 desbordamientos horizontales.
- **FR-005**: Los logotipos, el visor de fotos y la vista previa de subida MUST NOT cambiar.
- **FR-006**: La configuración de producción MUST:
  - servir el dominio por HTTPS con certificado automático y renovado;
  - redirigir HTTP a HTTPS y `www.<dominio>` al dominio principal (301, conservando la ruta);
  - enviar `Strict-Transport-Security`.
- **FR-007**: Los orígenes permitidos del panel MUST normalizarse a *punycode*, para que el acceso
  funcione aunque la configuración escriba el dominio con «ñ».
- **FR-008**: La guía de operación MUST incluir:
  - la migración desde la web anterior en la misma MV (parada, arranque, datos y comprobaciones);
  - la vuelta atrás;
  - el acceso al panel: dirección, creación de la cuenta y recuperación.
- **FR-009**: La cabecera pública MUST mostrar el logotipo nuevo aportado por el propietario en
  lugar de la silueta y del texto en dos filas. El logotipo MUST verse completo, con su
  proporción original y sin recortes.
- **FR-010**: El logotipo MUST caber en la cabecera sin cambiar su altura, sin superar el ancho de
  la marca anterior y sin mover la navegación, el botón «INSCRIPCIONES» ni el botón de menú, en
  todos los anchos entre 320 y 1440 px.
- **FR-011**: El logotipo MUST servirse con resolución suficiente para pantallas de alta densidad
  y en un formato ligero, sin enviar el original de 393 KB.
- **FR-012**: El logotipo MUST seguir siendo un enlace a la portada con nombre accesible. La
  barra lateral del panel y el icono del navegador MUST NOT cambiar. El pie lo cambia la US4
  (FR-013–FR-016).
- **FR-013**: El pie público MUST mostrar el logotipo nuevo en lugar de la silueta y del texto en
  dos filas, en una versión en negativo para fondo oscuro derivada del original. La tinta oscura
  (texto y montañas) MUST pasar a blanco y el naranja MUST conservarse. El logotipo MUST verse
  completo, con su proporción original y sin recortes.
- **FR-014**: El logotipo del pie MUST NOT superar el ancho de la marca anterior ni el de su
  columna. La cabecera MUST NOT cambiar. Las demás columnas del pie MUST conservar su posición
  horizontal y su ancho. El resto de la primera columna MUST desplazarse hacia abajo como mucho
  lo que el logotipo es más alto que la marca anterior. 0 desbordamientos entre 320 y 1440 px.
- **FR-015**: El logotipo del pie MUST servirse con resolución suficiente para pantallas de alta
  densidad y en un formato ligero.
- **FR-016**: El logotipo del pie MUST ser un enlace a la portada con nombre accesible. La barra
  lateral del panel y el icono del navegador MUST NOT cambiar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 fotos recortadas en las páginas públicas y del panel a 320, 360, 768, 1024 y
  1440 px: se ve el 100 % de cada imagen.
- **SC-002**: La foto de Adriana se ve completa en la portada y en `/solidaridad` en todos los
  anchos.
- **SC-003**: 0 incumplimientos de accesibilidad AA y 0 desbordamientos en las páginas revisadas.
- **SC-004**: Los marcos de foto conservan su tamaño y su posición respecto a la versión anterior
  (diferencia de 0 px).
- **SC-005**: El ensayo en modo producción con HTTPS y un dominio con «ñ» da 0 fallos en:
  - las redirecciones;
  - el certificado;
  - HSTS;
  - el acceso al panel;
  - un guardado.
- **SC-006**: El logotipo nuevo se ve completo en el 100 % de las páginas públicas a 320, 360,
  768, 1024 y 1440 px y en los anchos de cambio de diseño. En ninguno queda rastro de la silueta
  ni del texto en dos filas.
- **SC-007**: La altura de la cabecera y la posición de la navegación, del botón «INSCRIPCIONES» y
  del botón de menú no cambian respecto a la versión anterior (diferencia de 0 px). Hay 0
  desbordamientos horizontales y 0 incumplimientos de accesibilidad AA.
- **SC-008**: Ninguna variante del logotipo pesa más de 50 KB. La que se descarga mide al menos el
  doble del tamaño en pantalla en las de alta densidad.
- **SC-009**: El logotipo en negativo se ve completo en el pie del 100 % de las páginas públicas a
  320, 360, 768, 1024 y 1440 px y en los anchos de cambio de diseño. En ningún pie queda la
  silueta ni el texto en dos filas.
- **SC-010**: La cabecera no cambia (diferencia de 0 px). Las columnas 2.ª a 4.ª del pie conservan
  su posición horizontal y su ancho (diferencia de 0 px). Hay 0 desbordamientos y 0
  incumplimientos de accesibilidad AA. La parte naranja tiene un contraste de al menos 3:1 con el
  fondo del pie.
- **SC-011**: Ninguna variante del logotipo del pie pesa más de 50 KB. La que se descarga mide al
  menos el doble del tamaño en pantalla en las de alta densidad.

## Assumptions

- **Fondos decorativos fuera de alcance**: el paisaje de la portada, el banner de la galería y el
  marcador del mapa son fondos con degradado, no fotos de contenido, y siguen como están. Si el
  propietario quiere aplicarles la misma regla, se añadirá como historia en esta feature.
- **Relleno**: el verde oscuro de la paleta (`--forest`) ya se usa en tarjetas y cabeceras.
- **Ampliable**: esta feature irá incorporando como historias nuevas los demás ajustes que pida el
  propietario tras su revisión.
- **Alcance del logotipo nuevo (US3)**: el propietario habla de la parte superior izquierda, es
  decir, la cabecera pública. El pie de página y la barra lateral del panel tienen fondo verde
  oscuro y usan la marca en blanco. El logotipo nuevo, con el texto oscuro, no se leería allí, así
  que conservan la marca actual. El icono del navegador también se mantiene: un logotipo
  apaisado no se distingue a 16 px. Si el propietario quiere también una versión clara del
  logotipo para esos fondos, se añadirá como historia. *(Actualizado por la US4: el propietario
  pidió el logotipo también en el pie, decisión P8.)*
- **Tamaño del logotipo**: lo limita la altura de la cabecera, que no cambia. El nombre
  «TRAIL PEÑASAGRA» dentro del logotipo queda aproximadamente del mismo tamaño que el texto
  anterior.
- **Versión en negativo (US4)**: el propietario no ha aportado una versión para fondo oscuro. Se
  deriva del original sin redibujar nada: solo cambia el color de la tinta oscura a blanco. Si el
  propietario aporta una versión oficial, basta con sustituir los archivos.
- **Tamaño del logotipo en el pie (US4)**: el ancho es el de la marca anterior (silueta, separación
  y texto), o el de la columna si es menor. Con la proporción del logotipo, queda algo más alto que
  la marca anterior. Por eso el párrafo y el enlace a Instagram de la primera columna bajan esa
  diferencia. El pie solo crece donde la primera columna es la más alta.
- **Barra lateral del panel (US4)**: el propietario habla del pie. La barra lateral del panel
  conserva su marca. Si la quiere también allí, se añadirá como historia.
