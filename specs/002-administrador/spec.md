# Feature Specification: Administrador

**Feature Branch**: `002-administrador`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "Administrador (short-name: administrador). La organización accede a un panel privado con cuentas propias de la aplicación. Alcance: (1) creación segura del administrador inicial y recuperación de acceso mediante un comando de operador con entrada oculta de contraseña; (2) inicio de sesión en /admin, mensajes que no revelan qué campo falló, sesión de servidor de 8 horas y cierre de sesión que revoca el acceso; (3) estados de la pantalla de acceso y resumen del panel con datos privados; (4) límite persistente de 8 intentos fallidos por origen en 15 minutos; (5) protección de lecturas privadas y escrituras con origen permitido y CSRF; secciones sin feature informan de que no guardan; (6) revocación al cerrar sesión, al desactivar la cuenta o por comando; sesiones que sobreviven a reinicios. Fuera de alcance: cambio de contraseña desde la web, varias cuentas con roles, recuperación por correo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear el administrador inicial de forma segura (Priority: P1)

La persona responsable técnica crea la primera cuenta de administración con un comando de
operador. Escribe el usuario y la contraseña de forma oculta (dos veces). La contraseña nunca
aparece en el repositorio, en la línea de comandos ni en los registros. Con el mismo tipo de
comando puede restablecer la contraseña si se olvida, desactivar o reactivar una cuenta y
revocar todas las sesiones.

**Why this priority**: sin una cuenta creada de forma segura no hay panel. Es la única vía de
alta, porque no existe registro público.

**Independent Test**: ejecutar el comando en el entorno local, comprobar que la cuenta existe
con la contraseña protegida y que un segundo alta con el mismo usuario se rechaza.

**Acceptance Scenarios**:

1. **Given** una base sin administradores, **When** el operador ejecuta el alta con un usuario
   válido e introduce dos veces la misma contraseña válida, **Then** se crea la cuenta activa y
   la contraseña se guarda solo de forma irreversible.
2. **Given** una cuenta existente, **When** se intenta dar de alta el mismo usuario, **Then** se
   rechaza sin modificar la cuenta y se indica el comando de restablecimiento.
3. **Given** una contraseña que no cumple la política (demasiado corta, igual al usuario o las dos
   entradas no coinciden), **When** se intenta el alta, **Then** se rechaza explicando el motivo.
4. **Given** una cuenta existente, **When** el operador restablece su contraseña, **Then** la
   contraseña anterior deja de servir y se revocan todas las sesiones de esa cuenta.

---

### User Story 2 - Entrar y salir del panel (Priority: P1)

Una persona de la organización abre `/admin`, introduce usuario y contraseña y ve el resumen del
panel con los datos privados. La sesión dura como máximo 8 horas. Al cerrar sesión, el acceso
queda revocado en el servidor y no solo oculto en la pantalla.

**Why this priority**: es el acceso a todas las funciones de gestión de las features siguientes.

**Independent Test**: con una cuenta creada, entrar en `/admin`, recargar, cerrar sesión y
comprobar que una petición privada con la sesión anterior se rechaza.

**Acceptance Scenarios**:

1. **Given** una cuenta activa, **When** se envían credenciales correctas, **Then** se muestra
   el resumen del panel y los datos privados se cargan.
2. **Given** una sesión iniciada, **When** se recarga la página o se reinician los servicios,
   **Then** la sesión sigue válida hasta su caducidad.
3. **Given** una sesión iniciada, **When** se pulsa cerrar sesión, **Then** vuelve la pantalla de
   acceso y cualquier petición privada con esa sesión se rechaza.
4. **Given** credenciales incorrectas (usuario inexistente o contraseña errónea), **When** se
   envían, **Then** se muestra el mismo mensaje genérico, sin indicar qué campo falló.
5. **Given** una sesión con más de 8 horas, **When** se hace cualquier petición privada,
   **Then** se rechaza y el panel pide volver a entrar.
