"""Feature 011 · Metadatos de página para Caddy (contracts/meta-y-rutas.md) y errores en español."""

import re

import pytest

from tests.conftest import consultar, crear_cliente, escribir
from tests.test_clasificaciones import _crear

ORIGEN = "http://localhost:8080"


def _meta(c, ruta):
    r = c.get("/api/meta", params={"ruta": ruta})
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/plain")
    assert r.headers["cache-control"] == "no-store"
    return r.text


def _etiqueta(texto, propiedad):
    m = re.search(rf'(?:property|name)="{re.escape(propiedad)}" content="([^"]*)"', texto)
    return m.group(1) if m else None


def test_noticia_publicada(admin_importado):
    texto = _meta(admin_importado, "/noticias/gracias-trail-2026")
    assert texto.startswith("<!-- meta -->")
    assert "<title>" in texto and texto.count("<title>") == 1
    assert _etiqueta(texto, "og:type") == "article"
    assert _etiqueta(texto, "og:url") == f"{ORIGEN}/noticias/gracias-trail-2026"
    assert _etiqueta(texto, "og:image") == f"{ORIGEN}/reused/noticias/gracias_2026.webp"
    assert f'<link rel="canonical" href="{ORIGEN}/noticias/gracias-trail-2026" />' in texto
    assert 0 < len(_etiqueta(texto, "description")) <= 165


def test_album_prueba_y_alias_recorridos(admin_importado):
    album = _meta(admin_importado, "/galeria/edicion-2026")
    assert _etiqueta(album, "og:title") == "Volver a sentir la montaña | Trail Peñasagra"
    # Feature 012 · US11 (P13): el título del álbum va entre comillas latinas.
    assert _etiqueta(album, "description") == "Fotografías de «Volver a sentir la montaña» (2026)."
    carrera = _meta(admin_importado, "/carreras/speed-14k")
    assert _etiqueta(carrera, "og:title").endswith("| Trail Peñasagra")
    assert "14 km" in _etiqueta(carrera, "og:title")
    alias = _meta(admin_importado, "/recorridos/speed-14k")
    assert _etiqueta(alias, "og:title") == _etiqueta(carrera, "og:title")
    assert _etiqueta(alias, "og:url") == f"{ORIGEN}/recorridos/speed-14k"
    # Un título que ya contiene «Peñasagra» no repite el nombre del sitio.
    reina = _meta(admin_importado, "/carreras/trail-27k")
    assert _etiqueta(reina, "og:title") == "Trail Peñasagra · 27 km"


def test_clasificaciones_por_anio(admin_importado):
    assert _meta(admin_importado, "/clasificaciones/2026") == "no-encontrada"
    _crear(admin_importado)  # clasificación publicada de 2026
    texto = _meta(admin_importado, "/clasificaciones/2026")
    assert _etiqueta(texto, "og:title") == "Clasificaciones 2026 | Trail Peñasagra"
    assert _meta(admin_importado, "/clasificaciones/2019") == "no-encontrada"
    assert _meta(admin_importado, "/clasificaciones/dos-mil") == "no-encontrada"


def test_escapado_e_imagen_de_reserva(admin_importado, base_importada):
    consultar(
        base_importada,
        "UPDATE noticias SET titulo = 'Uno <b>\"dos\"</b> & tres', imagen = '' "
        "WHERE slug = 'proxima-edicion'",
    )
    texto = _meta(admin_importado, "/noticias/proxima-edicion")
    assert "<b>" not in texto and '"dos"' not in texto
    assert "Uno &lt;b&gt;&quot;dos&quot;&lt;/b&gt; &amp; tres" in texto
    assert _etiqueta(texto, "og:image") == f"{ORIGEN}/reused/logos/corremos_por_adriana.webp"


def test_borrador_no_existe(admin_importado, base_importada):
    consultar(
        base_importada, "UPDATE noticias SET publicada = false WHERE slug = 'proxima-edicion'"
    )
    consultar(base_importada, "UPDATE albumes SET publicado = false WHERE slug = 'edicion-2025'")
    assert _meta(admin_importado, "/noticias/proxima-edicion") == "no-encontrada"
    assert _meta(admin_importado, "/galeria/edicion-2025") == "no-encontrada"


@pytest.mark.parametrize(
    "ruta",
    [
        "/noticias/inventada",
        "/galeria/inventado",
        "/carreras/inventada",
        "/no-existe",
        "/noticias",
        "/noticias/gracias-trail-2026/extra",
        "/noticias/../admin",
        "/noticias/a%20b",
        "/otra/gracias-trail-2026",
        "noticias/gracias-trail-2026",
        "/",
    ],
)
def test_rutas_no_encontradas(base_importada, ruta):
    with crear_cliente(base_importada) as anonimo:
        assert _meta(anonimo, ruta) == "no-encontrada"


def test_ruta_obligatoria_y_limitada(base_importada):
    with crear_cliente(base_importada) as anonimo:
        assert anonimo.get("/api/meta").status_code == 400
        assert anonimo.get("/api/meta", params={"ruta": "/" + "a" * 400}).status_code == 400


def test_errores_genericos_en_espanol(base_importada):
    with crear_cliente(base_importada) as c:
        r = c.get("/api/no-existe")
        assert r.status_code == 404 and r.json() == {"error": "No encontrado."}
        r = c.delete("/api/content")
        assert r.status_code == 405 and r.json() == {"error": "Método no permitido."}
        # Los 404 con mensaje propio no cambian.
        r = escribir(c, "DELETE", "/api/admin/noticias/x", params={"version": 1})
        assert r.status_code == 401
