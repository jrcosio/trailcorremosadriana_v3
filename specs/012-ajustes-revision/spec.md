# Feature Specification: Ajustes de la revisión del propietario

**Feature Branch**: `012-ajustes-revision`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Ajustes que pide el propietario tras revisar la web; se irán añadiendo historias. Historia 1: «las fotos se tienen que ver completas siempre». La foto de Adriana sale con la cabeza cortada en la portada y en /solidaridad. Historia 3 (P7): logotipo nuevo en la cabecera en lugar de la silueta y el texto en dos filas. Historia 4 (P8): «pon también el logo en el pie». Historia 5 (P9): cambiar la frase del pie «Hecho con pasión por JR BLANCO · Hackers Cosío» por «Hecho por la Escuela Hacker Cosío». Historia 6 (P10): en la clasificación, que los 3 primeros, además del 1, 2 y 3 en negrita, se diferencien con un color suave cada uno («lo que tú decidas que queda más visual para el podio»). Historia 7: «en el panel del admin, si la pantalla está más pequeña, no tiene scroll el panel de opciones». Historia 8 (P11): «el logo, es cierto que hay que poner el oficial también aquí» (panel de administración). Historia 9: «sí, corrige el contraste del panel» (incumplimientos AA hallados con la sesión iniciada; decisión P4). Historia 10 (P12): «si cambio a femenino no me identifica a las tres campeonas»; podio de las tres primeras chicas y los tres primeros chicos de todas las pruebas, y también por categoría. Historia 11 (P13): «en la home, como título principal en grande, pone PENASAGRA y es PEÑASAGRA; repasa para que todo esté bien escrito». Historia 12: «un deploy.sh que, al descargar el repositorio en la máquina virtual y ejecutarlo, lo haga todo, y el .env para copiarlo directamente en la MV»."

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

---

### User Story 5 - Nueva frase de autoría en el pie (Priority: P1)

Decisión P9 del propietario: cambiar la frase del pie «Hecho con pasión por JR BLANCO · Hackers
Cosío» por «Hecho por la Escuela Hacker Cosío».

**Why this priority**: es una instrucción directa del propietario y la frase aparece en todas las
páginas públicas.

**Independent Test**: abrir varias páginas públicas a 320, 360, 768, 1024 y 1440 px. Comprobar
que la línea inferior del pie dice «Hecho por la Escuela Hacker Cosío» y que no quedan restos de
la frase anterior.

**Acceptance Scenarios**:

1. **Given** cualquier página pública, incluida la de página no encontrada, **When** se muestra a
   cualquier ancho entre 320 y 1440 px, **Then**:
   - la línea inferior del pie dice exactamente «Hecho por la Escuela Hacker Cosío»;
   - ya no aparecen «Hecho con pasión», «JR BLANCO» ni «Hackers Cosío».
2. **Given** la línea inferior del pie, **When** se compara con la versión anterior, **Then**:
   - el aviso «© año Asociación Peñasagra» no cambia;
   - la frase nueva conserva el color y el tamaño de letra de esa línea;
   - el resto del pie y la cabecera no se mueven.
3. **Given** la revisión automática de accesibilidad, **When** se ejecuta en las páginas públicas,
   **Then** da 0 incumplimientos AA y 0 desbordamientos horizontales.

---

### User Story 6 - Podio destacado en las clasificaciones (Priority: P1)

Decisión P10 del propietario: en las clasificaciones, los tres primeros no solo deben llevar el
puesto en negrita. Cada uno debe distinguirse con un color suave propio: «el primero verdecito, el
segundo otro color suave y el tercero lo mismo. Lo de verde es por decir algo, pero lo que tú
decidas que queda más visual para el podio».

Se eligen los colores de las medallas, que todo el mundo asocia al podio: oro, plata y bronce, en
tonos suaves.

- La fila de cada uno de los tres primeros lleva un fondo suave de su color.
- Tiene una franja a la izquierda del mismo color, más intenso.
- El puesto aparece dentro de una medalla redonda de ese color.

**Why this priority**: es una instrucción directa del propietario y mejora la lectura de los
resultados oficiales.

**Independent Test**: abrir `/clasificaciones/2026` a 320, 360, 768, 1024 y 1440 px. Comprobar:

- que las filas del 1.º, 2.º y 3.º de cada carrera se distinguen con tres colores diferentes;
- que el resto de filas, la tabla y la página no cambian.

**Acceptance Scenarios**:

1. **Given** una clasificación publicada, **When** se muestra la página con los primeros puestos,
   **Then**:
   - la fila del 1.º lleva un fondo suave dorado, la del 2.º uno plateado y la del 3.º uno
     bronce, distintos entre sí, del blanco y del gris de las filas alternas;
   - su número de puesto aparece en negrita dentro de una medalla del mismo color, más intenso;
   - la fila lleva a la izquierda una franja de ese color.
