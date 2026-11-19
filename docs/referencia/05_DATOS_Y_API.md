# Modelo de datos y API

## Documento SiteData

| Clave | Campos principales |
|---|---|
| `settings` | `edition`, `date`, `countdown`, `registrationsOpen`, `solidarityRegistration`, `registrationMessage`, `email`, `phone`, `instagram` |
| `races[]` | `id`, `title`, `label`, `km`, `elevation`, `price`, `image`, `description`, `terrain`, `start`, `route`, `wikiloc`, `gpx`, `registration`, `edition`, `aid`, `published` |
| `news[]` | `id`, `title`, `category`, `date`, `image`, `excerpt`, `body`, `published` |
| `albums[]` | `id`, `title`, `year`, `image`, `url`, `photos[]`, `published` |
| `results[]` | `id`, `title`, `year`, `raceId`, `race`, `sourceFile`, `importedAt`, `rows[]`, `published` |
| `sponsors[]` / `collaborators[]` | `id`, `name`, `image`, `url`, `order`, `published` |
| `regulation` | Texto del reglamento, con apartados separados por líneas en blanco |

`date` del evento se guarda como ISO; la entrada y la presentación del evento usan Europe/Madrid. Los precios actuales son texto, no importes de una pasarela propia.

## Tablas D1

| Tabla | Campos | Uso |
|---|---|---|
| `content` | `id`, `value`, `revision` | Documento de contenido y control de concurrencia |
| `sessions` | `token`, `expires` | Hash de sesión y vencimiento |
| `login_limits` | `id`, `attempts`, `start` | Límite de intentos de acceso |

## Endpoints

| Método y ruta | Acceso | Contrato |
|---|---|---|
| `GET /api/content` | Público en la aplicación | `{ data, revision }`; filtra elementos no publicados |
| `GET /api/content?admin=1` | Sesión de administrador | Documento completo con borradores |
| `PUT /api/content` | Sesión + Origin del mismo sitio | `{ data, revision }`; devuelve `{ ok, revision }` |
| `POST /api/login` | Formulario de acceso + mismo Origin | `{ username, password }`; fija cookie al acertar |
| `GET /api/session` | Cualquier visitante | `{ authenticated }` |
| `POST /api/logout` | Mismo Origin | Elimina sesión y cookie |
| `POST /api/upload` | Sesión + mismo Origin | FormData con `file`; devuelve `{ url: '/media/…' }` |
| `GET /media/:key` | Lectura | Bytes, tipo de contenido, ETag y caché del archivo |

El alojamiento privado de revisión puede exigir además su propia autenticación antes de que la petición llegue a la aplicación.

## Estados relevantes

- `400`: datos o formato inválidos, o apertura sin ningún destino de inscripción.
- `401`: falta sesión o ha caducado.
- `403`: origen no permitido; en subida también acceso no autorizado.
- `409`: la revisión no coincide; recargar antes de guardar para no pisar otra sesión.
- `413`: petición o archivo demasiado grande.
- `429`: demasiados intentos de acceso.
- `500/503`: error de servicio o configuración; no simular éxito en la interfaz.

## Límites actuales

Documento de guardado cercano a 3 MB; hasta 30 pruebas, 500 noticias, 200 álbumes, 500 fotos por álbum, 500 registros de clasificación y 200 entidades por tipo. Los resultados se importan como CSV de hasta 1 MB y 5.000 participantes, sin pasar por `/api/upload`: se leen en el navegador y sus filas normalizadas se guardan mediante `PUT /api/content`. El límite total del documento sigue siendo 3 MB. La subida genérica de archivos admite hasta 10 MB: JPG, PNG, WebP, PDF y GPX; la pantalla de clasificaciones solo ofrece CSV. El servidor comprueba firma básica/formato; SVG no se admite como subida del CMS.

El enlace solidario admite únicamente HTTPS sin credenciales embebidas. Otros campos URL tienen validación más básica y admiten recursos internos conocidos. La mejora de tipos y validación integral es una tarea de continuidad.

## Ejemplo conceptual de guardado

```json
{
  "revision": 3,
  "data": {
    "settings": { "edition": "2027", "registrationsOpen": false },
    "races": [],
    "news": [],
    "albums": [],
    "results": [],
    "sponsors": [],
    "collaborators": [],
    "regulation": "..."
  }
}
```

Es un esquema explicativo abreviado. Para una petición real hay que enviar todos los campos obligatorios de `settings` y del documento, tomando el contenido completo de una lectura previa. La referencia exacta de validación es `app/api/content/route.ts`.

## Resultados normalizados

Cada fila de `results[].rows` contiene `position: number | null`, `bib`, `name`, `time`, `category`, `club`, `gender` y `status`. Los tiempos y dorsales se conservan como texto. El nombre combina la columna de nombre con apellidos si se asigna. Las columnas sobrantes del CSV no se guardan. `raceId` referencia una carrera; `race` conserva su nombre descriptivo. El servidor limita los campos, rechaza dorsales repetidos y evita dos CSV de la misma carrera y edición. Los antiguos enlaces sin filas se conservan como datos privados de compatibilidad hasta su reimportación desde CSV. No se convierte un PDF automáticamente.
