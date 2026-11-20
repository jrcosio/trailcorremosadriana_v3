# Feature Specification: Ajustes de la revisión del propietario

**Feature Branch**: `012-ajustes-revision`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Ajustes que pide el propietario tras revisar la web; se irán añadiendo historias. Historia 1: «las fotos se tienen que ver completas siempre». La foto de Adriana sale con la cabeza cortada en la portada y en /solidaridad."

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

### Edge Cases

- **Foto con la misma proporción que su marco**: se ve igual que antes, sin relleno visible.
- **Foto horizontal en un marco vertical, y al revés**: se ve completa; el relleno aparece arriba y
  abajo o a los lados.
- **Contenido sin foto propia**: la imagen de reserva (paisaje de la sierra) también se ve completa.
- **Foto que no carga**: el marco muestra el color de fondo de la paleta, sin errores.
- **Visor de fotos y vista previa de subida**: ya muestran la foto completa y no cambian.

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

## Assumptions

- **Fondos decorativos fuera de alcance**: el paisaje de la portada, el banner de la galería y el
  marcador del mapa son fondos con degradado, no fotos de contenido, y siguen como están. Si el
  propietario quiere aplicarles la misma regla, se añadirá como historia en esta feature.
- **Relleno**: el verde oscuro de la paleta (`--forest`) ya se usa en tarjetas y cabeceras.
- **Ampliable**: esta feature irá incorporando como historias nuevas los demás ajustes que pida el
  propietario tras su revisión.
