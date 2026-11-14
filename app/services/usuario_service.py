from app.extensions import db
from app.models.usuario import Usuario
from app.models.rol import Rol

from app.repositories.usuario_repository import (
    UsuarioRepository
)

from app.repositories.gamificacion_repository import (
    GamificacionRepository
)

from app.schemas.simul_auth_schema import (
    UsuarioSchema
)

from app.utils.response import (
    success,
    error
)

from app.utils.roles import crear_token


usuario_schema = UsuarioSchema()


class UsuarioService:

    def __init__(self):

        self.repository = UsuarioRepository()

        self.gamificacion = GamificacionRepository()

    # --------------------------------------------------------
    # AUTENTICACIÓN (contra la tabla usuario del museo)
    # --------------------------------------------------------

    def register(self, data):

        """
        Crea una cuenta de estudiante con nivel 1.
        """

        # Los campos ya pasaron la validación del esquema
        # pydantic declarado en la ruta (422 documentado en
        # Swagger/OpenAPI).
        datos = data

        if self.repository.get_by_correo(
            datos["correo"]
        ):

            return error(
                "El correo ya está registrado",
                409
            )

        nombre_rol = datos.get("rol") or "estudiante"

        rol_cuenta = db.session.query(Rol).filter_by(
            nombre=nombre_rol
        ).first()

        if not rol_cuenta:

            return error(
                "Catálogo de roles no sembrado",
                500
            )

        usuario = Usuario(
            nombre=datos["nombre"],
            correo=datos["correo"],
            id_rol=rol_cuenta.id_rol,
            id_nivel=1,
            programa_cohorte=(
                datos.get("programa_cohorte") or None
            ),
            estado=True
        )

        usuario.set_password(
            datos["password"]
        )

        self.repository.create(usuario)

        return success(
            usuario_schema.dump(usuario),
            "Usuario creado",
            201
        )

    def login(self, data):

        """
        Autentica contra usuario + JWT (mismo patrón que
        AuthController del profesor, pero sobre la tabla
        usuario con roles del museo).
        """

        # Credenciales ya validadas por el esquema de la
        # ruta; aquí solo se autentica contra la BD.
        datos = data

        usuario = self.repository.get_by_correo(
            datos["correo"]
        )

        if not usuario:

            return error(
                "Credenciales inválidas",
                401
            )

        if not usuario.check_password(
            datos["password"]
        ):

            return error(
                "Credenciales inválidas",
                401
            )

        if not usuario.estado:

            return error(
                "La cuenta está desactivada",
                403
            )

        token = crear_token(usuario.id_usuario)

        return success(
            {
                "access_token": token,
                "user": usuario_schema.dump(usuario),
            },
            "Autenticación exitosa"
        )

    # --------------------------------------------------------
    # PERFIL
    # --------------------------------------------------------

    def me(self, usuario):

        return success(
            usuario_schema.dump(usuario)
        )

    def get_usuario(self, usuario_id):

        usuario = self.repository.get_by_id(
            usuario_id
        )

        if not usuario:

            return error(
                "Usuario no encontrado",
                404
            )

        return success(
            usuario_schema.dump(usuario)
        )

    # --------------------------------------------------------
    # GESTIÓN DE USUARIOS (RF-USR-05)
    # --------------------------------------------------------

    def listar(self, q=None, rol=None, estado=None):

        usuarios = self.repository.get_all(
            q=q,
            rol=rol,
            estado=estado
        )

        return success(
            usuario_schema.dump(usuarios, many=True)
        )

    def actualizar(self, usuario_id, data):

        usuario = self.repository.get_by_id(
            usuario_id
        )

        if not usuario:

            return error(
                "Usuario no encontrado",
                404
            )

        if "estado" in data:

            usuario.estado = bool(data["estado"])

        if "id_rol" in data:

            nuevo_rol = db.session.get(
                Rol,
                data["id_rol"]
            )

            if not nuevo_rol:

                return error(
                    "Rol no encontrado",
                    404
                )

            usuario.id_rol = nuevo_rol.id_rol

        if "nombre" in data and data["nombre"]:

            usuario.nombre = data["nombre"]

        self.repository.update(usuario)

        return success(
            usuario_schema.dump(usuario),
            "Usuario actualizado"
        )
