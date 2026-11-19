"""Aplicación FastAPI de Trail Peñasagra."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import archivos, contenido, salud, sesion
from app.core.config import Settings, get_settings
from app.core.db import crear_engine
from app.services.contenido import cargar_contenido


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
    async def error_validacion(_: Request, __: RequestValidationError) -> JSONResponse:
        # Sin detalles internos del esquema (FR-021 de la feature 002).
        return JSONResponse({"error": "Datos no válidos."}, status_code=400)

    @app.exception_handler(OperationalError)
    async def base_no_disponible(_: Request, __: OperationalError) -> JSONResponse:
        return JSONResponse(
            {"error": "El servicio no está disponible. Inténtalo más tarde."}, status_code=503
        )

    app.include_router(salud.router)
    app.include_router(contenido.router)
    app.include_router(sesion.router)
    app.include_router(archivos.router)
    return app


app = create_app()
