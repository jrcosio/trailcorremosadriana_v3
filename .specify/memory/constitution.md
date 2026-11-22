# Constitución de Trail Peñasagra — Corremos por Adriana

## Core Principles

### I. Preservación visual

- Las pantallas, URLs y decisiones aprobadas (`docs/referencia/12_DECISIONES_APROBADAS.md`,
  `02_ESTILO_VISUAL.md` y `docs/referencia/screens/`) MUST conservarse al cambiar la
  implementación.
- MUST mantenerse: el título literal «TRAIL PEÑASAGRA» (TRAIL blanco, PEÑASAGRA naranja), la
  silueta de Adriana junto a la frase solidaria ampliada «Corremos por Adriana.», la ausencia de
  rótulo sobre el contador, el botón superior «INSCRIPCIONES» hacia `/inscripciones` y los
  logotipos de patrocinadores en tamaño grande sin recortar ni deformar.
- Toda feature que afecte a pantallas MUST revisarse visualmente a 360, 768, 1024 y 1440 px sin
  desbordamiento horizontal de la página.
- Un cambio visual sustancial MUST partir de una instrucción nueva del propietario.

Razón: el diseño ya está aprobado; el trabajo es de continuidad, no de rediseño.

### II. Persistencia real

- PostgreSQL con tablas relacionadas es la fuente de verdad, gestionado con SQLAlchemy y
  migraciones Alembic versionadas.
- MUST NOT usarse localStorage, memoria del proceso ni un documento JSON único como
  almacenamiento definitivo de contenidos.
- Los cambios guardados MUST sobrevivir a recargar la página y a reiniciar los servicios.
- Las escrituras de recursos editables MUST usar control de concurrencia optimista por versión y
  responder 409 ante conflicto, sin sobrescribir datos.
- Los borradores y datos no publicados MUST NOT aparecer en la API pública.

Razón: la organización debe actualizar la web sin tocar código y sin perder información.

### III. Seguridad del administrador

- El panel usa cuentas propias de la aplicación con contraseñas en Argon2id y sesiones opacas de
  servidor revocables; en base de datos solo se guarda el hash del token.
- La cookie de sesión MUST ser HttpOnly, con SameSite restrictivo y Secure en producción; el
  desarrollo local usa configuración específica sin debilitar la de producción.
- MUST existir un límite persistente de intentos de acceso y protección CSRF con comprobación de
  Origin en toda escritura autenticada.
- Los permisos MUST comprobarse en FastAPI; ocultar un botón no es control de acceso.
- MUST NOT versionarse secretos, contraseñas, `.env` reales ni credenciales de producción.
- Las vistas de demostración (`/pantallas/admin`) MUST NOT guardar cambios reales.

Razón: el panel controla contenido público y enlaces de pago de una causa solidaria.

### IV. Compatibilidad de datos y URLs

- MUST conservarse las URLs documentadas y las históricas de producción (`/recorridos`,
  `/clasificaciones/{año}`, `/galeria`, `/reglamento`, `/contacto`).
- La importación de datos existentes MUST ser repetible y MUST NOT sobrescribir una base con
  contenido sin una acción explícita.
- Los recursos reutilizados MUST conservar su procedencia y licencias.
- Los contratos de API consumidos por el frontend (p. ej. `/api/content`) MUST mantenerse hasta
  que sus consumidores se reconecten de forma coordinada.

Razón: hay enlaces compartidos, resultados históricos y contenido publicado que no deben romperse.

### V. Funcionalidades verificables

- Cada feature funcional MUST cerrar su recorrido completo (base de datos + API + interfaz
  administrativa + interfaz pública) cuando corresponda.
- Las integraciones con PostgreSQL MUST probarse con PostgreSQL real; los mocks solo valen para
  pruebas aisladas.
- MUST NOT declararse terminado lo que no se ha ejecutado y comprobado; los checklists de
  requisitos se marcan solo con evidencia de revisión.
- Cada feature termina con pruebas ejecutadas y sus resultados, documentación actualizada y un
  commit local revisable.

Razón: «funciona» significa comprobado contra los servicios reales de desarrollo.

### VI. Alcance controlado

- MUST NOT inventarse participantes, tiempos, fechas oficiales, patrocinadores, colaboradores ni
  enlaces de inscripción o pago.
- Inscripciones y pagos se completan en la plataforma externa enlazada; el Dorsal Solidario usa
  su URL específica, solo se activa con inscripciones abiertas y destino HTTPS válido, y no tiene
  clasificación.
- El contacto usa mailto mientras no se apruebe otro servicio.
- Se trabaja una feature cada vez, con especificaciones acotadas; no se crea una especificación
  única para toda la aplicación.

Razón: la web informa sobre un evento real y una causa real; los datos falsos causan daño.

## Restricciones técnicas

- Frontend: React + TypeScript con Vite, reutilizando componentes, estilos y recursos de la
  propuesta aprobada.
- Backend: FastAPI + Pydantic; PostgreSQL; SQLAlchemy; Alembic; Argon2id.
- Archivos: adaptador de almacenamiento local o compatible con S3 (Cloudflare R2 en producción);
  PostgreSQL guarda referencias y metadatos.
- Ejecución: Docker y Docker Compose; PostgreSQL solo en la red interna; migraciones como paso
  controlado.
- Fechas del evento interpretadas en Europe/Madrid y guardadas con zona horaria.
- Estructura del repositorio: `frontend/`, `backend/`, `infra/`, `docs/`, `specs/`.
- `datos_iniciales/` es referencia de solo lectura, ignorada por Git y por el contexto de Docker;
  el proyecto MUST compilar y funcionar sin ella.

## Flujo de desarrollo

- Spec-Driven Development con Spec Kit por feature: specify → clarify (cuando proceda) → plan →
  checklist (cuando aporte valor) → tasks → analyze → implement → pruebas → converge.
- La feature activa se identifica por `.specify/feature.json`; se comprueba al cambiar de feature.
- Rama Git por feature y merge local a `main` al cerrarla. Commits locales sin push, sin
  despliegues ni cambios de dominio o de producción.
- `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md` se actualizan al cerrar cada fase con estado,
  decisiones, pruebas, bloqueos y siguiente acción.
- Orden de autoridad: propietario > decisiones aprobadas > código de la propuesta > código de
  producción. Las discrepancias se registran en `docs/referencia/DISCREPANCIAS.md`.

## Governance

- Esta constitución prevalece sobre otras prácticas del proyecto.
- Las enmiendas se documentan en este archivo con versión semántica (MAJOR: retirar o redefinir
  principios; MINOR: añadir principios o secciones; PATCH: aclaraciones) y nota de impacto.
- Cada plan de feature MUST superar el Constitution Check antes de investigar y de nuevo tras el
  diseño; cualquier excepción se justifica en su tabla de complejidad.
- `/speckit-analyze` trata como CRÍTICO cualquier conflicto con estos principios.

Enmiendas:

- **1.0.1 (2026-11-22)**: en el principio I, el título literal de la portada pasa de «TRAIL
  PENASAGRA» a «TRAIL PEÑASAGRA», con Ñ, por instrucción del propietario (decisión P13; feature
  012, US11). Impacto: solo cambia la escritura de esa palabra; se mantienen las dos líneas, los
  colores y el tamaño. Los demás principios, las plantillas y los planes no cambian. Se anotan
  `docs/referencia/12_DECISIONES_APROBADAS.md` y `02_ESTILO_VISUAL.md`.

**Version**: 1.0.1 | **Ratified**: 2026-11-19 | **Last Amended**: 2026-11-22