6. **Given** el servicio de datos no disponible, **When** se intenta entrar, **Then** se muestra un
   error de servicio y nunca se concede acceso.

---

### User Story 3 - Proteger lecturas privadas y escrituras (Priority: P1)

Todo lo privado (borradores y datos internos) y toda escritura requieren una sesión válida. Las
escrituras exigen además venir del origen permitido de la web y llevar la protección contra
peticiones falsificadas. Las secciones del panel cuyas features todavía no están construidas
informan de que aún no guardan cambios, sin simular éxito.

**Why this priority**: es la garantía de seguridad que exigen la constitución (principio III) y
los criterios de aceptación de administración.

**Independent Test**: lanzar peticiones privadas y de escritura sin sesión, con sesión pero sin
protección CSRF y desde otro origen, y comprobar que todas se rechazan con el código adecuado.

**Acceptance Scenarios**:

1. **Given** ninguna sesión, **When** se piden datos privados o se intenta una escritura desde el
   origen permitido, **Then** se responde «no autorizado» (401).
2. **Given** una sesión válida, **When** se envía una escritura sin el comprobante CSRF o con uno
   que no corresponde a la sesión, **Then** se rechaza como prohibida (403).
3. **Given** cualquier escritura (incluidos acceso y cierre de sesión) desde un origen distinto del
   permitido o sin origen, **When** llega al servicio, **Then** se rechaza como prohibida (403).
4. **Given** una sesión válida en una sección del panel aún no migrada, **When** se pulsa guardar,
   **Then** se muestra que esa sección todavía no guarda cambios y no se modifica ningún dato.
5. **Given** las vistas de diseño `/pantallas/admin/...`, **When** se pulsa guardar, **Then** se
   sigue mostrando el aviso de vista de diseño sin ninguna escritura.

---

### User Story 4 - Limitar los intentos de acceso (Priority: P2)

Tras 8 intentos fallidos desde el mismo origen de red en 15 minutos, el acceso se bloquea para
ese origen hasta que pase la ventana, aunque la contraseña sea correcta. El bloqueo persiste
aunque el servicio se reinicie.

**Why this priority**: mitiga ataques de fuerza bruta; depende de que exista el acceso (US2).

**Independent Test**: enviar 8 intentos fallidos, comprobar que el 9.º (correcto o no) se bloquea
y que, pasada la ventana, se puede volver a entrar.

**Acceptance Scenarios**:

1. **Given** 8 intentos fallidos desde un origen en 15 minutos, **When** se intenta de nuevo
   (aunque sea con credenciales correctas), **Then** se responde «demasiados intentos» (429) y la
   pantalla muestra ese estado.
2. **Given** un origen bloqueado, **When** pasan 15 minutos desde el primer intento fallido de la
   ventana, **Then** se puede volver a intentar.
3. **Given** varios intentos fallidos seguidos de uno correcto antes del bloqueo, **When** se
   entra, **Then** el contador de ese origen se reinicia.
4. **Given** un origen bloqueado, **When** se reinicia el servicio, **Then** el bloqueo continúa.

---

### User Story 5 - Revocar el acceso (Priority: P2)

El operador puede desactivar una cuenta o revocar todas sus sesiones con un comando. Una cuenta
desactivada no puede entrar y sus sesiones abiertas dejan de servir inmediatamente.

**Why this priority**: permite reaccionar ante una pérdida de dispositivo o de credenciales.

**Independent Test**: con una sesión abierta, desactivar la cuenta o revocar sus sesiones y
comprobar que la siguiente petición privada se rechaza.

**Acceptance Scenarios**:

1. **Given** una sesión abierta, **When** el operador desactiva la cuenta, **Then** la siguiente
   petición privada se rechaza y la cuenta no puede volver a entrar hasta reactivarse.
