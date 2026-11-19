# Backend y base de datos: especificación para el agente de desarrollo

Estado: arquitectura aprobada y pendiente de implementación. Esta actualización del ZIP solo incorpora documentación. El código entregado sigue utilizando Cloudflare Workers, D1 y R2; no se ha migrado a FastAPI ni a PostgreSQL.

## Objetivo

Implementar el backend definitivo con FastAPI y PostgreSQL, conservando las pantallas, los recursos y los comportamientos aprobados. La implementación la realizará el agente que continúe este paquete con Claude Code o Codex.

Lee primero `../AGENTS.md`, el alcance, el estilo, el mapa de pantallas, la arquitectura actual y el contrato de clasificaciones CSV. Inspecciona el código antes de cambiarlo. La nueva arquitectura sustituye las recomendaciones anteriores de mantener indefinidamente el documento JSON como almacenamiento principal.

## Stack aprobado

| Componente | Elección | Responsabilidad |
|---|---|---|
| Frontend | React y TypeScript existentes | Conservar diseño, URLs, pantallas públicas y administrador |
| API | FastAPI y Pydantic | Validación, permisos, contenidos, archivos y clasificaciones |
| Persistencia | PostgreSQL | Tablas relacionadas, índices, transacciones e histórico de ediciones |
| Acceso a datos | SQLAlchemy | Modelos y operaciones de base de datos |
| Migraciones | Alembic | Cambios de esquema reproducibles y versionados |
| Contraseñas | Argon2id | Hash de contraseñas de cuentas propias |
| Sesiones | Tokens opacos y cookies seguras | Sesiones de administrador revocables desde el servidor |
| Archivos | Cloudflare R2 mediante su API compatible con S3 | Fotografías, logotipos y GPX; PostgreSQL guarda sus referencias |
| Ejecución | Docker y Docker Compose | Arranque local y configuración reproducible del despliegue |

El agente debe fijar versiones compatibles en los archivos de dependencias durante la implementación. No se impone aquí una versión futura no comprobada. Mantener la tecnología de presentación actual mientras sea viable; justificar cualquier adaptación del framework por su dependencia de Workers y preservar las características públicas existentes.

## Organización propuesta

Separar frontend, backend e infraestructura en el proyecto. La organización exacta puede adaptarse al código inspeccionado, pero debe quedar inequívoco qué proceso sirve cada parte.

| Carpeta propuesta | Contenido |
|---|---|
| `proyecto/frontend/` | Interfaz existente, componentes, estilos y recursos |
| `proyecto/backend/app/api/` | Rutas públicas y administrativas |
| `proyecto/backend/app/models/` | Modelos SQLAlchemy |
| `proyecto/backend/app/schemas/` | Contratos Pydantic de entrada y salida |
| `proyecto/backend/app/services/` | Importación CSV, publicación y reglas de negocio |
| `proyecto/backend/app/core/` | Configuración, autenticación y seguridad |
| `proyecto/backend/app/storage/` | Adaptador de archivos local/S3 |
| `proyecto/backend/alembic/` | Migraciones PostgreSQL |
| `proyecto/backend/tests/` | Pruebas de API y persistencia |
| `proyecto/infra/` | Configuración del proxy y herramientas operativas |
| `proyecto/compose.yaml` | Servicios, red interna, volúmenes y comprobaciones de salud |

Estas carpetas son la estructura prevista; todavía no existen en esta entrega como implementación de FastAPI.

## Modelo relacional

Las clasificaciones y sus participantes deben persistirse en tablas. El contrato JSON que consume hoy el frontend puede mantenerse temporalmente mediante un adaptador; no debe obligar a guardar toda la aplicación en una única fila.

