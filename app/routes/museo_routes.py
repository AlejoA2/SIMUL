from fastapi import APIRouter, Depends, Query

from app.controllers.museo_controller import (
    MuseoController
)
from app.utils.roles import requiere_usuario


# ============================================================
# APIRouter — vistas transversales del museo
# ============================================================

museo_router = APIRouter(
    tags=["Museo"]
)


controller = MuseoController()


# ============================================================
# PORTADA / HISTORIA / HALL / CATÁLOGOS
# ============================================================

@museo_router.get(
    "/home",
    summary="Datos de la portada (KPIs)"
)
def home():

    """
    GET /api/museo/home
    """

    return controller.home()


@museo_router.get(
    "/timeline",
    summary="Línea de tiempo agrupada por década"
)
def timeline():

    """
    GET /api/museo/timeline
    """

    return controller.timeline()


@museo_router.get(
    "/hall",
    summary="Premiación / Hall de la fama"
)
def hall():

    """
    GET /api/museo/hall
    """

    return controller.hall()


@museo_router.get(
    "/categorias",
    summary="Categorías con conteo"
)
def categorias():

    """
    GET /api/museo/categorias
    """

    return controller.categorias()


@museo_router.get(
    "/anios",
    summary="Años con conteo"
)
def anios():

    """
    GET /api/museo/anios
    """

    return controller.anios()


# ============================================================
# NOTIFICACIONES (RF-NOT-01)
# ============================================================

@museo_router.get(
    "/notificaciones",
    summary="Notificaciones del usuario",
    description="Filtro: ?no_leidas=1",
    dependencies=[Depends(requiere_usuario)]
)
def notificaciones(
    no_leidas: str | None = Query(
        None,
        description="1 = solo no leídas"
    )
):

    """
    GET /api/museo/notificaciones
    """

    return controller.notificaciones({
        "no_leidas": no_leidas,
    })


@museo_router.post(
    "/notificaciones/{notif_id}/leer",
    summary="Marcar notificación como leída",
    dependencies=[Depends(requiere_usuario)]
)
def marcar_leida(notif_id: int):

    """
    POST /api/museo/notificaciones/<id>/leer
    """

    return controller.marcar_leida(notif_id)
