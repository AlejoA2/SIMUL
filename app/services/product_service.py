from app.repositories.product_repository import (
    ProductRepository
)


class ProductService:

    def __init__(self):

        # El Service utiliza el Repository
        # para acceder a los datos.

        self.repository = ProductRepository()


    def get_products(self):

        """
        Obtiene todos los productos.
        """

        return self.repository.get_all()


    def get_product(self, product_id):

        """
        Obtiene un producto específico.
        """

        return self.repository.get_by_id(
            product_id
        )


    def create_product(
        self,
        data,
        owner_id
    ):

        """
        Crea un producto.

        Aquí podríamos agregar reglas de negocio.
        """

        return self.repository.create(
            data,
            owner_id
        )


    def update_product(
        self,
        product,
        data
    ):

        """
        Actualiza un producto.
        """

        return self.repository.update(
            product,
            data
        )


    def delete_product(
        self,
        product
    ):

        """
        Elimina un producto.
        """

        self.repository.delete(
            product
        )