# Feature Specification: Evento y carreras

**Feature Branch**: `004-evento-carreras`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Evento y carreras (short-name: evento-carreras): ediciones, configuración, recorridos, datos por carrera, fecha, contador y conexión con las pantallas públicas. La organización gestiona desde el panel la edición actual, su fecha y hora peninsular y el contador, y las pruebas con sus datos por edición (distancia, desnivel, precio de referencia, salida, terreno, descripción, avituallamientos, foto, ruta, Wikiloc, GPX y publicación). La web pública (portada, contador, /carreras, /recorridos y detalle de cada prueba) muestra esos datos persistentes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configurar la próxima edición y su fecha (Priority: P1)

La organización indica en `/admin/evento` la edición actual (año), su fecha y hora de salida en
hora peninsular española (o la deja vacía si no está confirmada) y si se muestra la cuenta atrás.
La portada refleja esos datos.

**Why this priority**: la fecha y el contador son lo primero que ve cualquier visitante. Hoy
dependen de datos fijos.

**Independent Test**: guardar una fecha en el panel, recargar, reiniciar los servicios y comprobar
la portada y el panel; vaciar la fecha y comprobar «Fecha por confirmar».

**Acceptance Scenarios**:

1. **Given** la edición 2027 sin fecha, **When** se abre la portada, **Then** el contador muestra
   guiones y «La fecha de 2027 está por confirmar».
2. **Given** el panel de evento, **When** se guarda 2027 con fecha 10/07/2027 a las 09:00,
   **Then** la portada cuenta hasta las 09:00 hora peninsular de ese día y muestra «10 de julio de
   2027», también después de recargar y de reiniciar los servicios.
3. **Given** una fecha en horario de verano o de invierno, **When** se guarda y se vuelve a abrir
   el panel, **Then** aparece exactamente la misma hora local introducida.
4. **Given** el contador desactivado, **When** se abre la portada, **Then** se muestra la fecha sin
   cuenta atrás.
5. **Given** dos personas editando el evento a la vez, **When** la segunda guarda sobre una
   versión ya modificada, **Then** se le avisa del conflicto y no se pierde el cambio de la
   primera.

---

### User Story 2 - Gestionar las pruebas y sus datos (Priority: P1)

La organización crea, edita, publica, retira y borra pruebas en `/admin/recorridos`. Cada prueba
tiene identidad estable (su dirección no cambia) y datos asociados a una edición: distancia,
desnivel, precio de referencia, hora de salida, terreno, descripción, avituallamientos, foto,
enlace de ruta, identificador de Wikiloc, GPX y enlace de inscripción.

**Why this priority**: las pruebas son el contenido central de la web y la base de inscripciones
y clasificaciones.

**Independent Test**: editar los kilómetros de una prueba existente, crear una nueva como
borrador, publicarla y borrarla, comprobando cada paso en la web pública tras recargar.

**Acceptance Scenarios**:

1. **Given** las tres pruebas de referencia, **When** se edita la distancia de la Trail y se
   guarda, **Then** `/carreras` y `/carreras/trail-27k` muestran el nuevo valor tras recargar.
2. **Given** una prueba nueva, **When** se guarda, **Then** queda como borrador y no aparece en la
   web pública hasta publicarla.
3. **Given** una prueba publicada, **When** se retira (se desmarca la publicación), **Then**
   desaparece de la web pública y su detalle muestra la pantalla de no encontrado.
4. **Given** una prueba sin clasificaciones, **When** se borra con confirmación, **Then**
   desaparece del panel y de la web.
5. **Given** que se cambia la «edición de estos datos» de una prueba (por ejemplo, de 2026 a
   2027), **When** se guarda, **Then** la web muestra los datos de la nueva edición y los de la
   edición anterior se conservan como histórico.
6. **Given** datos no válidos (distancia negativa, enlace que no es HTTPS, Wikiloc no numérico),
   **When** se guarda, **Then** se rechaza con un mensaje claro y no se modifica nada.