2. **Given** las filas del 4.º en adelante y las de participantes sin puesto, **When** se muestran,
   **Then** no cambian respecto a la versión anterior: el mismo fondo, alternado, y el mismo texto.
3. **Given** cualquier ancho entre 320 y 1440 px, **When** se muestra la tabla, **Then**:
   - ninguna fila cambia de alto ni la tabla de ancho;
   - no hay desbordamientos de la página, aunque la tabla siga desplazándose en horizontal dentro
     de su recuadro, como antes.
4. **Given** la revisión de accesibilidad, **When** se comprueba la tabla, **Then**:
   - el texto de las filas del podio y el número de cada medalla tienen un contraste de al menos
     4,5:1;
   - el puesto sigue escrito, así que la información no depende solo del color;
   - axe da 0 incumplimientos AA.
5. **Given** la búsqueda o los filtros de categoría o sexo, **When** el resultado incluye a alguno
   de los tres primeros de la general, **Then** su fila conserva el color de su puesto. El resto de
   filas no se colorea, aunque quede entre las primeras de la lista filtrada. *(Sustituido por la
   US10, decisión P12: el podio es por sexo y, con el filtro de categoría, por categoría.)*
6. **Given** la vista previa de un CSV en el panel, **When** muestra sus primeras filas, **Then**
   los tres primeros se ven igual que en la web pública.

---

### User Story 7 - La barra lateral del panel se desplaza en pantallas bajas (Priority: P1)

Fallo detectado por el propietario: en el panel de administración, si la pantalla es baja, las
últimas opciones de la barra lateral quedan cortadas y no se pueden alcanzar. Con ellas quedan
fuera el usuario y el botón «Cerrar sesión».

**Why this priority**: con la pantalla baja no se puede entrar en «Ajustes» ni cerrar la sesión
desde la barra lateral. Impide usar el panel.

**Independent Test**: entrar en el panel con ventanas bajas, de escritorio y de móvil, con el menú
desplegado. Comprobar que la barra lateral se desplaza y que todas las opciones y «Cerrar sesión»
se pueden alcanzar y pulsar.

**Acceptance Scenarios**:

1. **Given** una ventana más baja que el contenido de la barra lateral, de escritorio o de móvil
   con el menú abierto, **When** se desplaza la barra lateral, **Then**:
   - se llega a todas las opciones, al usuario y a «Cerrar sesión», y se pueden pulsar;
   - la barra lateral sigue fija y el contenido de la página no se mueve con ella.
2. **Given** una ventana con altura suficiente, **When** se muestra la barra lateral, **Then** se
   ve como antes: sin barra de desplazamiento y con el usuario y «Cerrar sesión» abajo del todo.
3. **Given** una ventana baja y una opción del final, por ejemplo «Ajustes», **When** se abre esa
   sección, **Then** la barra lateral muestra la opción marcada sin tener que buscarla.
4. **Given** la navegación por teclado, **When** el foco llega a una opción que no se ve, **Then**
   la barra lateral se desplaza hasta mostrarla.
5. **Given** cualquier ancho, **When** se muestra la barra lateral, **Then** no aparece
   desplazamiento horizontal, ni en la barra ni en la página.

---

### User Story 8 - Logotipo oficial en el panel de administración (Priority: P1)

Decisión P11 del propietario: «el logo, es cierto que hay que poner el oficial también aquí»,
sobre la barra lateral del panel.

La marca antigua, con la silueta y el texto, se sustituye por el logotipo oficial en negativo, el
mismo del pie, en los dos sitios del panel donde aparece:

- la barra lateral, donde se conserva debajo el rótulo «ADMINISTRACIÓN»;
- la pantalla de acceso, sobre la foto.

**Why this priority**: es una instrucción directa del propietario y completa la marca nueva en
toda la web.

**Independent Test**: abrir la pantalla de acceso a varios anchos y entrar en el panel a
escritorio y a móvil. Comprobar que el logotipo oficial se ve completo y nítido, sin la silueta ni
el texto antiguo, y que el resto no se mueve en horizontal.

**Acceptance Scenarios**:

1. **Given** la barra lateral del panel, **When** se muestra a cualquier ancho, **Then**:
   - aparece el logotipo oficial en negativo, completo y sin deformar;
   - debajo queda el rótulo «ADMINISTRACIÓN» con su estilo;
   - ya no aparecen la silueta ni «PEÑASAGRA»;
   - lleva a la portada del panel.
2. **Given** la pantalla de acceso, **When** se muestra la foto, **Then**:
   - aparece el logotipo oficial en negativo en lugar de la silueta y de «TRAIL PEÑASAGRA /
     CORREMOS POR ADRIANA»;
   - lleva a la portada de la web.
