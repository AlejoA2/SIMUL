from fastapi import APIRouter, Body, Depends

from app.controllers.validacion_controller import (
    ValidacionController
)
from app.schemas.contenido_schema import DecisionIn
from app.utils.roles import requiere_usuario


# ============================================================
# APIRouter — bandeja de validación (RF-VAL)
# ============================================================

validacion_router = APIRouter(
    tags=["Validación"],
    dependencies=[Depends(requiere_usuario)]
)


controller = ValidacionController()


# ============================================================
# BANDEJA
# ============================================================

@validacion_router.get(
    "/bandeja",
    summary="Bandeja de pendientes (admin/docente)"
)
def bandeja():

    """
    GET /api/museo/validacion/bandeja
    """

    return controller.bandeja()


# ============================================================
# DECISIONES
# ============================================================

@validacion_router.post(
    "/{contenido_id}/aprobar",
    summary="Aprobar contenido (+100 puntos al autor)",
    description=(
        "Transacción única: estado publicado, bitácora, "
        "notificación, puntos, nivel e insignias."
    )
)
def aprobar(
    contenido_id: int,
    payload: DecisionIn | None = Body(default=None)
):

    """
    POST /api/museo/validacion/<id>/aprobar
    """

    return controller.aprobar(
        contenido_id,
        payload.model_dump(exclude_unset=True)
        if payload else {}
    )


@validacion_router.post(
    "/{contenido_id}/rechazar",
    summary="Rechazar contenido (con observaciones)"
)
def rechazar(
    contenido_id: int,
    payload: DecisionIn | None = Body(default=None)
):

    """
    POST /api/museo/validacion/<id>/rechazar
    """

    return controller.rechazar(
        contenido_id,
        payload.model_dump(exclude_unset=True)
        if payload else {}
    )


# ============================================================
# HISTÓRICO DE DECISIONES (RF-SEG-04)
# ============================================================

@validacion_router.get(
    "/{contenido_id}/historial",
    summary="Histórico de validación de un contenido"
)
def historial(contenido_id: int):

    """
    GET /api/museo/validacion/<id>/historial
    """

    return controller.historial(contenido_id)
