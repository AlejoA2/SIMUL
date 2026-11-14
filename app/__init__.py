"""
Fábrica de la aplicación FastAPI.

Arquitectura modular por capas (la misma que exige el
template del profesor):

    routes → controllers → services → repositories → models

- /docs  → Swagger/OpenAPI (documentación automática)
- /redoc → documentación ReDoc
- Sesión SQLAlchemy por petición (middleware)
- Errores con el sobre {success, message, data|details}
- Vistas HTML (Jinja2) y /static para las 21 páginas
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import (
    HTTPException as StarletteHTTPException
)

from app.config import Config
from app.extensions import (
    Base,
    cerrar_sesion,
    engine,
    instalar_sesion
)

logger = logging.getLogger("simul")


def create_app(test_config=None):

    # --------------------------------------------------------
    # APP + documentación OpenAPI
    # --------------------------------------------------------

    app = FastAPI(
        title="Museo Digital Interactivo — API SIMUL",
        description=(
            "Backend del Museo Digital Interactivo "
            "(ProyectoSIMUL).\n\n"
            "**Módulos:** autenticación JWT, contenido con "
            "subtipos, bandeja de validación, gamificación "
            "(puntos/niveles/insignias), administración y "
            "vistas transversales del museo.\n\n"
            "Conéctate con *Authorize* usando el access "
            "token de `/api/museo/auth/login`."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    if test_config is not None:

        for clave, valor in test_config.items():

            setattr(Config, clave, valor)

    # --------------------------------------------------------
    # Sesión por petición: una conexión SQLAlchemy viva
    # mientras se atiende la petición (los repositorios
    # usan db.session). Se confirma si la respuesta fue
    # exitosa y se revierte si fue un error.
    # --------------------------------------------------------

    @app.middleware("http")
    async def sesion_por_peticion(
        request: Request,
        call_next
    ):

        # Los estáticos no necesitan base de datos.
        if request.url.path.startswith("/static"):

            return await call_next(request)

        sesion, token = instalar_sesion()

        try:

            respuesta = await call_next(request)

            if respuesta.status_code < 400:

                sesion.commit()

            else:

                sesion.rollback()

            return respuesta

        except Exception:

            sesion.rollback()

            raise

        finally:

            cerrar_sesion(sesion, token)

    # --------------------------------------------------------
    # Manejo de errores con el sobre estándar de la API
    # --------------------------------------------------------

    @app.exception_handler(StarletteHTTPException)
    async def http_exception(
        request: Request,
        exc: StarletteHTTPException
    ):

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail)
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validacion_exception(
        request: Request,
        exc: RequestValidationError
    ):

        # Mismo formato que genera el validador de
        # campos de las capas de servicio: details[field].
        detalles = {}

        for err in exc.errors():

            campo = ".".join(
                str(parte)
                for parte in err["loc"]
                if parte != "body"
            ) or "body"

            detalles.setdefault(campo, []).append(
                err["msg"]
            )

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Datos inválidos",
                "details": detalles
            }
        )

    @app.exception_handler(Exception)
    async def excepcion_interna(
        request: Request,
        exc: Exception
    ):

        logger.exception(
            "Error no controlado en %s %s",
            request.method,
            request.url.path
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Error interno del servidor"
            }
        )

    # --------------------------------------------------------
    # Estáticos (CSS, JS, imágenes)
    # --------------------------------------------------------

    app.mount(
        "/static",
        StaticFiles(directory="app/static"),
        name="static"
    )

    # --------------------------------------------------------
    # Routers
    # --------------------------------------------------------

    from app.routes.simul_auth_routes import simul_auth_router
    from app.routes.contenido_routes import contenido_router
    from app.routes.validacion_routes import validacion_router
    from app.routes.gamificacion_routes import (
        gamificacion_router
    )
    from app.routes.admin_routes import admin_router
    from app.routes.museo_routes import museo_router
    from app.routes.web_routes import web_router

    from app.utils.templados import registrar_rutas_web

    registrar_rutas_web(web_router)

    # Páginas HTML (sin documentación OpenAPI).
    app.include_router(web_router)

    # API REST del museo (/api/museo/*).
    app.include_router(
        simul_auth_router,
        prefix="/api/museo/auth"
    )

    app.include_router(
        contenido_router,
        prefix="/api/museo/contenido"
    )

    app.include_router(
        validacion_router,
        prefix="/api/museo/validacion"
    )

    app.include_router(
        gamificacion_router,
        prefix="/api/museo/gamificacion"
    )

    app.include_router(
        admin_router,
        prefix="/api/museo/admin"
    )

    app.include_router(
        museo_router,
        prefix="/api/museo"
    )

    # --------------------------------------------------------
    # Tablas: el DDL (db/DDL.sql) es la fuente de verdad;
    # create_all cubre un arranque desde cero (las vistas
    # no las crea: van en el DDL).
    # --------------------------------------------------------

    # from ... import: un "import app.models" a secas
    # rebindaría el nombre local `app` (la FastAPI) con el
    # paquete y create_app devolvería el módulo.
    from app import models as _modelos  # noqa: F401

    Base.metadata.create_all(engine)

    return app