| Tabla propuesta | Contenido y relaciones |
|---|---|
| `ediciones` | Año único, fecha/hora con zona, estado del evento y configuración de esa edición |
| `carreras` | Identidad estable y slug de la prueba; conservar URLs aprobadas |
| `carreras_edicion` | Carrera + edición, distancia, desnivel, precio de presentación, recorrido, GPX, horarios, imagen y enlace de inscripción |
| `clasificaciones` | Referencia única a una carrera de una edición, título, estado borrador/publicado, versión y metadatos de importación |
| `resultados` | Clasificación, posición general nullable, dorsal, nombre, tiempo, categoría, club, sexo, estado y orden de origen |
| `noticias` | Título, categoría, fecha, resumen, cuerpo, imagen, estado y versión |
| `albumes` | Título, edición, portada, enlace histórico externo, estado y orden |
| `fotografias` | Álbum, archivo, texto alternativo y orden |
| `entidades` | Nombre, tipo patrocinador/colaborador, logotipo, web, orden y visibilidad |
| `archivos` | Clave de almacenamiento, tipo, tamaño y datos necesarios para gestionar su acceso y uso |
| `administradores` | Usuario único, hash de contraseña, estado y fechas de gestión |
| `sesiones` | Administrador, hash del token de sesión, vencimiento y revocación |
| `limites_login` | Contadores y vencimiento para el control persistente de intentos |
| `configuracion` | Contacto, redes y ajustes generales que no pertenecen a una edición |

El reglamento puede guardarse como texto asociado a la edición. El contador, la apertura global de inscripciones, el mensaje de disponibilidad y la URL específica del dorsal solidario deben quedar asociados a la edición que corresponda. Patrocinadores y colaboradores mantienen secciones distintas aunque compartan modelo.

Restricciones obligatorias:

- Una combinación de carrera y edición en `carreras_edicion`.
- Una clasificación por carrera/edición; al sustituir el CSV se actualiza ese registro.
- Dorsal único dentro de una clasificación; el mismo dorsal puede existir en otra carrera o edición.
- Claves foráneas válidas e índices para relaciones y consultas públicas.
- Control de concurrencia por versión/revisión para evitar sobrescrituras silenciosas.
- Posición numérica positiva o nula; un participante no clasificado conserva su estado y no recibe puesto inventado.
- El tiempo de presentación y el dorsal se conservan como texto. Si se añade un tiempo numérico para ordenar, debe derivarse con un formato conocido y conservar el valor original.

El Dorsal Solidario se configura como modalidad de colaboración/pago de la edición. No se registra como carrera clasificable ni puede tener filas de clasificación. Preservar su presencia en Inicio, Solidaridad e Inscripciones.

## Contratos de API y transición del frontend

El frontend actual utiliza `/api/content`, `/api/login`, `/api/session`, `/api/logout`, `/api/upload` y `/media/...`. El agente debe revisar sus consumidores y mantenerlos operativos durante la transición o modificarlos de forma coordinada. No retirar rutas antes de conectar los componentes que dependen de ellas.

| Área | Contrato objetivo |
|---|---|
| Autenticación | Inicio de sesión, consulta de sesión y cierre de sesión |
| Contenido público | Solo datos publicados; nunca hashes, sesiones ni borradores |
| Gestión de contenido | Crear, leer, editar, publicar y retirar cada recurso con permisos en el servidor |
| Clasificaciones | Consulta por carrera/edición y búsqueda/paginación de participantes en el servidor |
| Importación CSV | Vista previa validada y confirmación de importación para una carrera/edición |
| Archivos | Subida autenticada, entrega controlada y referencias persistentes |
| Estado del servicio | Endpoints de salud y disponibilidad para despliegue y pruebas |

Las operaciones del panel deben requerir sesión válida y comprobar permisos en FastAPI. Un botón oculto no sustituye una comprobación del servidor. Documentar la API en OpenAPI y añadir contratos TypeScript explícitos para el frontend.

Se recomienda servir frontend y `/api` bajo el mismo origen mediante un proxy. Si se separan los orígenes, configurar explícitamente CORS con credenciales y los dominios permitidos. No usar comodines para escrituras autenticadas.

## Autenticación del administrador

- Cuentas propias de la aplicación; la versión independiente no requiere iniciar sesión en ChatGPT.
- Hash Argon2id, sin guardar contraseñas en texto claro ni incluir credenciales de producción en el repositorio o ZIP.
- Cookie de sesión `HttpOnly`, `Secure` en producción, `SameSite` apropiado y alcance limitado. El token opaco solo se entrega al navegador; en PostgreSQL se guarda su hash.
- Sesiones con caducidad y revocación al cerrar sesión o desactivar la cuenta. Mantener como referencia la duración actual de ocho horas, documentando cualquier ajuste.
- Control persistente de intentos de login; conservar o justificar el límite actual de ocho intentos por quince minutos.
- Protección CSRF para las operaciones autenticadas con cookies y comprobación del origen de las escrituras.
- Comando de creación o recuperación del administrador mediante entrada segura. No habilitar registro público de administradores.
- Prever desarrollo local con configuración específica; no debilitar las cookies de producción para resolver HTTP local.

