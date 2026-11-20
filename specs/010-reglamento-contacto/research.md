# Research: Reglamento y contacto (010)

- **R1 Reglamento por edición**: columna `ediciones.reglamento` (texto, `''` por defecto, como
  máximo 200 000 caracteres). DOC 14 lo permite («texto asociado a la edición») y así comparte la
  versión de la edición con el evento y las inscripciones. *Alternativa descartada*: tabla
  `reglamentos` aparte, que añade una versión más sin ganar nada.
- **R2 Reglamento mostrado**: el de la edición actual o, si está vacío, el de la edición de año más
  alto con texto. En una base sin ediciones se sirve la semilla, como en las demás secciones. El
  editor muestra lo mismo: guardar sin cambios no envía nada y guardar cambios crea el reglamento
  de la edición actual.
- **R3 Normalización**: `\r\n` y `\r` → `\n` y se recortan los espacios exteriores. No se tocan
  los espacios internos ni las líneas en blanco, que separan los apartados.
- **R4 Contacto**: tabla `configuracion` de fila única (`id = 1`, CHECK) con columnas tipadas
  (`correo`, `telefono`, `instagram`) y `version`. *Alternativa descartada*: clave-valor, que pierde
  la validación por columna. La versión 0 crea la fila (mismo criterio que los demás recursos).
- **R5 Validación**:
  - Correo: `^[^@\s]+@[^@\s]+\.[^@\s]+$`, hasta 254 caracteres.
  - Teléfono: `^\+?[0-9 ()-]+$`, hasta 30 caracteres, con entre 6 y 15 dígitos.
  - Instagram: `url_externa_segura` con host `instagram.com` o `www.instagram.com`.
  - Etiquetas: «correo de la organización», «teléfono de contacto», «Instagram» y «reglamento».
- **R6 Retirada de `PUT /api/content`**: no quedan secciones sin recurso. Se elimina la ruta (405)
  y las pruebas de protección de la 002 pasan a `PUT /api/admin/contacto`, un endpoint real con la
  misma cadena Origin → sesión → CSRF. En el cliente, `planificar` devuelve un error local para
  cambios sin recurso, sin llamar al servidor (FR-011).
- **R7 Usuario de Instagram**: `@` + primer segmento de la ruta del enlace; si no se puede
  derivar, se muestra «Instagram». Con el dato actual el resultado es `@asociacion_penasagra`,
  igual que el texto fijo de la propuesta.
- **R8 Importación**:
  - Reglamento de la semilla en la edición 2026, si existe y ninguna edición tiene reglamento.
  - Contacto de la semilla si no hay fila.
  - `--reemplazar` borra las ediciones y, por tanto, su reglamento, que se vuelve a importar.
