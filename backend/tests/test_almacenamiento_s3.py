"""US3 · Almacenamiento compatible con S3 contra un servidor S3 real por HTTP (moto en Compose)."""

import os
import uuid

import pytest

from app.storage.s3 import AlmacenamientoS3
from tests.conftest import GPX, JPEG, PDF, PNG, WEBP, consultar, crear_cliente, entrar, subir

ENDPOINT = os.environ.get("S3_TEST_ENDPOINT_URL", "")
pytestmark = pytest.mark.skipif(not ENDPOINT, reason="Sin S3_TEST_ENDPOINT_URL (servicio s3-dev)")
CLAVE_ACCESO = os.environ.get("S3_TEST_ACCESS_KEY_ID", "")
CLAVE_SECRETA = os.environ.get("S3_TEST_SECRET_ACCESS_KEY", "")


def _ajustes_s3(bucket: str) -> dict:
    return {
        "almacenamiento": "s3",
        "s3_endpoint_url": ENDPOINT,
        "s3_bucket": bucket,
        "s3_region": "us-east-1",
        "s3_access_key_id": CLAVE_ACCESO,
        "s3_secret_access_key": CLAVE_SECRETA,
        "s3_crear_bucket": True,
    }


@pytest.fixture
def bucket() -> str:
    return f"trail-pruebas-{uuid.uuid4().hex[:10]}"


def test_ida_y_vuelta_identica(bucket):
    s3 = AlmacenamientoS3(
        ENDPOINT, bucket, "us-east-1", CLAVE_ACCESO, CLAVE_SECRETA, crear_bucket=True
    )
    clave = f"{uuid.uuid4().hex}.jpg"
    s3.guardar(clave, JPEG, "image/jpeg")
    assert s3.leer(clave) == JPEG
    assert s3.leer(f"{uuid.uuid4().hex}.jpg") is None


@pytest.mark.parametrize("datos", [JPEG, PNG, WEBP, PDF, GPX])
def test_subida_y_entrega_por_la_api_con_s3(base_con_admin, bucket, datos):
    with crear_cliente(base_con_admin, **_ajustes_s3(bucket)) as c:
        entrar(c)
        r = subir(c, datos, "archivo")
        assert r.status_code == 200, r.text
        entrega = c.get(r.json()["url"])
    assert entrega.status_code == 200
    assert entrega.content == datos


def test_sin_credenciales_ni_endpoint_en_respuestas(base_con_admin, bucket):
    with crear_cliente(base_con_admin, **_ajustes_s3(bucket)) as c:
        entrar(c)
        respuestas = [subir(c, JPEG, "a.jpg")]
        respuestas.append(c.get(respuestas[0].json()["url"]))
        respuestas.append(c.get("/media/0123456789abcdef0123456789abcdef.jpg"))
    for r in respuestas:
        texto = r.text if r.headers.get("content-type", "").startswith("application/json") else ""
        cabeceras = str(dict(r.headers))
        for secreto in (ENDPOINT, bucket, CLAVE_SECRETA or "∅", "s3-dev", "amazonaws"):
            assert secreto not in texto and secreto not in cabeceras


def test_s3_inaccesible_503_sin_fila(base_con_admin, bucket):
    ajustes = _ajustes_s3(bucket) | {"s3_endpoint_url": "http://127.0.0.1:1"}
    with crear_cliente(base_con_admin, **ajustes) as c:
        entrar(c)
        r = subir(c, JPEG, "a.jpg")
    assert r.status_code == 503
    assert consultar(base_con_admin, "SELECT count(*) FROM archivos")[0][0] == 0
