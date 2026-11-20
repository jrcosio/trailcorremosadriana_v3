"""Feature 011 · US6: archivos subidos sin referencias (comando `limpiar-archivos`)."""

import io

import pytest

from app import cli
from app.storage.local import AlmacenamientoLocal
from tests.conftest import consultar

HUERFANO = "a" * 32 + ".webp"
EN_BORRADOR = "b" * 32 + ".jpg"
EN_PUBLICADO = "c" * 32 + ".png"
RECIENTE = "d" * 32 + ".webp"


@pytest.fixture
def escenario(base_importada, tmp_path):
    almacen = AlmacenamientoLocal(str(tmp_path))
    for clave, horas in ((HUERFANO, 48), (EN_BORRADOR, 72), (EN_PUBLICADO, 30), (RECIENTE, 2)):
        almacen.guardar(clave, b"contenido " + clave.encode(), "image/webp")
        consultar(
            base_importada,
            "INSERT INTO archivos (clave, tipo, tamano, sha256, creado_en) VALUES "
            f"('{clave}', 'image/webp', 42, '{'0' * 64}', now() - interval '{horas} hours')",
        )
    # Referencias desde un borrador y desde una ficha publicada (cualquier tabla y columna).
    consultar(
        base_importada,
        f"UPDATE noticias SET imagen = '/media/{EN_BORRADOR}', publicada = false "
        "WHERE slug = 'proxima-edicion'",
    )
    consultar(
        base_importada,
        "UPDATE albumes SET url_externa = '', "
        f"portada = 'https://web.example/media/{EN_PUBLICADO}' WHERE slug = 'edicion-2024'",
    )
    return base_importada, almacen, tmp_path


def _limpiar(url, almacen, *args, entrada=""):
    salida = io.StringIO()
    codigo = cli.main(
        ["limpiar-archivos", *args],
        database_url=url,
        entrada=io.StringIO(entrada),
        salida=salida,
        almacenamiento=almacen,
    )
    return codigo, salida.getvalue()


def _claves(url):
    return {c for (c,) in consultar(url, "SELECT clave FROM archivos")}


def test_listar_no_borra(escenario):
    url, almacen, carpeta = escenario
    codigo, texto = _limpiar(url, almacen)
    assert codigo == 0
    assert HUERFANO in texto and "1 archivo sin referencias" in texto
    assert EN_BORRADOR not in texto and EN_PUBLICADO not in texto and RECIENTE not in texto
    assert _claves(url) == {HUERFANO, EN_BORRADOR, EN_PUBLICADO, RECIENTE}
    assert (carpeta / HUERFANO).exists()


def test_borrar_exige_confirmacion_escrita(escenario):
    url, almacen, carpeta = escenario
    codigo, texto = _limpiar(url, almacen, "--borrar", entrada="si\n")
    assert codigo == 1 and "Cancelado" in texto
    assert HUERFANO in _claves(url) and (carpeta / HUERFANO).exists()


def test_borrar_solo_huerfanos_antiguos(escenario):
    url, almacen, carpeta = escenario
    codigo, texto = _limpiar(url, almacen, "--borrar", entrada="BORRAR\n")
    assert codigo == 0 and "1 archivo eliminado" in texto
    assert _claves(url) == {EN_BORRADOR, EN_PUBLICADO, RECIENTE}
    assert not (carpeta / HUERFANO).exists()
    for clave in (EN_BORRADOR, EN_PUBLICADO, RECIENTE):
        assert (carpeta / clave).exists()


def test_umbral_de_horas(escenario):
    url, almacen, _ = escenario
    _, texto = _limpiar(url, almacen, "--horas", "1")
    assert HUERFANO in texto and RECIENTE in texto
    _, texto = _limpiar(url, almacen, "--horas", "100")
    assert "No hay archivos sin referencias" in texto
    with pytest.raises(SystemExit):
        _limpiar(url, almacen, "--horas", "0")


def test_sin_huerfanos(base_importada, tmp_path):
    codigo, texto = _limpiar(base_importada, AlmacenamientoLocal(str(tmp_path)), "--borrar")
    assert codigo == 0 and "No hay archivos sin referencias con más de 24 horas." in texto
