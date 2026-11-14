from fastapi import APIRouter, Depends, Query

from app.controllers.gamificacion_controller import (
    GamificacionController
)
from app.utils.roles import requiere_usuario


# ============================================================
# APIRouter — gamificación (RF-GAM)
# ============================================================

gamificacion_router = APIRouter(
    tags=["Gamificación"]
)


controller = GamificacionController()


# ============================================================
# RANKING / CATÁLOGOS
# ============================================================

@gamificacion_router.get(
    "/ranking",
    summary="Ranking de puntos por nivel"
)
def ranking(
    limite: int | None = Query(
        None,
        ge=1,
        le=500,
        description="Máximo de usuarios (por defecto 100)"
    )
):

    """
    GET /api/museo/gamificacion/ranking
    """

    return controller.ranking({"limite": limite})


@gamificacion_router.get(
    "/niveles",
    summary="Catálogo de niveles"
)
def niveles():

    """
    GET /api/museo/gamificacion/niveles
    """

    return controller.niveles()


@gamificacion_router.get(
    "/insignias",
    summary="Catálogo de insignias",
    description="Con sesión, marca las que ya posee el usuario."
)
def insignias():

    """
    GET /api/museo/gamificacion/insignias
    """

    return controller.insignias()


# ============================================================
# HISTORIAL DE PUNTOS
# ============================================================

@gamificacion_router.get(
    "/mi-historial",
    summary="Historial de puntos del usuario",
    dependencies=[Depends(requiere_usuario)]
)
def mi_historial():

    """
    GET /api/museo/gamificacion/mi-historial
    """

    return controller.mi_historial()


@gamificacion_router.get(
    "/historial/{usuario_id}",
    summary="Historial de puntos de un usuario",
    description=(
        "Solo el propio usuario o un administrador "
        "(401 sin sesión, 403 si consulta a otro)."
    ),
    dependencies=[Depends(requiere_usuario)]
)
def historial(usuario_id: int):

    """
    GET /api/museo/gamificacion/historial/<id>
    """

    return controller.historial(usuario_id)
