from flask_jwt_extended import (
    create_access_token
)

from marshmallow import ValidationError

from app.extensions import db

from app.models.user import User

from app.schemas.auth_schema import (
    RegisterSchema,
    LoginSchema,
    UserSchema
)

from app.utils.response import (
    success,
    error
)


# Creamos una instancia de cada schema.
register_schema = RegisterSchema()

login_schema = LoginSchema()

user_schema = UserSchema()


class AuthController:

    def register(self, payload):

        """
        Registra un nuevo usuario.
        """

        # ----------------------------------------------------
        # VALIDACIÓN
        # ----------------------------------------------------

        try:

            data = register_schema.load(
                payload
            )

        except ValidationError as exc:

            return error(
                "Datos inválidos",
                422,
                exc.messages
            )


        # ----------------------------------------------------
        # COMPROBAR DUPLICADOS
        # ----------------------------------------------------

        existing_user = User.query.filter_by(
            email=data["email"]
        ).first()


        if existing_user:

            return error(
                "El correo ya está registrado",
                409
            )


        # ----------------------------------------------------
        # CREAR USUARIO
        # ----------------------------------------------------

        user = User(
            name=data["name"],
            email=data["email"]
        )


        # Nunca almacenamos la contraseña
        # directamente.

        user.set_password(
            data["password"]
        )


        db.session.add(user)

        db.session.commit()


        # ----------------------------------------------------
        # RESPUESTA
        # ----------------------------------------------------

        return success(
            user_schema.dump(user),
            "Usuario creado",
            201
        )


    def login(self, payload):

        """
        Autentica un usuario y genera un JWT.
        """

        # ----------------------------------------------------
        # VALIDAR DATOS
        # ----------------------------------------------------

        try:

            data = login_schema.load(
                payload
            )

        except ValidationError as exc:

            return error(
                "Datos inválidos",
                422,
                exc.messages
            )


        # ----------------------------------------------------
        # BUSCAR USUARIO
        # ----------------------------------------------------

        user = User.query.filter_by(
            email=data["email"]
        ).first()


        if not user:

            return error(
                "Credenciales inválidas",
                401
            )


        # ----------------------------------------------------
        # VALIDAR CONTRASEÑA
        # ----------------------------------------------------

        if not user.check_password(
            data["password"]
        ):

            return error(
                "Credenciales inválidas",
                401
            )


        # ----------------------------------------------------
        # CREAR JWT
        # ----------------------------------------------------

        token = create_access_token(
            identity=str(user.id)
        )


        # ----------------------------------------------------
        # RESPUESTA
        # ----------------------------------------------------

        return success(

            {
                "access_token": token,
                "user": user_schema.dump(user)
            },

            "Autenticación exitosa"
        )