2. **Given** una sesión abierta, **When** el operador revoca las sesiones de la cuenta, **Then**
   la siguiente petición privada se rechaza, pero la cuenta puede volver a entrar.

---

### Edge Cases

- Usuario con mayúsculas o espacios alrededor: se normaliza (sin espacios, minúsculas) tanto en
  el alta como en el acceso.
- Contraseña extremadamente larga o vacía: se rechaza sin coste excesivo de cálculo.
- Cookie de sesión manipulada, de otra instalación o de una sesión ya revocada: se trata como sin
  sesión.
- Dos sesiones simultáneas de la misma cuenta (dos navegadores): ambas válidas; cerrar una no
  cierra la otra.
- Acceso desde el servidor de desarrollo local (otro puerto): solo se permite si ese origen está
  configurado explícitamente como permitido.
- Base de datos caída durante el acceso: error de servicio (503), nunca acceso concedido.
- Intentos repetidos con usuarios distintos desde el mismo origen: cuentan para el mismo límite.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST permitir crear cuentas de administración solo mediante un comando
  de operador; MUST NOT existir registro público.
- **FR-002**: El comando de alta MUST pedir la contraseña de forma oculta y por duplicado (o leerla
  de la entrada estándar para automatización), nunca como argumento, y MUST NOT modificar una
  cuenta existente.
- **FR-003**: La política de contraseña MUST exigir al menos 12 caracteres, como máximo 128, y que
  sea distinta del usuario.
- **FR-004**: Las contraseñas MUST guardarse solo con un algoritmo de derivación resistente a
  ataques de memoria (Argon2id) y nunca en claro.
- **FR-005**: El operador MUST poder restablecer la contraseña, desactivar y reactivar una cuenta
  y revocar todas sus sesiones mediante comandos; restablecer o desactivar MUST revocar las
  sesiones abiertas de la cuenta.
- **FR-006**: El acceso MUST validar usuario y contraseña en el servidor y, si aciertan, crear una
  sesión con un identificador aleatorio no adivinable del que el servidor solo guarda una huella.
- **FR-007**: La sesión MUST caducar a las 8 horas de su creación (valor configurable) y MUST
  persistir entre reinicios del servicio.
- **FR-008**: El identificador de sesión MUST viajar en una cookie inaccesible para los scripts de
  la página, limitada al mismo sitio y marcada como segura en producción.
- **FR-009**: Los fallos de acceso MUST mostrar un único mensaje genérico, tanto si el usuario no
  existe como si la contraseña es errónea o la cuenta está desactivada, y su tiempo de respuesta
  no debe permitir distinguir los casos.
- **FR-010**: El sistema MUST bloquear el acceso desde un origen de red tras 8 intentos fallidos
  en una ventana de 15 minutos (valores configurables), respondiendo «demasiados intentos» (429)
  hasta que la ventana expire, indicando de forma legible por máquina los segundos de espera
  restantes; la pantalla muestra un aviso de espera sin revelar datos de la cuenta; un acceso
  correcto reinicia el contador; el contador MUST persistir entre reinicios.
- **FR-011**: El cierre de sesión MUST revocar la sesión en el servidor y borrar las cookies del
  navegador.
- **FR-012**: Toda lectura privada y toda escritura MUST requerir una sesión válida (no caducada,
  no revocada, de cuenta activa); sin ella se responde 401.
- **FR-013**: Toda escritura (incluidos acceso y cierre de sesión) MUST rechazarse con 403 si su
  origen no es uno de los permitidos (el origen público configurado y, opcionalmente, orígenes de
  desarrollo explícitos) o si no declara origen. «Escritura» es toda petición que crea, modifica o
  elimina datos o estado de sesión. Las comprobaciones se aplican en este orden: origen (403),
  sesión (401), comprobante CSRF (403).
- **FR-014**: Toda escritura autenticada MUST incluir un comprobante CSRF vinculado a la sesión;
  si falta o no coincide se responde 403.