7. **Given** que se guarda dos veces seguidas una prueba recién creada, **When** termina, **Then**
   existe una sola prueba.

---

### User Story 3 - Datos iniciales desde el contenido aprobado (Priority: P1)

El operador carga una sola vez los datos aprobados: la edición 2026 con su fecha oficial (11 de
julio de 2026 a las 09:00), la edición 2027 sin fecha como edición actual y las tres pruebas con
sus datos de referencia de 2026. El comando nunca sobrescribe datos ya existentes salvo que se
pida explícitamente.

**Why this priority**: sin estos datos la web pública perdería su contenido al pasar a la base de
datos.

**Independent Test**: ejecutar la importación en una base vacía y repetirla; comprobar que la
segunda vez no cambia nada.

**Acceptance Scenarios**:

1. **Given** una base sin ediciones ni pruebas, **When** se ejecuta la importación, **Then** se
   crean las ediciones 2026 y 2027 y las tres pruebas con los datos de 2026, y la web muestra lo
   mismo que antes de la migración.
2. **Given** una base con datos, **When** se repite la importación, **Then** no se modifica nada y
   se informa de ello.

---

### User Story 4 - Ver pruebas y fecha en la web pública (Priority: P2)

Un visitante ve en la portada, en `/carreras` (y su alias histórico `/recorridos`) y en el
detalle de cada prueba solo los datos publicados, con la edición a la que pertenecen, el mapa de
Wikiloc bajo demanda y la descarga GPX solo si existe.

**Why this priority**: es la consecuencia visible de US1–US3. Las pantallas ya existen y no
cambian de aspecto.

**Independent Test**: comparar la web pública antes y después de la migración (capturas y textos)
y comprobar el detalle de una prueba con GPX subido.

**Acceptance Scenarios**:

1. **Given** los datos importados, **When** se abre la web, **Then** las capturas y los textos
   coinciden con los de la feature 001.
2. **Given** una prueba con un GPX subido, **When** se abre su detalle, **Then** aparece la descarga
   del GPX; sin GPX, no aparece.

---

### Edge Cases

- Fecha en el cambio de hora (último domingo de marzo/octubre): una hora inexistente (salto de
  primavera) avanza a la siguiente hora válida; una hora ambigua (otoño) toma la primera
  ocurrencia (horario de verano). Al reabrir se muestra la hora resultante.
- Fecha ya pasada: el contador queda a cero («Nos vemos en la montaña»), sin negativos.
- Cambiar la edición actual a un año nuevo: se crea esa edición; la anterior se conserva.
- Borrar una prueba con clasificaciones (feature 006): se rechaza con un aviso, sin borrar nada.
- Prueba con un identificador nuevo creado en el panel: su dirección pública usa ese identificador
  y no cambia al editarla.
- Base sin importar: la web sigue mostrando el contenido de referencia (comportamiento
  transitorio documentado).
- Secciones del panel aún no migradas: siguen informando de que no guardan cambios.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST guardar ediciones con año único, fecha y hora opcional con zona
  horaria, indicador de contador e indicación de cuál es la edición actual (exactamente una).
- **FR-002**: La fecha MUST introducirse y mostrarse en hora peninsular (Europe/Madrid) con cambios
  de horario correctos y almacenarse como instante absoluto.
- **FR-003**: Guardar el evento con un año distinto del actual MUST convertir esa edición en la
  actual (creándola si no existe) sin borrar la anterior.
- **FR-004**: El sistema MUST guardar pruebas con identificador estable y nombre, frase corta y
  color, y sus datos por edición (distancia, desnivel, precio de referencia, hora de salida,
  terreno, descripción, avituallamientos, foto, ruta, Wikiloc, GPX, enlace de inscripción y
  publicación), con una sola ficha por prueba y edición.
- **FR-005**: La web pública MUST mostrar, de cada prueba, los datos publicados de su edición más
  reciente; las pruebas sin datos publicados MUST NOT aparecer ni ser accesibles por su dirección.
