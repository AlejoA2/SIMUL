from marshmallow import (
    Schema,
    fields,
    validate
)


class ProductCreateSchema(Schema):

    name = fields.Str(
        required=True,
        validate=validate.Length(
            min=2,
            max=150
        )
    )

    description = fields.Str(
        allow_none=True,
        load_default=""
    )

    price = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(
            min=0
        )
    )

    stock = fields.Int(
        required=True,
        validate=validate.Range(
            min=0
        )
    )


class ProductUpdateSchema(Schema):

    name = fields.Str(
        validate=validate.Length(
            min=2,
            max=150
        )
    )

    description = fields.Str(
        allow_none=True
    )

    price = fields.Decimal(
        as_string=True,
        validate=validate.Range(
            min=0
        )
    )

    stock = fields.Int(
        validate=validate.Range(
            min=0
        )
    )


class ProductResponseSchema(Schema):

    id = fields.Int()

    name = fields.Str()

    description = fields.Str(
        allow_none=True
    )

    price = fields.Decimal(
        as_string=True
    )

    stock = fields.Int()

    owner_id = fields.Int()

    created_at = fields.DateTime()

    updated_at = fields.DateTime()