La elección de sesiones opacas evita introducir JWT como requisito sin una necesidad del proyecto. Si se propone otro mecanismo, justificar cómo conserva cierre de sesión efectivo, vencimiento y revocación.

## Clasificaciones CSV en el backend definitivo

Conservar la experiencia descrita en [13_CLASIFICACIONES_CSV.md](13_CLASIFICACIONES_CSV.md), trasladando la validación autorizada al backend y las filas a PostgreSQL.

1. El administrador selecciona carrera y edición y envía el CSV para validar su vista previa.
2. FastAPI comprueba sesión, carrera clasificable, tamaño, codificación, delimitador, cabeceras y asignación de columnas.
3. Valida filas, campos obligatorios y dorsales duplicados y devuelve una vista previa y errores comprensibles.
4. La confirmación identifica exactamente los datos revisados. Puede reutilizarse el archivo y el mapeo con una huella de contenido o una importación temporal vinculada a la sesión; documentar e implementar la opción elegida.
5. Al confirmar, se revalidan permisos, contenido y versión del registro. La sustitución de filas y la actualización de metadatos se realizan dentro de una transacción PostgreSQL.
6. Si cualquier paso falla, permanece la clasificación anterior. No insertar la mitad de un CSV ni mezclarlo con el archivo anterior.
7. Las consultas públicas filtran clasificación publicada y ofrecen búsqueda por nombre/dorsal/club, categoría, sexo y paginación. Conservar posiciones generales al filtrar.

Mantener los formatos soportados por el contrato actual y las filas NC/DNF/DNS/DSQ. Los límites iniciales de 1 MB y 5.000 participantes por CSV deben configurarse y verificarse en el servidor. El límite global de 3 MB del documento JSON es una limitación del prototipo; debe dejar de condicionar las tablas de resultados de la arquitectura nueva.

Guardar las filas normalizadas y los metadatos de importación. La conservación del CSV original en un objeto privado sería una ampliación opcional: no publicarlo ni conservar columnas descartadas por defecto. La plantilla contiene ejemplos ficticios y no se importa como clasificación oficial.

## Imágenes, GPX y almacenamiento

Utilizar R2 mediante un adaptador compatible con S3, configurable por entorno. PostgreSQL guarda referencias y metadatos; los archivos se almacenan como objetos. Para arrancar y probar sin credenciales de producción, permitir un adaptador de archivos local con volumen persistente o un servicio compatible con S3 de desarrollo.

Conservar las fotografías, logotipos, fuentes y la silueta originales incluidos en `public/`. Copiar los archivos publicados exportados en `contenido/media/` cuando se importen sus referencias. Los álbumes históricos externos siguen siendo enlaces; no presentar sus fotos como descargadas si no se han importado.

Validar tipo, tamaño y contenido básico de las subidas, generar claves propias y bloquear rutas arbitrarias. Definir el acceso a archivos de borradores y evitar exponer credenciales S3 en el navegador. La retirada de un contenido y el borrado físico de su archivo son operaciones distintas; no borrar un objeto todavía referenciado.

## Reglas de producto que deben conservarse

- Todas las URLs y fichas del mapa de pantallas; no introducir un rediseño al cambiar el backend.
- Título literal «TRAIL PENASAGRA», silueta de Adriana, textos ampliados, patrocinadores grandes y ausencia del rótulo retirado sobre el contador.
- Apertura/cierre de inscripciones y URL HTTPS específica del pago solidario. Se habilita el enlace solo cuando se cumplen ambas condiciones.
- El Dorsal Solidario permanece fuera de las clasificaciones, también en las validaciones del servidor.
- Estados borrador/publicado, errores claros, control de versiones y persistencia tras recargar.
- `/pantallas/admin` continúa como demostración sin escritura, distinta del panel autenticado `/admin`.
- Fecha del evento interpretada con Europe/Madrid y guardada con zona horaria; ninguna fecha de 2027 se inventa.
- Inscripciones y pagos se completan en los enlaces externos configurados. El contacto sigue usando mailto hasta que se apruebe otra integración.

