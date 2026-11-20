"""Comando de operador para administrar cuentas del panel.

Uso: python -m app.cli <subcomando> …   (ver specs/002-administrador/contracts/cli-operador.md)
La contraseña se pide de forma oculta (dos veces) o se lee de stdin con --password-stdin;
nunca se acepta como argumento ni se imprime.
"""

import argparse
import getpass
import sys
from typing import TextIO

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import crear_engine
from app.core.seguridad import CredencialInvalida
from app.services import administradores, clasificaciones, importacion
from app.services.administradores import AdminNoEncontrado, AdminYaExiste
from app.services.csv_clasificaciones import (
    CsvNoValido,
    adivinar_mapeo,
    decodificar,
    leer_csv,
    mapear,
)

OK, ERROR, INVALIDO = 0, 1, 2


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m app.cli", description="Administración de cuentas del panel"
    )
    sub = p.add_subparsers(dest="orden", required=True)
    for nombre, ayuda in (
        ("crear-admin", "Crea una cuenta de administración (no modifica una existente)"),
        ("restablecer-password", "Cambia la contraseña y revoca las sesiones abiertas"),
    ):
        s = sub.add_parser(nombre, help=ayuda)
        s.add_argument("usuario")
        s.add_argument(
            "--password-stdin", action="store_true", help="Lee la contraseña de la entrada estándar"
        )
    for nombre, ayuda in (
        ("desactivar", "Desactiva la cuenta y revoca sus sesiones"),
        ("activar", "Reactiva la cuenta"),
        ("revocar-sesiones", "Revoca todas las sesiones abiertas de la cuenta"),
    ):
        sub.add_parser(nombre, help=ayuda).add_argument("usuario")
    sub.add_parser("listar-admins", help="Lista las cuentas (sin datos sensibles)")
    clas = sub.add_parser(
        "importar-clasificacion", help="Importa un CSV (por stdin) como clasificación"
    )
    clas.add_argument(
        "--carrera", required=True, help="Identificador de la prueba (p. ej. trail-27k)"
    )
    clas.add_argument("--edicion", required=True, help="Año de la edición (p. ej. 2026)")
    clas.add_argument("--titulo", required=True)
    clas.add_argument("--archivo", default="clasificacion.csv", help="Nombre del archivo de origen")
    clas.add_argument("--publicar", action="store_true")
    clas.add_argument(
        "--sustituir", action="store_true", help="Sustituye una clasificación existente"
    )
    imp = sub.add_parser(
        "importar-inicial", help="Importa los datos aprobados en las partes vacías"
    )
    imp.add_argument(
        "--reemplazar",
        action="store_true",
        help="Borra y vuelve a importar (pide confirmación escrita)",
    )
    return p


class _NoCoinciden(Exception):
    pass


def _leer_password(desde_stdin: bool, entrada: TextIO) -> str:
    if desde_stdin:
        return entrada.readline().rstrip("\r\n")
    primera = getpass.getpass("Contraseña: ")
    segunda = getpass.getpass("Repite la contraseña: ")
    if primera != segunda:
        raise _NoCoinciden
    return primera


def main(
    argv: list[str] | None = None,
    database_url: str | None = None,
    entrada: TextIO | None = None,
    salida: TextIO | None = None,
) -> int:
    args = _parser().parse_args(argv)
    entrada = entrada or sys.stdin
    salida = salida or sys.stdout

    def decir(texto: str) -> None:
        print(texto, file=salida)

    engine = crear_engine(database_url or get_settings().database_url)
    try:
        with Session(engine) as db:
            if args.orden == "crear-admin":
                password = _leer_password(args.password_stdin, entrada)
                admin = administradores.crear(db, args.usuario, password)
                decir(f"Administrador «{admin.usuario}» creado.")
            elif args.orden == "restablecer-password":
                password = _leer_password(args.password_stdin, entrada)
                n = administradores.restablecer_password(db, args.usuario, password)
                decir(f"Contraseña restablecida. {n} sesiones revocadas.")
            elif args.orden == "desactivar":
                n = administradores.desactivar(db, args.usuario)
                decir(f"Cuenta desactivada. {n} sesiones revocadas.")
            elif args.orden == "activar":
                administradores.activar(db, args.usuario)
                decir("Cuenta activada.")
            elif args.orden == "revocar-sesiones":
                n = administradores.revocar_sesiones(db, args.usuario)
                decir(f"{n} sesiones revocadas.")
            elif args.orden == "importar-inicial":
                if args.reemplazar:
                    decir(
                        "Esto borrará el evento y las pruebas. Escribe REEMPLAZAR para continuar:"
                    )
                    if entrada.readline().strip() != "REEMPLAZAR":
                        decir("Cancelado. No se ha modificado nada.")
                        return ERROR
                acciones = importacion.importar(db, reemplazar=args.reemplazar)
                decir(
                    "\n".join(acciones)
                    if acciones
                    else "Sin cambios: los datos ya estaban importados."
                )
            elif args.orden == "importar-clasificacion":
                datos = (
                    entrada.buffer.read() if hasattr(entrada, "buffer") else entrada.read().encode()
                )
                tabla = leer_csv(decodificar(datos))
                filas = mapear(tabla, adivinar_mapeo(tabla.cabeceras))
                accion, n = clasificaciones.importar_directo(
                    db,
                    args.carrera,
                    args.edicion,
                    args.titulo,
                    args.archivo,
                    filas,
                    args.publicar,
                    args.sustituir,
                )
                decir(f"Clasificación {accion}: {n} participantes.")
            elif args.orden == "listar-admins":
                cuentas = administradores.listar(db)
                if not cuentas:
                    decir("No hay administradores.")
                for a in cuentas:
                    acceso = (
                        a.ultimo_acceso_en.isoformat(timespec="minutes")
                        if a.ultimo_acceso_en
                        else "nunca"
                    )
                    decir(
                        f"{a.usuario}\t{'activo' if a.activo else 'inactivo'}\t"
                        f"último acceso: {acceso}"
                    )
        return OK
    except (CsvNoValido, clasificaciones.ClasificacionRechazada) as e:
        decir(str(e))
        return INVALIDO
    except _NoCoinciden:
        decir("Las contraseñas no coinciden.")
        return INVALIDO
    except CredencialInvalida as e:
        decir(str(e))
        return INVALIDO
    except AdminYaExiste as e:
        decir(
            f"El administrador «{e}» ya existe. "
            "Usa `restablecer-password` para cambiar su contraseña."
        )
        return ERROR
    except AdminNoEncontrado as e:
        decir(f"No existe el administrador «{e}».")
        return ERROR
    finally:
        engine.dispose()


if __name__ == "__main__":
    sys.exit(main())
