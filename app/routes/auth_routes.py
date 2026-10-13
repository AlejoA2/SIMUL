from flask import (
    Blueprint,
    request
)

from app.controllers.auth_controller import (
    AuthController
)


# ============================================================
# BLUEPRINT
# ============================================================

auth_bp = Blueprint(
    "auth",
    __name__
)


# Controller reutilizable.
controller = AuthController()


# ============================================================
# REGISTRO
# ============================================================

@auth_bp.post("/register")
def register():

    """
    POST /api/auth/register
    """

    # Obtenemos el JSON enviado por Axios.

    payload = request.get_json(
        silent=True
    ) or {}


    # Delegamos al Controller.

    return controller.register(
        payload
    )


# ============================================================
# LOGIN
# ============================================================

@auth_bp.post("/login")
def login():

    """
    POST /api/auth/login
    """

    payload = request.get_json(
        silent=True
    ) or {}


    return controller.login(
        payload
    )