3. **Given** la barra lateral y la pantalla de acceso, **When** se comparan con la versión
   anterior, **Then**:
   - el logotipo no es más ancho que la marca anterior;
   - la barra lateral, el contenido del panel y el formulario de acceso no cambian de ancho ni de
     posición horizontal;
   - lo que queda debajo del logotipo solo baja, y como mucho lo que el logotipo es más alto que
     la marca anterior.
4. **Given** una pantalla de alta densidad, **When** se muestra el logotipo, **Then** se ve
   nítido.
5. **Given** la cabecera y el pie públicos y el icono del navegador, **When** se comparan,
   **Then** no han cambiado.

---

### User Story 9 - Contraste AA en todo el panel (Priority: P1)

El propietario lo pide: «sí, corrige el contraste del panel». La decisión P4 (contraste AA) se
aplica también al panel con la sesión iniciada. Al verificar la US8 aparecieron textos con
contraste insuficiente. El cierre (011) solo había revisado la pantalla de acceso.

**Why this priority**: la organización usa el panel a diario y la decisión P4 exige AA.

**Independent Test**: revisar con axe todas las secciones del panel con la sesión iniciada:
listas, un elemento existente y el alta de cada colección, a 360, 1024 y 1440 px. Revisar también
los estados de guardado (aviso de éxito, «Guardado correctamente» y mensaje de error) y las dos
variantes de la etiqueta de estado. Comprobar que no hay ningún incumplimiento.

**Acceptance Scenarios**:

1. **Given** cualquier sección del panel con la sesión iniciada, **When** se revisa a 360, 1024 y
   1440 px, **Then** axe da 0 incumplimientos WCAG 2.1 A/AA.
2. **Given** los estados de guardado y las etiquetas «Publicado» y «Borrador», **When** se
   revisan, **Then** dan 0 incumplimientos.
3. **Given** los textos corregidos, **When** se comparan con la versión anterior, **Then** solo
   cambia su color, a un tono de la paleta del mismo estilo. No cambian ni el tamaño, ni el peso,
   ni los fondos, ni la posición de nada.
4. **Given** la revisión, **When** guarda para comprobar los estados, **Then** no cambia ningún
   dato: las escrituras se interceptan.

---

### User Story 10 - Podio masculino, femenino y por categoría (Priority: P1)

Decisión P12 del propietario. Con el filtro «Femenino» no se identificaba a las tres campeonas:
el podio de la US6 era el de la general, y en 2026 los tres primeros de la general son hombres en
las tres pruebas. «Son campeones tanto los masculinos como los femeninos». Hay que identificar a
las tres primeras chicas y a los tres primeros chicos de todas las pruebas, y también el podio de
cada categoría.

El propietario elige:

- sin filtros, los 3 primeros chicos y las 3 primeras chicas de la prueba;
- con el filtro de sexo, el podio de ese sexo; con el de categoría, el de esa categoría;
- la columna «Pos.» sigue con la posición general;
- la fila conserva el fondo y la franja de oro, plata o bronce;
- junto al nombre, una etiqueta del mismo color con el puesto del podio: «1.ª mujer», «2.º hombre»,
  «1.º Vet A M».

**Why this priority**: sin esto, las campeonas no aparecen como tales. Es un fallo visible en los
resultados oficiales.

**Independent Test**: abrir `/clasificaciones/2026`. Sin filtros, cada prueba muestra 6 filas
destacadas: los 3 primeros chicos y las 3 primeras chicas. Con «Femenino», las 3 primeras chicas;
con una categoría, sus 3 primeros. Al buscar a la campeona por su dorsal, conserva su etiqueta.

**Acceptance Scenarios**:

1. **Given** una clasificación con participantes de los dos sexos, **When** se muestra sin
   filtros, **Then**:
   - los 3 primeros hombres y las 3 primeras mujeres, por su puesto, llevan el fondo, la franja y
     la etiqueta de su puesto en el podio: «1.º hombre», «1.ª mujer»…;
   - la columna «Pos.» sigue mostrando su posición general.
2. **Given** el filtro «Femenino» o «Masculino», **When** se aplica, **Then** las 3 primeras
   personas de ese sexo llevan su color y su etiqueta, aunque no estén entre los 3 primeros de la
   general.
3. **Given** el filtro de una categoría, **When** se aplica, **Then** sus 3 primeros llevan su color
   y una etiqueta con la categoría, por ejemplo «1.º Vet A M».
4. **Given** una búsqueda o el cambio de página, **When** aparece alguien del podio del grupo
   filtrado, **Then** conserva su color y su etiqueta. La búsqueda no cambia quién está en el
   podio.
5. **Given** dos participantes empatados en un puesto del podio, **When** se muestran, **Then** los
   dos llevan el color y la etiqueta de ese puesto.
6. **Given** una clasificación sin datos de sexo, **When** se muestra, **Then** se destaca el podio
   de la general con la etiqueta «1.º general».
7. **Given** la vista previa de un CSV o la clasificación actual en el panel, **When** se muestran,
   **Then** el podio se calcula con la misma regla.
