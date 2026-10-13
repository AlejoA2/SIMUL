from flask_jwt_extended import (
    get_jwt_identity
)

from marshmallow import ValidationError

from app.schemas.product_schema import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductResponseSchema
)

from app.services.product_service import (
    ProductService
)

from app.utils.response import (
    success,
    error
)


# Schemas reutilizables.
create_schema = ProductCreateSchema()

update_schema = ProductUpdateSchema()

response_schema = ProductResponseSchema(
    many=True
)

single_schema = ProductResponseSchema()


class ProductController:

    """
    Controller responsable de productos.
    """

    def __init__(self):

        # Delegamos la lógica al Service.
        self.service = ProductService()


    def get_all(self):

        """
        GET /api/products/

        Devuelve todos los productos.
        """

        products = self.service.get_products()


        return success(
            response_schema.dump(
                products
            )
        )


    def get_by_id(
        self,
        product_id
    ):

        """
        GET /api/products/<id>
        """

        product = self.service.get_product(
            product_id
        )


        if not product:

            return error(
                "Producto no encontrado",
                404
            )


        return success(
            single_schema.dump(
                product
            )
        )


    def create(
        self,
        payload
    ):

        """
        POST /api/products/

        Recibe JSON desde Axios.
        """

        # ----------------------------------------------------
        # VALIDAR JSON
        # ----------------------------------------------------

        try:

            data = create_schema.load(
                payload
            )

        except ValidationError as exc:

            return error(
                "Datos inválidos",
                422,
                exc.messages
            )


        # ----------------------------------------------------
        # OBTENER USUARIO DEL JWT
        # ----------------------------------------------------

        owner_id = int(
            get_jwt_identity()
        )


        # ----------------------------------------------------
        # CREAR PRODUCTO
        # ----------------------------------------------------

        product = self.service.create_product(
            data,
            owner_id
        )


        # ----------------------------------------------------
        # RESPONDER
        # ----------------------------------------------------

        return success(
            single_schema.dump(
                product
            ),
            "Producto creado",
            201
        )


    def update(
        self,
        product_id,
        payload
    ):

        """
        PUT /api/products/<id>
        """

        # ----------------------------------------------------
        # BUSCAR PRODUCTO
        # ----------------------------------------------------

        product = self.service.get_product(
            product_id
        )


        if not product:

            return error(
                "Producto no encontrado",
                404
            )


        # ----------------------------------------------------
        # VALIDAR DATOS
        # ----------------------------------------------------

        try:

            data = update_schema.load(
                payload
            )

        except ValidationError as exc:

            return error(
                "Datos inválidos",
                422,
                exc.messages
            )


        if not data:

            return error(
                "No hay datos para actualizar",
                400
            )


        # ----------------------------------------------------
        # ACTUALIZAR
        # ----------------------------------------------------

        product = self.service.update_product(
            product,
            data
        )


        return success(
            single_schema.dump(
                product
            ),
            "Producto actualizado"
        )


    def delete(
        self,
        product_id
    ):

        """
        DELETE /api/products/<id>
        """

        product = self.service.get_product(
            product_id
        )


        if not product:

            return error(
                "Producto no encontrado",
                404
            )


        # ----------------------------------------------------
        # ELIMINAR
        # ----------------------------------------------------

        self.service.delete_product(
            product
        )


        return success(
            None,
            "Producto eliminado"
        )