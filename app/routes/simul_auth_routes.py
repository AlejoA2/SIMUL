from flask import (
    Blueprint,
    request
)

from flask_jwt_extended import (
    jwt_required
)

from app.controllers.simul_auth_controller import (
    SimulAuthController
)


# ============================================================
# BLUEPRINT — autenticación del museo
# ============================================================

simul_auth_bp = Blueprint(
    "simul_auth",
    __name__
)


controller = SimulAuthController()


# ============================================================
# REGISTRO
# ============================================================

@simul_auth_bp.post("/register")
def register():

    """
    POST /api/museo/auth/register
    """

    payload = request.get_json(
        silent=True
    ) or {}

    return controller.register(payload)


# ============================================================
# LOGIN
# ============================================================

@simul_auth_bp.post("/login")
def login():

    """
    POST /api/museo/auth/login
    """

    payload = request.get_json(
        silent=True
    ) or {}

    return controller.login(payload)


# ============================================================
# SESIÓN ACTUAL
# ============================================================

@simul_auth_bp.get("/me")
@jwt_required()
def me():

    """
    GET /api/museo/auth/me
    """

    return controller.me()