8. **Given** la tabla, **When** se revisa, **Then**:
   - la etiqueta tiene un contraste de al menos 4,5:1;
   - las filas que no son del podio conservan su fondo;
   - no hay desbordamientos de la página.

   La etiqueta ensancha la columna del nombre. Por eso la tabla puede repartir de nuevo los anchos
   y algún texto largo (el club) puede cambiar de salto de línea.

### User Story 11 - «PEÑASAGRA» con Ñ y textos bien escritos (Priority: P1)

Decisión P13 del propietario: «en la home, como título principal en grande, pone PENASAGRA y es
PEÑASAGRA; repasa para que todo esté bien escrito». El título de la portada pasa a «TRAIL» /
«PEÑASAGRA», con el mismo tamaño, color y posición. Además se repasa la ortografía de todos los
textos de la web pública y del panel, y se corrige lo que esté mal escrito.

La revisión cubre los textos de 56 vistas, sus atributos legibles (texto alternativo, nombres
accesibles, textos de ayuda de los campos, título y descripción de la página) y los mensajes del
código que solo aparecen en algunos estados: errores, avisos y validaciones. Encuentra:

- el título «PENASAGRA», sin Ñ;
- en el panel, textos formados con el nombre interno de la sección: «Buscar galeria…» y «Volver a
  galeria», sin tilde; «Información del noticia» e «Información del prueba», con el género
  equivocado; «Añade noticia y publícalo cuando esté listo.», sin artículo y con el género
  equivocado;
- los nombres accesibles de los botones de subida con mayúscula a mitad de frase: «Subir Imagen
  de portada»;
- los errores del CSV que nombran el campo en inglés: «“category” admite hasta 150 caracteres»;
- en el formulario de contacto, dos preguntas sin signos de interrogación: «Cómo te llamas» y
  «Sobre qué quieres hablar»;
- la descripción de la página de un álbum, con el título sin comillas: «Fotografías de Volver a
  sentir la montaña (2026).».

**Why this priority**: es el nombre de la carrera en el lugar más visible de la web. Los textos mal
escritos dan una imagen descuidada de la organización.

**Independent Test**: abrir la portada a 320, 360, 768, 1024 y 1440 px y leer «TRAIL PEÑASAGRA» en
la misma caja que antes. Repetir la revisión de textos y comprobar que no queda ninguno de los
errores encontrados.

**Acceptance Scenarios**:

1. **Given** la portada, **When** se muestra a cualquier ancho, **Then** el título dice «TRAIL» y
   «PEÑASAGRA», con la Ñ dibujada en la misma fuente. Tiene el mismo tamaño, color y posición que
   antes, sin desbordamiento, y la virgulilla no toca la línea «TRAIL».
2. **Given** una lista del panel (noticias, galería, pruebas, patrocinadores o colaboradores),
   **When** se abre, **Then** el buscador dice «Buscar noticias…», «Buscar galería…»… Si está
   vacía, invita a añadir con el artículo y el género correctos: «Añade una noticia y publícala
   cuando esté lista.», «Añade un álbum y publícalo cuando esté listo.».
3. **Given** el alta o la edición de un elemento del panel, **When** se abre, **Then** el enlace de
   vuelta dice «Volver a galería» y el bloque del formulario, «Información de la noticia»,
   «Información del álbum», «Información de la prueba»…
4. **Given** un campo de subida de archivos, **When** se lee su nombre accesible, **Then** sigue la
   frase en minúscula: «Subir imagen de portada», «Subir track GPX».
5. **Given** un CSV con una categoría, un club, un tiempo, un sexo o un estado demasiado largos,
   **When** se valida en el navegador o en el servidor, **Then** el error nombra el campo en
   español: «“Categoría” admite hasta 150 caracteres.» (con las comillas latinas de la web).
6. **Given** el formulario de contacto, **When** se muestran sus textos de ayuda, **Then** las
   preguntas llevan sus dos signos: «¿Cómo te llamas?» y «¿Sobre qué quieres hablar?».
7. **Given** la página de un álbum, **When** se lee su descripción, **Then** el título del álbum va
   entre comillas latinas: «Fotografías de “Volver a sentir la montaña” (2026).».
8. **Given** el resto de la web, **When** se compara con la versión anterior, **Then** solo cambian
   los textos corregidos.

### User Story 12 - Despliegue automático con `deploy.sh` (Priority: P1)

El propietario quiere desplegar sin seguir una lista de comandos. Entra en la MV, descarga el
repositorio, copia el `.env` que se le entrega preparado y ejecuta `./deploy.sh`. El script lo hace
todo, y lo mismo en cada actualización.

Sus respuestas:

- **Datos**: instalación limpia, con los datos aprobados y las clasificaciones de 2026 de la
  carpeta de la web anterior en la MV.
- **Fotos**: en el disco de la MV.
- **Usuario del panel**: `organizacion`, con una contraseña generada.