## Docker y configuración

Preparar Dockerfiles y un Compose con frontend/proxy, backend y PostgreSQL. PostgreSQL debe quedar en la red interna; publicar solo los puertos necesarios. Incluir volúmenes persistentes, comprobaciones de salud y orden de arranque. Ejecutar las migraciones como un paso controlado para evitar carreras entre procesos.

Documentar las variables por nombre, sin valores reales: conexión PostgreSQL, origen público, opciones de cookie, duración de sesión, límites CSV/subidas, adaptador de almacenamiento y configuración S3/R2. Proporcionar `.env.example`; el archivo local real queda excluido del control de versiones y de la entrega.

El arranque debe permitir aplicar migraciones, importar los datos publicados y crear el administrador local. Ningún comando de inicialización debe sobrescribir una base con contenido sin una acción explícita.

Preparar instrucciones de copia y restauración de PostgreSQL y del almacenamiento de archivos, actualización de versión y recuperación del administrador. El destino de producción, las credenciales y el cambio de dominio se concretan posteriormente; este documento no autoriza publicar sobre la propuesta existente.

## Plan de implementación para el siguiente agente

1. Inventariar las rutas, validaciones, datos y recursos actuales. Registrar una referencia de las pantallas antes de modificar el backend.
2. Crear el backend FastAPI, modelos SQLAlchemy y migración inicial Alembic; arrancar PostgreSQL de desarrollo.
3. Implementar sesiones, login, logout, permisos y protección de escrituras.
4. Importar `contenido/contenido-publicado.json` a las tablas y trasladar las referencias de archivos. Esta exportación contiene solo información pública, no cuentas, sesiones ni borradores.
5. Conectar la gestión de noticias, álbumes, pruebas, entidades y configuración con persistencia relacional.
6. Implementar la vista previa/confirmación CSV y las consultas de resultados en PostgreSQL.
7. Conectar el frontend manteniendo su apariencia y las URLs; retirar las dependencias del backend Worker/D1 solo cuando sus sustitutos funcionen.
8. Completar Docker, variables, comandos de arranque, pruebas de integración y documentación operativa.

Para una migración real de producción habrá que disponer de una exportación autorizada de los datos privados que se quieran conservar. No deducir cuentas o borradores desde el contenido publicado ni reutilizar las sesiones del alojamiento anterior.

## Aceptación y entrega esperada

- PostgreSQL real en las pruebas de integración relevantes; no afirmar compatibilidad comprobada únicamente con SQLite.
- Alembic aplica el esquema sobre una base vacía y existe un procedimiento probado de copia/restauración.
- El contenido guardado y las subidas sobreviven a reiniciar los servicios.
- Inicio/cierre de sesión, caducidad, intentos, CSRF y acceso privado tienen pruebas útiles.
- Publicar/retirar noticias, álbumes, entidades y clasificaciones actualiza correctamente la web pública.
- Dos actualizaciones concurrentes no se sobrescriben silenciosamente.
- Un CSV válido se puede revisar, confirmar y consultar; uno inválido no altera los resultados existentes.
- Unicidad por carrera/edición y por dorsal dentro de la clasificación, sin restringir dorsales de otras carreras.
- El Dorsal Solidario no puede seleccionarse ni crearse como clasificación y sigue disponible para colaborar.
- Los ejemplos ficticios no aparecen como resultados oficiales.
- Las pantallas conservan diseño y comportamiento en móvil y escritorio.
- Entregar código, migraciones, Compose, instrucciones, pruebas ejecutadas y limitaciones verificables. No dar por migrado algo que solo figure en documentación.

## Referencias técnicas oficiales

- [FastAPI: plantilla full stack](https://fastapi.tiangolo.com/project-generation/)
- [FastAPI: despliegue con Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [FastAPI: hashing de contraseñas](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [PostgreSQL: restricciones](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [PostgreSQL: transacciones](https://www.postgresql.org/docs/current/tutorial-transactions.html)
- [Cloudflare R2: API compatible con S3](https://developers.cloudflare.com/r2/api/s3/)
