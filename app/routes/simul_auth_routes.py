from fastapi import APIRouter, Depends

from app.controllers.simul_auth_controller import (
    SimulAuthController
)
from app.schemas.simul_auth_schema import (
    SimulLoginIn,
    SimulRegisterIn
)
from app.utils.roles import requiere_usuario


# ============================================================
# APIRouter — autenticación del museo
# ============================================================

simul_auth_router = APIRouter(
    tags=["Autenticación"]
)


controller = SimulAuthController()


# ============================================================
# REGISTRO
# ============================================================

@simul_auth_router.post(
    "/register",
    summary="Registrar cuenta (estudiante o docente)",
    description=(
        "Crea una cuenta con nivel 1 y 0 puntos. "
        "El rol solo admite estudiante|docente: el "
        "autoregistro como admin se rechaza (422)."
    )
)
def register(payload: SimulRegisterIn):

    """
    POST /api/museo/auth/register
    """

    return controller.register(payload.model_dump())


# ============================================================
# LOGIN
# ============================================================

@simul_auth_router.post(
    "/login",
    summary="Iniciar sesión (devuelve access token JWT)"
)
def login(payload: SimulLoginIn):

    """
    POST /api/museo/auth/login
    """

    return controller.login(payload.model_dump())


# ============================================================
# SESIÓN ACTUAL
# ============================================================

@simul_auth_router.get(
    "/me",
    summary="Usuario del token vigente",
    dependencies=[Depends(requiere_usuario)]
)
def me():

    """
    GET /api/museo/auth/me
    """

    return controller.me()