**Why this priority**: sin esto, el cambio de la web anterior a la nueva depende de repetir a mano
una quincena de órdenes en el orden correcto.

**Independent Test**: ensayar en local un clon limpio con una web anterior simulada en 80/443:

- primera ejecución, segunda ejecución y actualización con cambios en `deploy.sh`;
- un fallo al arrancar, con vuelta atrás;
- la copia programada.

**Acceptance Scenarios**:

1. **Given** una MV con la web anterior en 80/443 y el repositorio recién descargado con su
   `.env`, **When** se ejecuta `./deploy.sh`, **Then**:
   - construye y migra la base;
   - carga los datos aprobados y las 3 clasificaciones de 2026 (63, 205 y 224 participantes);
   - crea la cuenta `organizacion`;
   - para la web anterior sin borrar sus datos y arranca la nueva por HTTPS;
   - comprueba redirecciones, cabeceras, 404 y certificado, y programa la copia diaria.
2. **Given** la web nueva ya instalada, **When** se ejecuta de nuevo, **Then** hace una copia
   previa, actualiza el código y el esquema, y no importa datos, no crea cuentas ni cambia
   contraseñas.
3. **Given** un `deploy.sh` nuevo en el repositorio, **When** se ejecuta el antiguo, **Then**
   descarga el código y continúa con la versión nueva.
4. **Given** que la web nueva no responde por HTTPS a tiempo, **When** había parado la web
   anterior, **Then** la vuelve a arrancar, deja la nueva parada con sus datos y termina con
   error.
5. **Given** un `.env` que falta, está incompleto o tiene valores sin rellenar, o Docker o Compose
   demasiado antiguos, **When** se ejecuta, **Then** se detiene antes de tocar nada, con un
   mensaje que dice qué falta.
6. **Given** otras tareas en el crontab, **When** se programa la copia, **Then** se conservan, y
   la del proyecto aparece una sola vez.

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
- **Empate en un puesto del podio (US6)**: si dos participantes comparten puesto, los dos llevan el
  color de ese puesto.
- **Puestos de dos o tres cifras (US6)**: solo el 1, el 2 y el 3 llevan medalla. La medalla se
  ensancha si hiciera falta, sin cortar el número.
- **Clasificación sin puestos (US6)**: si nadie tiene puesto, no se colorea ninguna fila.
- **Pantalla muy baja con el menú de móvil abierto (US7)**: el panel desplegado también se
  desplaza. Al llegar a su final, no arrastra la página de detrás.
- **Logotipo del panel que no carga (US8)**: el enlace conserva su nombre accesible y el rótulo
  «ADMINISTRACIÓN» sigue visible.
- **Participantes sin sexo (US10)**: si la clasificación tiene datos de sexo, quien no lo tiene no
  entra en ningún podio. Si no hay datos de sexo en toda la clasificación, se usa la general.
- **Categoría con los dos sexos (US10)**: su podio se calcula para cada sexo, cada uno con la
  etiqueta de la categoría y el ordinal de su género.
- **Podio fuera de la primera página (US10)**: la etiqueta aparece igual en la página donde esté.
- **Fuente del título que no carga (US11)**: la Ñ se dibuja con la fuente de reserva, igual que el
  resto del título. Barlow Condensed incluye la Ñ, así que no se mezclan fuentes dentro de la
  palabra.
- **Contenido escrito por la organización (US11)**: las noticias, las pruebas, el reglamento, los
  álbumes y los nombres de patrocinadores son datos que la organización edita desde el panel. Se
  revisan, pero no se cambian desde el código.
- **Puertos ocupados por un programa que no es Docker (US12)**: el script se detiene antes de
  arrancar la web nueva y vuelve a arrancar la anterior si la había parado.
- **CSV de 2026 no encontrados (US12)**: avisa y sigue. Las clasificaciones se suben desde el
  panel.
- **Base con datos (US12)**: nunca se importa ni se sobrescribe nada (constitución IV).
- **Datos oficiales (US11)**: los nombres de participantes y clubes, los valores de categoría
  («Senior F») y los nombres de los archivos CSV importados se muestran tal como llegan.

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
- **FR-017**: La línea inferior del pie de todas las páginas públicas MUST mostrar «Hecho por la
  Escuela Hacker Cosío» en lugar de «Hecho con pasión por JR BLANCO · Hackers Cosío». El aviso
  «© año Asociación Peñasagra» MUST NOT cambiar.
- **FR-018**: La frase nueva MUST conservar el color y el tamaño de letra de la línea inferior del
  pie. MUST NOT enlazar a ninguna dirección que no haya aportado el propietario.
