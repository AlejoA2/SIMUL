from flask import (
    Blueprint,
    request
)

from flask_jwt_extended import (
    jwt_required
)

from app.controllers.validacion_controller import (
    ValidacionController
)


# ============================================================
# BLUEPRINT — bandeja de validación (RF-VAL)
# ============================================================

validacion_bp = Blueprint(
    "validacion",
    __name__
)


controller = ValidacionController()


# ============================================================
# BANDEJA
# ============================================================

@validacion_bp.get("/bandeja")
@jwt_required()
def bandeja():

    """
    GET /api/museo/validacion/bandeja  (solo admin)
    """

    return controller.bandeja()


# ============================================================
# DECISIONES
# ============================================================

@validacion_bp.post("/<int:contenido_id>/aprobar")
@jwt_required()
def aprobar(contenido_id):

    """
    POST /api/museo/validacion/<id>/aprobar  (solo admin)
    """

    payload = request.get_json(
        silent=True
    ) or {}

    return controller.aprobar(
        contenido_id,
        payload
    )


@validacion_bp.post("/<int:contenido_id>/rechazar")
@jwt_required()
def rechazar(contenido_id):

    """
    POST /api/museo/validacion/<id>/rechazar  (solo admin)
    """

    payload = request.get_json(
        silent=True
    ) or {}

    return controller.rechazar(
        contenido_id,
        payload
    )


# ============================================================
# HISTÓRICO DE DECISIONES (RF-SEG-04)
# ============================================================

@validacion_bp.get("/<int:contenido_id>/historial")
@jwt_required()
def historial(contenido_id):

    """
    GET /api/museo/validacion/<id>/historial
    """

    return controller.historial(contenido_id)
