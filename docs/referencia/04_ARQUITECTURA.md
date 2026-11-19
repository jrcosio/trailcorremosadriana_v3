# Arquitectura actual y continuidad

El código incluido sigue utilizando Workers/D1/R2. La arquitectura de destino aprobada es FastAPI + PostgreSQL; se especifica en [14_BACKEND_FASTAPI_POSTGRESQL.md](14_BACKEND_FASTAPI_POSTGRESQL.md) para que la implemente el siguiente agente. Esta revisión del ZIP no contiene la migración implementada.

## Pila incluida

React 19.2.6, TypeScript 5.9.3, Vinext 1.0.0-beta.5 sobre Vite 8.0.13 y Cloudflare Workers. API mediante handlers de estilo App Router, D1 para datos y sesiones y R2 para archivos. Drizzle declara el esquema y genera migraciones SQLite. El lockfile fija las dependencias entregadas.

No es una aplicación estática: copiar solo un HTML no conserva el administrador, la persistencia ni las subidas.

## Organización

| Ruta | Responsabilidad |
|---|---|
| `app/[[...slug]]/page.tsx` | Convierte la URL en la prop `path` de la interfaz |
| `components/Site.tsx` | Cabecera, pie y pantallas públicas; contiene actualmente gran parte de la presentación |
| `components/admin/Admin.tsx` | Login, resumen, colecciones, editores y ajustes |
| `components/DorsalSolidario.tsx` | Bloques compartidos del dorsal solidario |
| `components/Results.tsx` / `ClassificationTable.tsx` | Clasificaciones públicas, búsqueda, filtros y paginación |
| `components/admin/ClassificationManager.tsx` / `ClassificationImport.tsx` | Gestión de CSV por carrera, columnas y vista previa |
| `lib/classifications.ts` / `classification-schema.ts` | Parser, normalización, exclusión solidaria y validación de servidor |
| `lib/registration.ts` | Validación y disponibilidad del enlace solidario |
| `lib/data.ts` | Datos iniciales, tipos amplios y filtro de publicaciones |
| `lib/server.ts` | Acceso a bindings, sesión, respuestas y lectura del documento de contenido |
| `app/api/` | Lecturas, guardado, autenticación y subida |
| `app/media/[...key]/route.ts` | Entrega de objetos de R2 |
| `db/schema.ts`, `drizzle/` | Tablas y migración inicial |
| `worker/index.ts` | Entrada del Worker de producción |
| `public/` | Fotos, logotipos, silueta y fuentes locales |

Las URLs son independientes, aunque varios componentes de pantalla comparten archivo físico. Modularizarlos es un trabajo de mantenibilidad pendiente, no una razón para cambiar rutas o rediseñar.

## Persistencia

Un documento JSON `SiteData` se almacena en la fila `content.id = main`, con número de revisión. El guardado usa comparación de revisión para evitar sobrescrituras silenciosas. Si no existe fila, se muestran los datos de `lib/data.ts`.

La copia del contenido publicado de este paquete está en `contenido/contenido-publicado.json`. No es una exportación de tablas de usuarios o sesiones. El importador local no sobrescribe una fila existente.

## Autenticación

El administrador real usa usuario y contraseña verificados en el servidor, PBKDF2-SHA256 y cookie de sesión HttpOnly, Secure y SameSite=Strict. Las sesiones se guardan por hash del token en D1 y caducan a las ocho horas. El límite actual bloquea tras ocho intentos en una ventana de quince minutos.

La privacidad del alojamiento de revisión mediante ChatGPT es una capa externa, diferente de la sesión del administrador. En un alojamiento propio, las páginas públicas deben seguir siendo públicas y las escrituras del administrador deben seguir protegidas por la aplicación.

## Evolución razonable

- Separar componentes de pantallas y formularios sin romper comportamiento.
- Sustituir `any`/`Record<string, any>` por tipos explícitos y validación compartida de todos los campos relevantes.
- Implementar la arquitectura aprobada de FastAPI y PostgreSQL con tablas normalizadas. El contrato JSON actual puede conservarse temporalmente como adaptador del frontend durante la transición; ver `14_BACKEND_FASTAPI_POSTGRESQL.md`.
- Aislar la infraestructura de Cloudflare si se elige otro proveedor. No confundir compatibilidad de componentes con compatibilidad directa de D1, R2 y `cloudflare:workers`.
- Definir un procedimiento explícito para credenciales, recuperación y copias de seguridad antes de usarlo como CMS de producción.
