"""
Autenticación y autorización (JWT + roles).

- crear_token(): emite el access token (sub = str(id),
  como pide la convención del template del profesor).
- requiere_usuario / usuario_opcional: dependencias de
  FastAPI que cargan el JWT del header Authorization
  (Bearer) y lo dejan disponible para los controllers
  mediante usuario_actual().

El botón "Authorize" de Swagger (/docs) permite probar
los endpoints protegidos pegando el token del login.
"""

from contextvars import ContextVar
from datetime import datetime, timedelta, timezone

import jwt as pyjwt
from fastapi import Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from app.config import Config
from app.models.usuario import Usuario
from app.repositories.usuario_repository import (
    UsuarioRepository
)


repository = UsuarioRepository()

_bearer = HTTPBearer(auto_error=False)

_usuario_ctx: ContextVar[Usuario | None] = ContextVar(
    "usuario_jwt",
    default=None
)


# ------------------------------------------------------------
# TOKEN
# ------------------------------------------------------------

def crear_token(usuario_id: int) -> str:

    """Firma un access token JWT válido por
    JWT_ACCESS_TOKEN_EXPIRES segundos."""

    ahora = datetime.now(timezone.utc)

    return pyjwt.encode(
        {
            "sub": str(usuario_id),
            "type": "access",
            "iat": ahora,
            "exp": ahora + timedelta(
                seconds=Config.JWT_ACCESS_TOKEN_EXPIRES
            )
        },
        Config.JWT_SECRET_KEY,
        algorithm="HS256"
    )


def _sub_del_token(token: str) -> str | None:

    """
    Devuelve el sub del token.

    Si el token es inválido o expirado lanza 401 (igual que
    verify_jwt_in_request(optional=True) del template de
    Flask: en rutas públicas un token presente pero malo
    también rechaza).
    """

    try:

        datos = pyjwt.decode(
            token,
            Config.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )

    except pyjwt.PyJWTError:

        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )

    sub = datos.get("sub")

    return str(sub) if sub is not None else None


# ------------------------------------------------------------
# CONTEXTO DE LA PETICIÓN
# ------------------------------------------------------------

def usuario_actual():

    """
    Devuelve el Usuario del JWT vigente o None.

    Lo cargó la dependencia de autenticación de la ruta
    (requiere_usuario o usuario_opcional). Un usuario
    inactivo nunca queda en contexto.
    """

    return _usuario_ctx.get()


# ------------------------------------------------------------
# DEPENDENCIAS FASTAPI
# ------------------------------------------------------------

def _dependencia_usuario(opcional: bool):

    async def dependencia(
        credenciales: HTTPAuthorizationCredentials | None = (
            Depends(_bearer)
        )
    ):

        """
        IMPORTANTE: debe ser async. Si fuera sync, FastAPI la
        ejecuta en un hilo (contextmanager_in_threadpool) y
        el ContextVar que se setea ahí NO se propaga al hilo
        donde corre el endpoint → usuario_actual() devolvería
        None. Como async corre en el contexto de la petición,
        el endpoint (aunque use threadpool) lo ve en su copia
        del contexto.
        """

        usuario = None

        if credenciales is not None:

            sub = _sub_del_token(credenciales.credentials)

            if sub is not None:

                try:

                    usuario_id = int(sub)

                except (TypeError, ValueError):

                    usuario_id = None

                if usuario_id is not None:

                    # La consulta va al threadpool: el hilo
                    # hereda la sesión del contexto de la
                    # petición (instalada por el middleware).
                    usuario = await run_in_threadpool(
                        repository.get_by_id,
                        usuario_id
                    )

                    # Inactivo = sin sesión (igual que con
                    # el template de Flask).
                    if (
                        usuario is not None
                        and not usuario.estado
                    ):

                        usuario = None

        if not opcional and usuario is None:

            raise HTTPException(
                status_code=401,
                detail="No autenticado"
            )

        token = _usuario_ctx.set(usuario)

        try:

            yield usuario

        finally:

            _usuario_ctx.reset(token)

    return dependencia


# Ruta protegida: exige un JWT válido de usuario activo.
requiere_usuario = _dependencia_usuario(opcional=False)

# Ruta pública con sesión opcional: si llega un JWT válido
# se carga el usuario; si no, continúa como anónimo.
usuario_opcional = _dependencia_usuario(opcional=True)
