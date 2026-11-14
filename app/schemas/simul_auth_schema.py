from marshmallow import (
    Schema,
    fields,
    validate
)


class SimulRegisterSchema(Schema):

    nombre = fields.Str(
        required=True,
        validate=validate.Length(
            min=3,
            max=120
        )
    )

    correo = fields.Email(
        required=True
    )

    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(
            min=8
        )
    )

    # Opcionales: la rewiring del frontend puede enviarlos.
    # El rol solo admite cuentas de usuario (nunca admin
    # por autoregistro).
    programa_cohorte = fields.Str(
        allow_none=True
    )

    rol = fields.Str(
        validate=validate.OneOf(
            ["estudiante", "docente"]
        )
    )


class SimulLoginSchema(Schema):

    correo = fields.Email(
        required=True
    )

    password = fields.Str(
        required=True,
        load_only=True
    )


class UsuarioSchema(Schema):

    """Serialización de usuario SIN password_hash."""

    id_usuario = fields.Int()

    nombre = fields.Str()

    correo = fields.Email()

    foto = fields.Str(allow_none=True)

    biografia = fields.Str(allow_none=True)

    programa_cohorte = fields.Str(allow_none=True)

    estado = fields.Bool()

    puntos_total = fields.Int()

    fecha_registro = fields.DateTime()

    rol = fields.Method("get_rol")

    nivel = fields.Method("get_nivel")

    def get_rol(self, obj):

        return obj.rol.nombre if obj.rol else None

    def get_nivel(self, obj):

        if not obj.nivel:

            return None

        return {
            "numero": obj.nivel.numero,
            "nombre": obj.nivel.nombre,
            "puntos_min": obj.nivel.puntos_min,
            "puntos_max": obj.nivel.puntos_max,
        }


class UsuarioUpdateSchema(Schema):

    """Cambio de estado / rol desde la gestión de usuarios."""

    estado = fields.Bool()

    id_rol = fields.Int()

    nombre = fields.Str(
        validate=validate.Length(
            min=3,
            max=120
        )
    )