- **FR-015**: La comprobación de sesión MUST informar si hay sesión válida y el usuario, sin
  exponer el identificador de sesión; si la sesión es válida pero el navegador no conserva el
  comprobante CSRF, MUST emitir uno nuevo vinculado a esa sesión.
- **FR-016**: Con sesión válida, la variante privada del contenido MUST devolver todos los
  elementos, incluidos los no publicados.
- **FR-017**: La pantalla de acceso MUST mostrar los estados: preparando, sin sesión, enviando,
  credenciales incorrectas, demasiados intentos y error de servicio; tras entrar MUST mostrar el
  resumen del panel.
- **FR-018**: Las secciones del panel cuya persistencia aún no existe MUST informar, al guardar,
  de que todavía no guardan cambios; MUST NOT modificar datos ni simular éxito.
- **FR-019**: Una sesión caducada o revocada MUST devolver al panel a la pantalla de acceso en la
  siguiente petición privada.
- **FR-020**: Las vistas de diseño `/pantallas/admin/...` MUST seguir sin enviar escrituras.
- **FR-021**: Las contraseñas, identificadores de sesión y comprobantes MUST NOT aparecer en
  registros, respuestas de error ni en el repositorio; las respuestas de error MUST ser mensajes
  genéricos sin detalles internos (trazas, consultas, configuración).

### Key Entities *(include if feature involves data)*

- **Administrador**: cuenta de la organización. Atributos: usuario único normalizado, huella de
  contraseña, estado (activo/inactivo), fechas de alta, actualización, último acceso y último
  cambio de contraseña.
- **Sesión**: acceso abierto por un administrador. Atributos: huella del identificador, huella del
  comprobante CSRF, creación, caducidad, revocación y último uso. Pertenece a un administrador.
- **Límite de acceso**: contador de intentos fallidos por origen de red (huella), con inicio de
  ventana.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Una persona de la organización entra al panel y ve el resumen en menos de 30
  segundos desde que abre `/admin`.
- **SC-002**: El 100 % de las peticiones privadas y de escritura sin sesión válida se rechazan
  (verificado sobre todas las rutas privadas existentes).
- **SC-003**: El 100 % de las escrituras sin origen permitido o sin comprobante CSRF válido se
  rechazan.
- **SC-004**: Tras el 8.º fallo, el 9.º intento desde el mismo origen se bloquea, y el bloqueo
  persiste tras reiniciar el servicio.
- **SC-005**: Tras cerrar sesión, desactivar la cuenta o revocar sesiones, el 100 % de las
  peticiones con la sesión anterior se rechazan.
- **SC-006**: Una sesión abierta sigue válida tras reiniciar todos los servicios.
- **SC-007**: Cero contraseñas, identificadores de sesión o comprobantes en claro en la base de
  datos, el repositorio, los registros o las respuestas de error.
- **SC-008**: Los mensajes de error de acceso son idénticos para usuario inexistente, contraseña
  errónea y cuenta desactivada.

## Assumptions

- Hay un único nivel de permiso: cualquier cuenta activa administra todo. No se gestionan roles
  ni varias cuentas desde la web (fuera de alcance), aunque el modelo admite varias cuentas
  creadas por comando.
- El «origen de red» del límite de intentos es la dirección del cliente que entrega la entrada
  web de confianza. El servicio no es accesible directamente desde fuera.
- La duración de sesión es absoluta: 8 horas desde el acceso, sin renovación por actividad, como
  referencia de la DOC 14.
- En desarrollo local por HTTP la cookie puede no marcarse como segura mediante configuración
  explícita. En producción siempre es segura.
- Las secciones del panel (noticias, galería, carreras…) se conectan a persistencia real en sus
  features (003–010). Hasta entonces se aplica FR-018.
- No hay cambio de contraseña desde la web ni recuperación por correo (fuera de alcance). La
  recuperación se hace con el comando de operador.
