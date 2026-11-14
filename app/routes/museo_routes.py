from flask import (
    Blueprint,
    request
)

from flask_jwt_extended import (
    jwt_required
)

from app.controllers.museo_controller import (
    MuseoController
)


# ============================================================
# BLUEPRINT — vistas transversales del museo
# ============================================================

museo_bp = Blueprint(
    "museo",
    __name__
)


controller = MuseoController()


# ============================================================
# PORTADA / HISTORIA / HALL / CATÁLOGOS
# ============================================================

@museo_bp.get("/home")
def home():

    """
    GET /api/museo/home
    """

    return controller.home()


@museo_bp.get("/timeline")
def timeline():

    """
    GET /api/museo/timeline
    """

    return controller.timeline()


@museo_bp.get("/hall")
def hall():

    """
    GET /api/museo/hall
    """

    return controller.hall()


@museo_bp.get("/categorias")
def categorias():

    """
    GET /api/museo/categorias
    """

    return controller.categorias()


@museo_bp.get("/anios")
def anios():

    """
    GET /api/museo/anios
    """

    return controller.anios()


# ============================================================
# NOTIFICACIONES (RF-NOT-01)
# ============================================================

@museo_bp.get("/notificaciones")
@jwt_required()
def notificaciones():

    """
    GET /api/museo/notificaciones  (?no_leidas=1)
    """

    return controller.notificaciones(request.args)


@museo_bp.post("/notificaciones/<int:notif_id>/leer")
@jwt_required()
def marcar_leida(notif_id):

    """
    POST /api/museo/notificaciones/<id>/leer
    """

    return controller.marcar_leida(notif_id)
