from app.services.validacion_service import ValidacionService

from app.utils.roles import usuario_actual

from app.utils.response import error


service = ValidacionService()


class ValidacionController:

    """Bandeja de validación y decisiones del admin
    (RF-VAL-01/02/03)."""

    def bandeja(self):

        """
        GET /api/museo/validacion/bandeja
        (@jwt_required, solo admin)
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        if usuario.rol_nombre != "admin":

            return error(
                "Se requiere rol administrador",
                403
            )

        return service.bandeja()

    def aprobar(self, contenido_id, payload):

        """
        POST /api/museo/validacion/<id>/aprobar
        (@jwt_required, solo admin)
        """

        return self._decidir(
            contenido_id,
            payload,
            "aprobar"
        )

    def rechazar(self, contenido_id, payload):

        """
        POST /api/museo/validacion/<id>/rechazar
        (@jwt_required, solo admin)
        """

        return self._decidir(
            contenido_id,
            payload,
            "rechazar"
        )

    def historial(self, contenido_id):

        """
        GET /api/museo/validacion/<id>/historial
        """

        return service.historial(contenido_id)

    # --------------------------------------------------------
    # INTERNOS
    # --------------------------------------------------------

    def _decidir(self, contenido_id, payload, accion):

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        if accion == "aprobar":

            return service.aprobar(
                contenido_id,
                usuario,
                payload
            )

        return service.rechazar(
            contenido_id,
            usuario,
            payload
        )
