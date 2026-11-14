from app.services.gamificacion_service import (
    GamificacionService
)

from app.utils.response import error


service = GamificacionService()


class GamificacionController:

    """Ranking, niveles, insignias e historial de
    puntos (RF-GAM-01/03)."""

    def ranking(self, args):

        """
        GET /api/museo/gamificacion/ranking
        """

        limite = args.get("limite")

        try:

            limite = int(limite) if limite else 100

        except (TypeError, ValueError):

            limite = 100

        return service.ranking(limite=limite)

    def niveles(self):

        """
        GET /api/museo/gamificacion/niveles
        """

        return service.niveles()

    def insignias(self):

        """
        GET /api/museo/gamificacion/insignias
        Con sesión marca las que ya posee el usuario.
        """

        from app.utils.roles import usuario_actual

        return service.insignias(
            usuario=usuario_actual()
        )

    def historial(self, usuario_id):

        """
        GET /api/museo/gamificacion/historial/<id>
        """

        return service.historial(usuario_id)

    def mi_historial(self):

        """
        GET /api/museo/gamificacion/mi-historial
        (@jwt_required)
        """

        from app.utils.roles import usuario_actual

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.historial(
            usuario.id_usuario
        )
