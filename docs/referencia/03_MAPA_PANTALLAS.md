# Mapa de pantallas

El paquete contiene **16 fichas públicas/de revisión** y **24 fichas de administración**, con creación y edición documentadas por separado.

Cada ficha describe objetivo, composición, datos, acciones, estados y criterios de aceptación. Las rutas `:id` son dinámicas; los enlaces actuales de ejemplo se conservan en `/pantallas`.

## Web pública y revisión

| Pantalla | URL | Ficha |
|---|---|---|
| Inicio | `/` | [Abrir](screens/publica/01-inicio.md) |
| Pruebas y recorridos | `/carreras` | [Abrir](screens/publica/02-carreras.md) |
| Trail Peñasagra | `/carreras/trail-27k` | [Abrir](screens/publica/03-trail-27k.md) |
| Speed Trail | `/carreras/speed-14k` | [Abrir](screens/publica/04-speed-14k.md) |
| Familiar Peñasagra | `/carreras/familiar-7k` | [Abrir](screens/publica/05-familiar-7k.md) |
| Inscripciones | `/inscripciones` | [Abrir](screens/publica/06-inscripciones.md) |
| Noticias | `/noticias` | [Abrir](screens/publica/07-noticias.md) |
| Detalle de noticia | `/noticias/:id` | [Abrir](screens/publica/08-noticia-detalle.md) |
| Galería de imágenes | `/galeria` | [Abrir](screens/publica/09-galeria.md) |
| Detalle de álbum | `/galeria/:id` | [Abrir](screens/publica/10-album.md) |
| Clasificaciones | `/clasificaciones` | [Abrir](screens/publica/11-clasificaciones.md) |
| Reglamento | `/reglamento` | [Abrir](screens/publica/12-reglamento.md) |
| Corremos por Adriana | `/solidaridad` | [Abrir](screens/publica/13-solidaridad.md) |
| Patrocinadores y colaboradores | `/patrocinadores` | [Abrir](screens/publica/14-patrocinadores.md) |
| Contacto | `/contacto` | [Abrir](screens/publica/15-contacto.md) |
| Índice de revisión | `/pantallas` | [Abrir](screens/publica/16-indice-pantallas.md) |

## Administración

| Pantalla | URL | Ficha |
|---|---|---|
| Acceso de administrador | `/admin (sin sesión)` | [Abrir](screens/admin/01-acceso.md) |
| Resumen del administrador | `/admin (con sesión)` | [Abrir](screens/admin/02-resumen.md) |
| Noticias · listado | `/admin/noticias` | [Abrir](screens/admin/03-noticias-listado.md) |
| Noticias · crear | `/admin/noticias/nuevo` | [Abrir](screens/admin/04-noticias-nuevo.md) |
| Noticias · editar | `/admin/noticias/:id` | [Abrir](screens/admin/05-noticias-editar.md) |
| Clasificaciones · listado | `/admin/clasificaciones` | [Abrir](screens/admin/06-clasificaciones-listado.md) |
| Clasificaciones · crear | `/admin/clasificaciones/nuevo` | [Abrir](screens/admin/07-clasificaciones-nuevo.md) |
| Clasificaciones · editar | `/admin/clasificaciones/:id` | [Abrir](screens/admin/08-clasificaciones-editar.md) |
| Galería · listado | `/admin/galeria` | [Abrir](screens/admin/09-galeria-listado.md) |
| Galería · crear | `/admin/galeria/nuevo` | [Abrir](screens/admin/10-galeria-nuevo.md) |
| Galería · editar | `/admin/galeria/:id` | [Abrir](screens/admin/11-galeria-editar.md) |
| Pruebas y rutas · listado | `/admin/recorridos` | [Abrir](screens/admin/12-recorridos-listado.md) |
| Pruebas y rutas · crear | `/admin/recorridos/nuevo` | [Abrir](screens/admin/13-recorridos-nuevo.md) |
| Pruebas y rutas · editar | `/admin/recorridos/:id` | [Abrir](screens/admin/14-recorridos-editar.md) |
| Patrocinadores · listado | `/admin/patrocinadores` | [Abrir](screens/admin/15-patrocinadores-listado.md) |
| Patrocinadores · crear | `/admin/patrocinadores/nuevo` | [Abrir](screens/admin/16-patrocinadores-nuevo.md) |
| Patrocinadores · editar | `/admin/patrocinadores/:id` | [Abrir](screens/admin/17-patrocinadores-editar.md) |
| Colaboradores · listado | `/admin/colaboradores` | [Abrir](screens/admin/18-colaboradores-listado.md) |
| Colaboradores · crear | `/admin/colaboradores/nuevo` | [Abrir](screens/admin/19-colaboradores-nuevo.md) |
| Colaboradores · editar | `/admin/colaboradores/:id` | [Abrir](screens/admin/20-colaboradores-editar.md) |
| Inscripciones | `/admin/inscripciones` | [Abrir](screens/admin/21-inscripciones.md) |
| Fecha y contador | `/admin/evento` | [Abrir](screens/admin/22-evento.md) |
| Reglamento | `/admin/reglamento` | [Abrir](screens/admin/23-reglamento.md) |
| Contacto y ajustes | `/admin/ajustes` | [Abrir](screens/admin/24-ajustes.md) |

## Vistas de diseño del panel

Cada URL administrativa dispone de una vista de referencia anteponiendo `/pantallas`: por ejemplo, `/pantallas/admin/noticias/nuevo`. Usa datos iniciales y no permite persistir cambios. No es un mecanismo alternativo de acceso al CMS real.

El shell del administrador (barra lateral, contexto, ver web, mensajes y cierre de sesión) es compartido. Los listados, nuevos y editores son pantallas distintas aunque la implementación reutilice formularios.
