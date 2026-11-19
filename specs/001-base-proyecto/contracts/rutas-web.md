# Contrato de rutas web (feature 001)

Servidas por Caddy desde `frontend/dist` en el mismo origen que la API.

## Resolución de archivos

| Petición | Archivo servido | Metadatos |
|---|---|---|
| `/` | `index.html` | Inicio |
| `/carreras`, `/recorridos`, `/inscripciones`, `/noticias`, `/galeria`, `/clasificaciones`, `/reglamento`, `/solidaridad`, `/patrocinadores`, `/contacto` | `<ruta>/index.html` | Propios de la ruta |
| `/admin` y `/admin/*` | `admin/index.html` | Genéricos + `robots: noindex, nofollow` |
| `/pantallas` y `/pantallas/*` | `pantallas/index.html` | Genéricos + `robots: noindex, nofollow` |
| Recursos existentes (`/assets/*`, `/reused/*`, `/images/*`, `/fonts/*`, `/templates/*`, `robots.txt`) | El archivo | — |
| Cualquier otra ruta (detalles `/carreras/:id`, `/noticias/:id`, `/galeria/:id`, rutas inexistentes) | `app.html` | Genéricos (404 HTTP real en la feature 011) |
| `/api/*`, `/media/*` | Proxy a la API | — |

## Metadatos por ruta estática

| Ruta | Título | Descripción |
|---|---|---|
| `/` | Trail Sierra de Peñasagra – Corremos por Adriana | Web oficial del Trail Sierra de Peñasagra – Corremos por Adriana. Carrera solidaria de montaña en Cosío, Rionansa (Cantabria). |
| `/carreras` | Carreras y recorridos \| Trail Peñasagra | Trail 27K, Speed Trail 14K y Familiar 7K: distancia, desnivel, avituallamientos y recorrido de cada prueba. |
| `/recorridos` | Recorridos \| Trail Peñasagra | Recorridos del Trail Peñasagra: 27K, 14K y marcha familiar de 7K. Perfiles, avituallamientos y material. |
| `/inscripciones` | Inscripciones \| Trail Peñasagra | Estado de las inscripciones del Trail Peñasagra y acceso al Dorsal Solidario. |
| `/noticias` | Noticias \| Trail Peñasagra | Novedades y anuncios del Trail Sierra de Peñasagra. |
| `/galeria` | Galería \| Trail Peñasagra | Galería de fotos de las ediciones del Trail Sierra de Peñasagra. |
| `/clasificaciones` | Clasificaciones \| Trail Peñasagra | Clasificaciones y resultados oficiales del Trail Sierra de Peñasagra. |
| `/reglamento` | Reglamento \| Trail Peñasagra | Reglamento oficial del Trail Sierra de Peñasagra: precios, categorías, material, seguridad y normativa. |
| `/solidaridad` | Corremos por Adriana \| Trail Peñasagra | Por qué corremos: montaña, deporte y solidaridad. Colabora con el Dorsal Solidario. |
| `/patrocinadores` | Patrocinadores y colaboradores \| Trail Peñasagra | Empresas e instituciones que hacen posible el Trail Peñasagra. |
| `/contacto` | Contacto \| Trail Peñasagra | Contacta con la organización del Trail Sierra de Peñasagra. |
| genérico (`app.html`, admin, pantallas) | Trail Peñasagra · Corremos por Adriana | Montaña, deporte y solidaridad en Cosío, Rionansa. Descubre el Trail Peñasagra, sus recorridos y todas las novedades. |

Todas incluyen `og:type=website`, `og:title`, `og:description`, `og:image`
(`{PUBLIC_ORIGIN}/reused/logos/corremos_por_adriana.webp`), `og:url`, `twitter:card=summary_large_image`,
`twitter:title`, `twitter:description` y `<link rel="canonical">`.

## robots.txt

```
User-agent: *
Disallow: /admin
Disallow: /api/
Disallow: /pantallas
```
