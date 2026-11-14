from flask import (
    Blueprint,
    request
)

from flask_jwt_extended import (
    jwt_required
)

from app.controllers.admin_controller import (
    AdminController
)


# ============================================================
# BLUEPRINT — administración (RF-USR-05 / RF-DSH-03)
# ============================================================

admin_bp = Blueprint(
    "admin",
    __name__
)


controller = AdminController()


# ============================================================
# GESTIÓN DE USUARIOS
# ============================================================

@admin_bp.get("/usuarios")
@jwt_required()
def usuarios():

    """
    GET /api/museo/admin/usuarios  (solo admin)
    Filtros: ?q= &rol= &estado=0|1
    """

    return controller.usuarios(request.args)


@admin_bp.put("/usuarios/<int:usuario_id>")
@jwt_required()
def actualizar_usuario(usuario_id):

    """
    PUT /api/museo/admin/usuarios/<id>  (solo admin)
    Cambia estado / rol / nombre.
    """

    payload = request.get_json(
        silent=True
    ) or {}

    return controller.actualizar_usuario(
        usuario_id,
        payload
    )


# ============================================================
# INDICADORES
# ============================================================

@admin_bp.get("/kpis")
@jwt_required()
def kpis():

    """
    GET /api/museo/admin/kpis  (solo admin)
    """

    return controller.kpis()
