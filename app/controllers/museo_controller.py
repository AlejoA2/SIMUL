from app.services.museo_service import MuseoService

from app.utils.roles import usuario_actual

from app.utils.response import error


service = MuseoService()


class MuseoController:

    """Vistas transversales: portada, línea del tiempo,
    hall de la fama, categorías y notificaciones."""

    def home(self):

        """
        GET /api/museo/home
        """

        return service.home()

    def timeline(self):

        """
        GET /api/museo/timeline
        """

        return service.timeline()

    def hall(self):

        """
        GET /api/museo/hall
        """

        return service.hall()

    def categorias(self):

        """
        GET /api/museo/categorias
        """

        return service.categorias()

    def anios(self):

        """
        GET /api/museo/anios
        """

        return service.anios()

    # --------------------------------------------------------
    # NOTIFICACIONES
    # --------------------------------------------------------

    def notificaciones(self, args):

        """
        GET /api/museo/notificaciones  (@jwt_required)
        Filtro: no_leidas=1
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.notificaciones(
            usuario,
            solo_no_leidas=(
                args.get("no_leidas") == "1"
            )
        )

    def marcar_leida(self, notif_id):

        """
        POST /api/museo/notificaciones/<id>/leer
        (@jwt_required)
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.marcar_leida(
            usuario,
            notif_id
        )