- **FR-019**: En las tablas de clasificación, públicas y de vista previa del panel, las filas con
  puesto 1, 2 y 3 MUST distinguirse con un fondo suave propio: oro, plata y bronce. Cada una lleva
  una franja a la izquierda y una medalla con el número, ambas en el mismo color más intenso. Los
  tres colores MUST ser distintos entre sí y del fondo de las demás filas. *(La US10 sustituye la
  medalla por una etiqueta junto al nombre, y el puesto general por el podio de cada grupo.)*
- **FR-020**: El texto de las filas del podio y el número de cada medalla MUST tener un contraste
  de al menos 4,5:1. El puesto MUST seguir escrito, así que la información no depende solo del
  color.
- **FR-021**: Las demás filas, el alto de todas las filas, el ancho de la tabla y el resto de la
  página MUST NOT cambiar. El podio se decide por el puesto publicado (la general), no por la
  posición en una lista filtrada. *(Sustituido en parte por FR-028–FR-031: el podio es por sexo o
  por categoría; las filas del podio pueden crecer si la etiqueta no cabe en su línea.)*
- **FR-022**: La barra lateral del panel MUST desplazarse en vertical cuando su contenido no cabe
  en la ventana, en escritorio y en el menú de móvil. Todas sus opciones, el usuario y «Cerrar
  sesión» MUST poder alcanzarse y pulsarse. MUST NOT aparecer desplazamiento horizontal.
- **FR-023**: Con altura suficiente, la barra lateral MUST verse como antes: sin barra de
  desplazamiento y con el usuario abajo. Al abrir una sección, su opción marcada MUST quedar a la
  vista en la barra lateral.
- **FR-024**: La barra lateral del panel y la pantalla de acceso MUST mostrar el logotipo oficial
  en negativo en lugar de la silueta y del texto de la marca. La barra lateral MUST conservar el
  rótulo «ADMINISTRACIÓN». Cada enlace MUST conservar su destino: el panel y la portada.
- **FR-025**: El logotipo del panel MUST NOT ser más ancho que la marca anterior. La barra
  lateral, el contenido del panel y el formulario de acceso MUST NOT cambiar de ancho ni de
  posición horizontal. La cabecera, el pie y el icono del navegador MUST NOT cambiar.
- **FR-026**: Todo el texto del panel con la sesión iniciada MUST tener contraste AA: 4,5:1, o
  3:1 si es grande. Esto incluye las listas, los formularios, los estados de guardado y las
  etiquetas de estado.
- **FR-027**: Cada corrección MUST limitarse al color del texto, con un tono de la paleta. Los
  tamaños, los pesos, los fondos y la disposición MUST NOT cambiar.
- **FR-028**: El podio de una clasificación MUST calcularse sobre quienes tienen puesto y cumplen
  los filtros de categoría y sexo activos, sin contar la búsqueda de texto:
  - se calcula para cada sexo;
  - si la clasificación no tiene datos de sexo, se usa la general;
  - cada uno ocupa el puesto que le corresponde por su posición, y los empates lo comparten;
  - solo cuentan los puestos 1, 2 y 3.
- **FR-029**: Las filas del podio MUST llevar el fondo, la franja y una etiqueta del color de su
  puesto (oro, plata o bronce) junto al nombre. La etiqueta dice el puesto en el podio, con el
  ordinal en el género de la persona, y el grupo: «hombre» o «mujer», la categoría filtrada o
  «general». La columna «Pos.» MUST seguir mostrando la posición general.
- **FR-030**: El servidor MUST indicar el puesto en el podio de cada fila de la consulta pública,
  para que la búsqueda y la paginación no lo cambien. La vista previa y la clasificación actual
  del panel MUST calcularlo con la misma regla.
- **FR-031**: La etiqueta MUST tener un contraste de al menos 4,5:1. Las filas que no son del podio
  MUST conservar su fondo, y la página MUST NOT desbordarse. El reparto de anchos de la tabla
  puede cambiar el salto de línea de algún texto largo.
- **FR-032**: El título de la portada MUST decir «TRAIL» y «PEÑASAGRA», con Ñ. MUST conservar el
  tamaño, el color, la posición y la caja de cada línea, sin desbordamiento entre 320 y 1440 px.
  La virgulilla MUST NOT tocar la línea «TRAIL».
- **FR-033**: Los textos del panel que dependen de la sección MUST escribirse con tildes y con el
  artículo y el género de cada elemento:
  - el buscador y el enlace de vuelta: «Buscar galería…», «Volver a galería»;
  - el bloque del formulario: «Información de la noticia», «Información del álbum»;
  - la invitación de la lista vacía: «Añade una noticia y publícala cuando esté lista.».
- **FR-034**: El nombre accesible de cada campo de subida MUST seguir en minúscula tras «Subir»:
  «Subir imagen de portada».
- **FR-035**: Los errores de longitud del CSV MUST nombrar el campo con su nombre en español
  («Categoría», «Club», «Tiempo», «Sexo», «Estado»), en el navegador y en el servidor.
