from app.services.usuario_service import UsuarioService

from app.utils.roles import usuario_actual

from app.utils.response import error


service = UsuarioService()


class SimulAuthController:

    """
    Autenticación del museo contra la tabla usuario
    (rol, nivel, puntos). La API del profesor en
    /api/auth sigue intacta.
    """

    def register(self, payload):

        """
        POST /api/museo/auth/register
        """

        return service.register(payload)

    def login(self, payload):

        """
        POST /api/museo/auth/login
        """

        return service.login(payload)

    def me(self):

        """
        GET /api/museo/auth/me  (@jwt_required)
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.me(usuario)
