"""Aplicación FastAPI de Trail Peñasagra."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.formparsers import MultiPartException

from app.api import (
    admin_carreras,
    admin_clasificaciones,
    admin_evento,
    admin_inscripciones,
    archivos,
    clasificaciones,
    contenido,
    media,
    salud,
    sesion,
)
from app.core.config import Settings, get_settings
from app.core.db import crear_engine
from app.services.contenido import cargar_contenido
from app.services.errores import Conflicto, NoEncontrado
from app.storage import AlmacenamientoNoDisponible, crear_almacenamiento

# Nombres legibles de los campos de los formularios del panel (mensajes de validación).
ETIQUETAS = {
    "title": "nombre",
    "label": "frase corta",
    "color": "color",
    "edition": "edición",
    "km": "distancia",
    "elevation": "desnivel",
    "price": "precio",
    "start": "hora de salida",
    "terrain": "terreno",
    "description": "descripción",
    "aid": "avituallamientos",
    "image": "fotografía",
    "route": "enlace a la ruta",
    "wikiloc": "ID de Wikiloc",
    "gpx": "track GPX",
    "registration": "enlace de inscripción",
    "date": "fecha y hora",
    "version": "versión",
    "registrationsOpen": "inscripciones abiertas",
    "registrationMessage": "mensaje al participante",
    "solidarityRegistration": "enlace de pago del dorsal solidario",
    "csv": "CSV",
    "mapping": "asignación de columnas",
    "sourceFile": "archivo CSV",
    "raceId": "carrera",
    "year": "edición",
}


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # La semilla se valida al arrancar: si no es válida, el servicio no arranca.
        app.state.contenido = cargar_contenido()
        yield
        app.state.engine.dispose()

    docs = settings.es_desarrollo
    app = FastAPI(
        title="Trail Peñasagra API",
        version="0.1.0",
        docs_url="/api/docs" if docs else None,
        openapi_url="/api/openapi.json" if docs else None,
        redoc_url=None,
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.engine = crear_engine(settings.database_url, settings.db_connect_timeout)
    app.state.almacenamiento = crear_almacenamiento(settings)

    @app.middleware("http")
    async def cabeceras_seguras(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers.setdefault("Cache-Control", "no-store")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        return response

    @app.exception_handler(StarletteHTTPException)
    async def error_http(_: Request, exc: HTTPException) -> JSONResponse:
        # Formato de error que ya consume el frontend: {"error": "..."}
        detalle = exc.detail if isinstance(exc.detail, str) else "Error"
        return JSONResponse({"error": detalle}, status_code=exc.status_code, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def error_validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
        # Mensaje claro con el campo afectado, sin detalles internos del esquema (002 FR-021).
        for error in exc.errors():
            campo = str(error.get("loc", ("",))[-1])
            if campo in ETIQUETAS:
                return JSONResponse(
                    {"error": f"Revisa el campo «{ETIQUETAS[campo]}»."}, status_code=400
                )
        return JSONResponse({"error": "Datos no válidos."}, status_code=400)

    @app.exception_handler(Conflicto)
    async def conflicto(_: Request, exc: Conflicto) -> JSONResponse:
        return JSONResponse({"error": exc.mensaje}, status_code=409)

    @app.exception_handler(NoEncontrado)
    async def no_encontrado(_: Request, exc: NoEncontrado) -> JSONResponse:
        return JSONResponse({"error": exc.mensaje}, status_code=404)

    @app.exception_handler(OperationalError)
    async def base_no_disponible(_: Request, __: OperationalError) -> JSONResponse:
        return JSONResponse(
            {"error": "El servicio no está disponible. Inténtalo más tarde."}, status_code=503
        )

    @app.exception_handler(AlmacenamientoNoDisponible)
    async def almacenamiento_no_disponible(
        _: Request, __: AlmacenamientoNoDisponible
    ) -> JSONResponse:
        return JSONResponse(
            {"error": "No se ha podido guardar el archivo. Inténtalo más tarde."}, status_code=503
        )

    @app.exception_handler(MultiPartException)
    async def multipart_no_valido(_: Request, __: MultiPartException) -> JSONResponse:
        return JSONResponse({"error": "Selecciona un archivo."}, status_code=400)

    app.include_router(salud.router)
    app.include_router(contenido.router)
    app.include_router(sesion.router)
    app.include_router(archivos.router)
    app.include_router(media.router)
    app.include_router(admin_evento.router)
    app.include_router(admin_carreras.router)
    app.include_router(admin_inscripciones.router)
    app.include_router(admin_clasificaciones.router)
    app.include_router(clasificaciones.router)
    return app


app = create_app()