- **FR-036**: Las preguntas de los textos de ayuda del formulario de contacto MUST llevar los
  signos de apertura y cierre. La descripción de la página de un álbum MUST poner su título entre
  comillas latinas.
- **FR-037**: El resto de los textos, los estilos y la disposición MUST NOT cambiar. Los contenidos
  que edita la organización y los datos oficiales MUST NOT modificarse desde el código.
- **FR-038**: `deploy.sh` MUST instalar o actualizar la web en la MV con una sola orden y poder
  repetirse sin efectos no deseados. Hace todo lo necesario:
  - comprobaciones, descarga del código, copia previa, construcción y migraciones;
  - datos iniciales en una base vacía y cuenta del panel si no hay ninguna;
  - cambio desde la web anterior y arranque;
  - comprobaciones y copia diaria.
- **FR-039**: El script MUST NOT sobrescribir datos existentes, cambiar contraseñas de cuentas
  existentes ni borrar los volúmenes de la web anterior ni de la nueva.
- **FR-040**: Si la web nueva no responde por HTTPS en el tiempo de espera, el script MUST volver
  a arrancar la web anterior que haya parado y terminar con error.
- **FR-041**: El `.env` de producción MUST entregarse fuera del repositorio, con secretos
  aleatorios y el dominio en *punycode*. MUST NOT versionarse.
- **FR-042**: La guía de operación MUST explicar el flujo, lo que hace el script, sus variables
  y la vuelta atrás.

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
- **SC-012**: En el 100 % de las páginas públicas a 320, 360, 768, 1024 y 1440 px, la línea
  inferior del pie muestra la frase nueva y ninguna de las palabras de la anterior. La cabecera y
  la parte superior del pie no se mueven (diferencia de 0 px). Hay 0 desbordamientos y 0
  incumplimientos de accesibilidad AA.
- **SC-013**: En las 3 clasificaciones de 2026, a 320, 360, 768, 1024 y 1440 px:
  - el 100 % de las filas con puesto 1, 2 o 3 muestran su color, su franja y su medalla, y ninguna
    otra fila;
  - los tres colores son distintos entre sí y del fondo de las demás filas;
  - las demás filas conservan su fondo y todas las filas su alto (diferencia de 0 px);
  - contraste del texto y de las medallas de al menos 4,5:1, 0 incumplimientos AA y 0
    desbordamientos.
- **SC-014**: En ventanas de escritorio y de móvil más bajas que la barra lateral, el 100 % de las
  opciones, el usuario y «Cerrar sesión» se alcanzan y se pueden pulsar. La opción de la sección
  abierta se ve al cargar. Hay 0 desplazamientos horizontales. Con altura suficiente, la barra
  lateral no se desplaza.
- **SC-015**: El logotipo oficial se ve completo y nítido en la barra lateral y en la pantalla de
  acceso, en todos los anchos medidos, sin restos de la marca antigua. La barra lateral, el
  contenido del panel y el formulario de acceso tienen 0 px de diferencia en ancho y posición
  horizontal. Hay 0 incumplimientos AA.
- **SC-017**: En las 3 clasificaciones de 2026, a 320, 360, 768, 1024 y 1440 px:
  - sin filtros, el 100 % de los 3 primeros hombres y las 3 primeras mujeres de cada prueba
    llevan su color y su etiqueta, y nadie más;
  - con «Femenino», «Masculino» o una categoría, el 100 % de su podio y nadie más;
  - buscar a la campeona conserva su etiqueta;
  - las demás filas conservan el fondo, y su alto solo cambia por el reparto de anchos de la
    tabla (medido: 5 filas a 1024 y 1440 px, de 1 a 2 líneas o al revés);
  - contraste de al menos 4,5:1 y 0 desbordamientos.
- **SC-016**: 0 incumplimientos de axe (WCAG 2.1 A/AA) en el 100 % de las vistas del panel
  revisadas: todas las secciones, un elemento existente y el alta de cada colección, a 360, 1024
  y 1440 px, más los estados de guardado. Ningún dato cambia durante la revisión. Las capturas
  del panel solo difieren en el color de los textos corregidos.
- **SC-018**: A 320, 360, 768, 1024 y 1440 px, la portada muestra «TRAIL PEÑASAGRA» en Barlow
  Condensed:
  - con el mismo tamaño y color, y con 0 px de diferencia en la caja del título y en la posición y
    el alto de cada línea;
  - el ancho de la segunda línea varía como mucho un 5 % del tamaño de letra;
  - 0 desbordamientos, y la virgulilla no invade la línea «TRAIL».
- **SC-019**: Una segunda revisión de los textos de las 56 vistas y de los mensajes del código no
  encuentra ninguno de los errores corregidos. Las capturas de las páginas públicas solo difieren
  en el título de la portada y en los textos de ayuda del formulario de contacto. Hay 0
  incumplimientos AA en la web y en el panel.
