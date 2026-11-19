"""Primitivas de seguridad: Argon2id, tokens opacos, huellas y política de credenciales."""

import hashlib
import hmac
import re
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_hasher = PasswordHasher()  # Argon2id, parámetros por defecto (RFC 9106, perfil de baja memoria)

PATRON_USUARIO = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
PASSWORD_MIN = 12
PASSWORD_MAX = 128
USUARIO_MAX = 64


class CredencialInvalida(ValueError):
    """Usuario o contraseña que no cumplen la política (mensaje apto para el operador)."""


def normalizar_usuario(usuario: str) -> str:
    return usuario.strip().lower()


def validar_usuario(usuario: str) -> str:
    normalizado = normalizar_usuario(usuario)
    if not PATRON_USUARIO.match(normalizado):
        raise CredencialInvalida(
            "El usuario debe tener entre 3 y 64 caracteres: letras minúsculas, números, '.', '_' o "
            "'-', y empezar por letra o número."
        )
    return normalizado


def validar_password(password: str, usuario: str) -> None:
    if len(password) < PASSWORD_MIN:
        raise CredencialInvalida(f"La contraseña debe tener al menos {PASSWORD_MIN} caracteres.")
    if len(password) > PASSWORD_MAX:
        raise CredencialInvalida(f"La contraseña no puede superar {PASSWORD_MAX} caracteres.")
    if password.strip().lower() == normalizar_usuario(usuario):
        raise CredencialInvalida("La contraseña no puede ser igual al usuario.")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verificar_password(hash_guardado: str, password: str) -> bool:
    try:
        return _hasher.verify(hash_guardado, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def necesita_rehash(hash_guardado: str) -> bool:
    return _hasher.check_needs_rehash(hash_guardado)


# Hash ficticio para igualar el tiempo de respuesta cuando el usuario no existe o está inactivo.
HASH_FICTICIO = _hasher.hash(secrets.token_urlsafe(32))


def nuevo_token() -> str:
    """Token opaco de 256 bits apto para cookie."""
    return secrets.token_urlsafe(32)


def huella(valor: str) -> str:
    """SHA-256 en hexadecimal (64 caracteres)."""
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()


def huellas_iguales(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("ascii"), b.encode("ascii"))
