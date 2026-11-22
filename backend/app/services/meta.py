"""Metadatos de las páginas de detalle para el HTML inicial (feature 011, research R1).

Caddy incluye esta respuesta en `plantilla.html`: si empieza por `MARCADOR` la inserta en el
`<head>`; si es `NO_ENCONTRADA` responde 404. Solo se describen elementos publicados.
"""

import re
from dataclasses import dataclass
from html import escape

from sqlalchemy.orm import Session

from app.services import carreras, clasificaciones, galeria, noticias

MARCADOR = "<!-- meta -->"
NO_ENCONTRADA = "no-encontrada"
SITIO = "Trail Peñasagra"
# Misma imagen general que `IMAGEN_COMPARTIR` de frontend/src/seo/rutas.ts.
IMAGEN_GENERAL = "/reused/logos/corremos_por_adriana.webp"
IDENTIFICADOR = re.compile(r"^[A-Za-z0-9_-]{1,100}$")
ANIO = re.compile(r"^\d{4}$")
MAX_DESCRIPCION = 160


@dataclass(frozen=True)
class MetadatosPagina:
    titulo: str
    descripcion: str
    imagen: str
    canonica: str
    tipo: str = "website"


def _titulo(base: str) -> str:
    return base if "peñasagra" in base.lower() else f"{base} | {SITIO}"


def _recortar(texto: str) -> str:
    texto = " ".join(texto.split())
    if len(texto) <= MAX_DESCRIPCION:
        return texto
    corte = texto[: MAX_DESCRIPCION - 1].rsplit(" ", 1)[0].rstrip(",.;:")
    return corte + "…"


def _absoluta(origen: str, imagen: str) -> str:
    if imagen.startswith("https://"):
        return imagen
    return origen + (imagen if imagen.startswith("/") else IMAGEN_GENERAL)


def _buscar(items: list[dict], ident: str) -> dict | None:
    return next((i for i in items if i.get("id") == ident), None)


def resolver(db: Session, ruta: str, origen: str) -> MetadatosPagina | None:
    """Metadatos de `/seccion/identificador` publicada, o `None` si no existe (404)."""
    partes = ruta.strip("/").split("/")
    if not ruta.startswith("/") or len(partes) != 2:
        return None
    seccion, ident = partes
    if not IDENTIFICADOR.match(ident):
        return None
    origen = origen.rstrip("/")
    canonica = f"{origen}/{seccion}/{ident}"
    if seccion == "noticias" and (n := _buscar(noticias.listar(db, privado=False), ident)):
        return MetadatosPagina(
            _titulo(n["title"]),
            _recortar(n.get("excerpt") or n.get("body") or ""),
            _absoluta(origen, n.get("image") or ""),
            canonica,
            "article",
        )
    if seccion == "galeria" and (a := _buscar(galeria.listar(db, privado=False), ident)):
        return MetadatosPagina(
            _titulo(a["title"]),
            # Feature 012 · US11 (decisión P13): el título del álbum, entre comillas latinas.
            f"Fotografías de «{a['title']}» ({a['year']}).",
            _absoluta(origen, a.get("image") or ""),
            canonica,
        )
    if seccion in ("carreras", "recorridos") and (
        c := _buscar(carreras.listar(db, privado=False), ident)
    ):
        base = f"{c['title']} · {c['km']} km" if c.get("km") else c["title"]
        return MetadatosPagina(
            _titulo(base),
            _recortar(c.get("description") or ""),
            _absoluta(origen, c.get("image") or ""),
            canonica,
        )
    if seccion == "clasificaciones" and ANIO.match(ident):
        publicadas = clasificaciones.listar(db, privado=False)
        if any(str(r.get("year")) == ident for r in publicadas):
            return MetadatosPagina(
                _titulo(f"Clasificaciones {ident}"),
                f"Clasificaciones y resultados oficiales del Trail Sierra de Peñasagra {ident}.",
                _absoluta(origen, IMAGEN_GENERAL),
                canonica,
            )
    return None


def renderizar(meta: MetadatosPagina) -> str:
    """Etiquetas del `<head>` con todos los valores escapados (contracts/meta-y-rutas.md)."""
    t, d, i, u = (
        escape(v, quote=True) for v in (meta.titulo, meta.descripcion, meta.imagen, meta.canonica)
    )
    etiquetas = [
        f"<title>{t}</title>",
        f'<meta name="description" content="{d}" />',
        f'<meta property="og:type" content="{meta.tipo}" />',
        f'<meta property="og:site_name" content="{SITIO}" />',
        '<meta property="og:locale" content="es_ES" />',
        f'<meta property="og:title" content="{t}" />',
        f'<meta property="og:description" content="{d}" />',
        f'<meta property="og:image" content="{i}" />',
        f'<meta property="og:url" content="{u}" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{t}" />',
        f'<meta name="twitter:description" content="{d}" />',
        f'<meta name="twitter:image" content="{i}" />',
        f'<link rel="canonical" href="{u}" />',
    ]
    return MARCADOR + "\n    " + "\n    ".join(etiquetas)