- **SC-020**: En el ensayo local (clon limpio, web anterior simulada en 80/443 y dominio
  `.localhost`):
  - la primera ejecución termina sin fallos, con 63/205/224 participantes y acceso al panel con la
    cuenta creada;
  - la segunda hace una copia y no cambia datos;
  - un `deploy.sh` nuevo se relanza solo;
  - un fallo forzado devuelve la web anterior al aire con los datos de la nueva intactos;
  - la copia programada conserva las demás tareas;
  - `shellcheck` sin avisos, y el Docker de desarrollo intacto.

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
  conserva su marca. Si la quiere también allí, se añadirá como historia. *(Actualizado por la
  US8: el propietario lo pidió, decisión P11.)*
- **Frase sin enlace (US5)**: en la frase anterior, «JR BLANCO» enlazaba a `jrblanco.es`. La frase
  nueva no nombra a JR BLANCO, y el propietario no ha dado una dirección para la Escuela Hacker
  Cosío. Por eso va como texto, sin enlace (constitución VI: no se inventan enlaces). Si el
  propietario quiere enlazarla, basta con que dé la dirección.
- **Colores del podio (US6)**: el propietario deja la elección abierta («lo de verde es por decir
  algo»). Se eligen oro, plata y bronce suaves porque se reconocen como podio sin explicación y no
  se confunden con el verde de la cabecera de la tabla ni con el naranja de los botones.
- **Podio de la general (US6)**: son los mismos tres puestos que ya iban en negrita, es decir, el
  puesto publicado en el CSV. Con la búsqueda o los filtros, cada fila conserva su puesto general.
  No se calcula un podio por sexo ni por categoría, porque sería interpretar los resultados
  oficiales. Si el propietario quiere destacar también el podio femenino o el de cada categoría,
  se añadirá como historia. *(Sustituido por la US10: el propietario lo pidió, decisión P12.)*
- **Alcance del logotipo en el panel (US8)**: el propietario habla del panel, cuya marca antigua
  está en la barra lateral y en la pantalla de acceso. Se cambia en los dos sitios. El icono del
  navegador sigue igual, por el mismo motivo que en la US3.
- **Rótulo «ADMINISTRACIÓN» (US8)**: no forma parte de la marca: indica que se está en el panel.
  Se conserva debajo del logotipo, con su estilo, y el «PEÑASAGRA» repetido desaparece. Si el
  propietario prefiere solo el logotipo, basta con quitarlo.
- **Contraste del panel (US9)**: antes del cambio, la revisión encuentra 2 defectos repetidos en
  todas las vistas:
  - las cabeceras de las tablas de listados: #7a8d7f sobre #f9fbfa, 3,40:1;
  - el pie del panel: #8b9b90 sobre #f3f5f4, 2,67:1.

  Pasan al gris de texto secundario de la paleta, `--muted` (#66716b), ya usado en el panel: 4,88:1
  y 4,63:1. axe no revisa los estados al pasar el ratón ni de foco: quedan fuera de esta
  revisión automática.
- **Etiqueta del podio (US10)**: «hombre» sale de los valores «Masculino», «M» u «Hombre» del CSV,
  y «mujer», de «Femenino», «F» o «Mujer». Si el CSV usa otro valor de sexo, la etiqueta lo
  muestra tal cual, con «.º».
- **Título literal (US11)**: la constitución (principio I) y la referencia aprobada pedían el
  título literal «TRAIL PENASAGRA». El propietario corrige ahora esa escritura: es «PEÑASAGRA».
  Se enmienda la constitución (1.0.1) y se anota la referencia. Se mantienen las dos líneas,
  «TRAIL» en blanco y «PEÑASAGRA» en naranja.
- **Contenidos de la organización (US11)**: en la revisión no aparece ninguna falta de ortografía
  en las noticias, las pruebas, el reglamento, los álbumes ni los patrocinadores. Si apareciera,
  se comunicaría al propietario para corregirla desde el panel, porque esos textos viven en la
  base de datos de cada instalación. Una frase del reglamento se puede mejorar en estilo: «Se
  sancionan […] los residuos» se refiere a abandonarlos. Se le comunica como sugerencia.
- **Plantilla CSV (US11)**: las cabeceras de la plantilla (`posicion`, `categoria`…) van sin
  tildes a propósito. Son nombres de columna, que la importación reconoce con o sin tilde. Sin
  tildes, la hoja de cálculo las abre bien con cualquier codificación.
- **`.env` de producción (US12)**: se entrega como `.env.produccion` en la raíz del repositorio
  local. Está ignorado por Git, y no se llama `.env` porque Compose lo leería y estropearía el
  entorno de desarrollo. En la MV se copia como `.env`. La contraseña inicial del panel va en ese
  archivo; no se escribe en otros sitios.
- **Copias programadas (US12)**: se instalan en el crontab de quien ejecuta el script (root con
  `sudo`). El registro queda en `COPIAS_DIR`, no en `/var/log`.
