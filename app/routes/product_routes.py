from flask import (
    Blueprint,
    request
)

from flask_jwt_extended import (
    jwt_required
)

from app.controllers.product_controller import (
    ProductController
)


# ============================================================
# BLUEPRINT
# ============================================================

product_bp = Blueprint(
    "products",
    __name__
)


# Controller.
controller = ProductController()


# ============================================================
# GET ALL
# ============================================================

@product_bp.get("/")
@jwt_required()
def get_products():

    """
    GET /api/products/

    Devuelve todos los productos.
    """

    return controller.get_all()


# ============================================================
# GET ONE
# ============================================================

@product_bp.get("/<int:product_id>")
@jwt_required()
def get_product(product_id):

    """
    GET /api/products/<id>
    """

    return controller.get_by_id(
        product_id
    )


# ============================================================
# CREATE
# ============================================================

@product_bp.post("/")
@jwt_required()
def create_product():

    """
    POST /api/products/
    """

    payload = request.get_json(
        silent=True
    ) or {}


    return controller.create(
        payload
    )


# ============================================================
# UPDATE
# ============================================================

@product_bp.put("/<int:product_id>")
@jwt_required()
def update_product(product_id):

    """
    PUT /api/products/<id>
    """

    payload = request.get_json(
        silent=True
    ) or {}


    return controller.update(
        product_id,
        payload
    )


# ============================================================
# DELETE
# ============================================================

@product_bp.delete("/<int:product_id>")
@jwt_required()
def delete_product(product_id):

    """
    DELETE /api/products/<id>
    """

    return controller.delete(
        product_id
    )