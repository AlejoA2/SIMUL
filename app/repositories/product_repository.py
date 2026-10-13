from app.extensions import db
from app.models.product import Product


class ProductRepository:

    def get_all(self):

        return Product.query.order_by(
            Product.id.desc()
        ).all()

    def get_by_id(self, product_id):

        return db.session.get(
            Product,
            product_id
        )

    def create(
        self,
        data,
        owner_id
    ):

        product = Product(
            **data,
            owner_id=owner_id
        )

        db.session.add(product)

        db.session.commit()

        return product

    def update(
        self,
        product,
        data
    ):

        for key, value in data.items():

            setattr(
                product,
                key,
                value
            )

        db.session.commit()

        return product

    def delete(self, product):

        db.session.delete(product)

        db.session.commit()