- **FR-006**: Las validaciones MUST rechazar: nombre vacío o de más de 150 caracteres;
  distancia o desnivel negativos o no numéricos; edición fuera de `20XX`; hora no válida;
  Wikiloc no numérico; foto, ruta, GPX o inscripción que no cumplan la regla de referencias (feature
  003); color que no sea hexadecimal; textos por encima de sus límites.
- **FR-007**: Toda modificación de evento o prueba MUST usar control de versión y responder
  conflicto (409) sin sobrescribir si la versión no es la vigente.
- **FR-008**: Crear una prueba con un identificador ya existente por un doble envío MUST NOT
  duplicarla.
- **FR-009**: Borrar una prueba MUST eliminar la prueba y sus datos por edición, salvo que tenga
  clasificaciones; en ese caso MUST rechazarse con un aviso.
- **FR-010**: Un comando de operador MUST importar los datos aprobados (ediciones 2026 y 2027 y las
  tres pruebas con datos de 2026) solo en las partes vacías, informando de lo que hace, y MUST NOT
  sobrescribir datos existentes salvo con una opción explícita de reemplazo.
- **FR-011**: El contrato de contenido existente MUST obtener de la base de datos la edición, la
  fecha, el contador y las pruebas (incluidos borradores y versiones en la variante privada), sin
  cambiar su forma para las pantallas.
- **FR-012**: Las pantallas del panel `/admin/evento` y `/admin/recorridos` MUST guardar en la base
  de datos con su apariencia actual. Tras guardar, el panel MUST mostrar los datos confirmados
  por el servidor. Las demás secciones siguen sin guardar hasta sus features.
- **FR-013**: Todas las escrituras MUST requerir la protección de administración (feature 002).
- **FR-014**: Los cambios MUST sobrevivir a recargar y a reiniciar los servicios.

### Key Entities *(include if feature involves data)*

- **Edición**: año, fecha y hora de salida (opcional, con zona), mostrar contador, si es la actual
  y versión.
- **Prueba (carrera)**: identificador estable (dirección pública), nombre, frase corta, color y
  orden.
- **Datos de prueba por edición**: pertenecen a una prueba y a una edición (única por par):
  distancia, desnivel, precio de referencia, hora de salida, terreno, descripción,
  avituallamientos, foto, ruta, Wikiloc, GPX, enlace de inscripción, publicación y versión.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Tras la importación, la web pública es idéntica en textos e imágenes a la de la
  feature 001 en las 11 rutas públicas estáticas y en los 3 detalles de prueba.
- **SC-002**: Una fecha guardada a las 09:00 en verano y otra en invierno se reabren exactamente a
  las 09:00 (2 de 2).
- **SC-003**: El 100 % de los cambios de evento y pruebas siguen presentes tras reiniciar todos los
  servicios.
- **SC-004**: El 100 % de las escrituras con una versión obsoleta se rechazan sin modificar datos.
- **SC-005**: Una prueba en borrador o retirada no aparece en ninguna respuesta pública ni en
  ninguna ruta pública (0 apariciones).
- **SC-006**: La importación repetida no modifica ningún dato (0 cambios en la segunda ejecución).

## Assumptions

- La edición actual (2027) no tiene fecha (decisión P1). Las pruebas muestran los datos de 2026
  identificados como referencia, porque es su edición más reciente.
- La fecha oficial de 2026 (sábado 11 de julio de 2026, salida a las 09:00 en Cosío) procede de
  la web de producción y es un dato real.
- Los campos de inscripción (apertura, mensaje, Dorsal Solidario) se gestionan en la feature 005.
  El enlace de inscripción por prueba se guarda ya en esta feature porque forma parte del
  formulario de pruebas, y su validación como destino de pago llega en la 005.
- La prohibición de borrar pruebas con clasificaciones se aplica cuando existan clasificaciones
  (feature 006).
- El contenido de referencia se sigue mostrando solo si la base no tiene ninguna edición ni prueba
  (entorno sin inicializar). Es un comportamiento transitorio documentado.
