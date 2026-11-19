"""Almacenamiento compatible con S3 (Cloudflare R2 en producción); credenciales en el servidor."""

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.storage import AlmacenamientoNoDisponible


class AlmacenamientoS3:
    def __init__(
        self,
        endpoint_url: str | None,
        bucket: str,
        region: str,
        access_key_id: str,
        secret_access_key: str,
        crear_bucket: bool = False,
    ) -> None:
        self.bucket = bucket
        self.cliente = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=access_key_id or None,
            aws_secret_access_key=secret_access_key or None,
            config=Config(connect_timeout=3, read_timeout=10, retries={"max_attempts": 2}),
        )
        self._crear_bucket = crear_bucket
        self._bucket_listo = not crear_bucket

    def _asegurar_bucket(self) -> None:
        if self._bucket_listo:
            return
        try:
            self.cliente.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.cliente.create_bucket(Bucket=self.bucket)
        self._bucket_listo = True

    def guardar(self, clave: str, datos: bytes, tipo: str) -> None:
        try:
            self._asegurar_bucket()
            self.cliente.put_object(Bucket=self.bucket, Key=clave, Body=datos, ContentType=tipo)
        except (BotoCoreError, ClientError) as exc:
            raise AlmacenamientoNoDisponible from exc

    def leer(self, clave: str) -> bytes | None:
        try:
            self._asegurar_bucket()
            respuesta = self.cliente.get_object(Bucket=self.bucket, Key=clave)
            return respuesta["Body"].read()
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in ("NoSuchKey", "404"):
                return None
            raise AlmacenamientoNoDisponible from exc
        except BotoCoreError as exc:
            raise AlmacenamientoNoDisponible from exc
