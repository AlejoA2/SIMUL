from flask import (
    Blueprint,
    request
)

from flask_jwt_extended import (
    jwt_required
)

from app.controllers.contenido_controller import (
    ContenidoController
)


# ============================================================
# BLUEPRINT — contenido del museo
# ============================================================

contenido_bp = Blueprint(
    "contenido",
    __name__
)


controller = ContenidoController()


# ============================================================
# LISTAR (público, con filtros de búsqueda)
# ============================================================

@contenido_bp.get("/")
def listar():

    """
    GET /api/museo/contenido
    Filtros: ?q= &categoria= &tipo= &anio= &page=
    """

    return controller.listar(request.args)


# ============================================================
# MIS APORTES / FAVORITOS (rutas fijas antes de /<id>)
# ============================================================

@contenido_bp.get("/mis-aportes")
@jwt_required()
def mis_aportes():

    """
    GET /api/museo/contenido/mis-aportes
    """

    return controller.mis_aportes()


@contenido_bp.get("/favoritos")
@jwt_required()
def favoritos():

    """
    GET /api/museo/contenido/favoritos
    """

    return controller.favoritos()


# ============================================================
# CREAR (todo contenido nace pendiente)
# ============================================================

@contenido_bp.post("/")
@jwt_required()
def crear():

    """
    POST /api/museo/contenido
    """

    payload = request.get_json(
        silent=True
    ) or {}

    return controller.crear(payload)


# ============================================================
# DETALLE / EDITAR / ELIMINAR
# ============================================================

@contenido_bp.get("/<int:contenido_id>")
def detalle(contenido_id):

    """
    GET /api/museo/contenido/<id>
    """

    return controller.detalle(contenido_id)


@contenido_bp.put("/<int:contenido_id>")
@jwt_required()
def actualizar(contenido_id):

    """
    PUT /api/museo/contenido/<id>
    """

    payload = request.get_json(
        silent=True
    ) or {}

    return controller.actualizar(
        contenido_id,
        payload
    )


@contenido_bp.delete("/<int:contenido_id>")
@jwt_required()
def eliminar(contenido_id):

    """
    DELETE /api/museo/contenido/<id>  (solo admin)
    """

    return controller.eliminar(contenido_id)


# ============================================================
# EVIDENCIAS (RF-EVD-01)
# ============================================================

@contenido_bp.post("/<int:contenido_id>/evidencias")
@jwt_required()
def agregar_evidencia(contenido_id):

    """
    POST /api/museo/contenido/<id>/evidencias
    """

    payload = request.get_json(
        silent=True
    ) or {}

    return controller.agregar_evidencia(
        contenido_id,
        payload
    )


# ============================================================
# COMENTARIOS (RF-CMT-01)
# ============================================================

@contenido_bp.get("/<int:contenido_id>/comentarios")
def listar_comentarios(contenido_id):

    """
    GET /api/museo/contenido/<id>/comentarios
    """

    return controller.listar_comentarios(contenido_id)


@contenido_bp.post("/<int:contenido_id>/comentarios")
@jwt_required()
def comentar(contenido_id):

    """
    POST /api/museo/contenido/<id>/comentarios
    """

    payload = request.get_json(
        silent=True
    ) or {}

    return controller.comentar(
        contenido_id,
        payload
    )


# ============================================================
# REACCIONES (RF-REA-01) — alterna
# ============================================================

@contenido_bp.post("/<int:contenido_id>/reaccion")
@jwt_required()
def reaccionar(contenido_id):

    """
    POST /api/museo/contenido/<id>/reaccion
    """

    payload = request.get_json(
        silent=True
    ) or {}

    return controller.reaccionar(
        contenido_id,
        payload
    )


# ============================================================
# FAVORITOS — alterna
# ============================================================

@contenido_bp.post("/<int:contenido_id>/favorito")
@jwt_required()
def favorito(contenido_id):

    """
    POST /api/museo/contenido/<id>/favorito
    """

    return controller.favorito(contenido_id)
