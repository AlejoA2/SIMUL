from flask import (
    Blueprint,
    request
)

from flask_jwt_extended import (
    jwt_required
)

from app.controllers.gamificacion_controller import (
    GamificacionController
)


# ============================================================
# BLUEPRINT — gamificación (RF-GAM)
# ============================================================

gamificacion_bp = Blueprint(
    "gamificacion",
    __name__
)


controller = GamificacionController()


# ============================================================
# RANKING / CATÁLOGOS
# ============================================================

@gamificacion_bp.get("/ranking")
def ranking():

    """
    GET /api/museo/gamificacion/ranking
    """

    return controller.ranking(request.args)


@gamificacion_bp.get("/niveles")
def niveles():

    """
    GET /api/museo/gamificacion/niveles
    """

    return controller.niveles()


@gamificacion_bp.get("/insignias")
def insignias():

    """
    GET /api/museo/gamificacion/insignias
    """

    return controller.insignias()


# ============================================================
# HISTORIAL DE PUNTOS
# ============================================================

@gamificacion_bp.get("/mi-historial")
@jwt_required()
def mi_historial():

    """
    GET /api/museo/gamificacion/mi-historial
    """

    return controller.mi_historial()


@gamificacion_bp.get("/historial/<int:usuario_id>")
def historial(usuario_id):

    """
    GET /api/museo/gamificacion/historial/<id>
    """

    return controller.historial(usuario_id)
