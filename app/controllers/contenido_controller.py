from app.services.contenido_service import ContenidoService

from app.utils.roles import usuario_actual

from app.utils.response import error


service = ContenidoService()


class ContenidoController:

    """CRUD del contenido del museo + social
    (evidencias, comentarios, reacciones, favoritos)."""

    # --------------------------------------------------------
    # LECTURA
    # --------------------------------------------------------

    def listar(self, args):

        """
        GET /api/museo/contenido
        Filtros: q, categoria, tipo, anio, page, per_page
        """

        return service.listar(
            q=args.get("q") or None,
            categoria=args.get("categoria") or None,
            tipo=args.get("tipo") or None,
            anio=self._entero(args.get("anio")),
            page=self._entero(args.get("page")) or 1,
            per_page=(
                self._entero(args.get("per_page")) or 12
            ),
        )

    def detalle(self, contenido_id):

        """
        GET /api/museo/contenido/<id>
        """

        return service.detalle(
            contenido_id,
            usuario_actual()
        )

    def mis_aportes(self):

        """
        GET /api/museo/contenido/mis-aportes
        (@jwt_required)
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.mis_aportes(usuario)

    def favoritos(self):

        """
        GET /api/museo/contenido/favoritos
        (@jwt_required)
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.favoritos(usuario)

    # --------------------------------------------------------
    # ESCRITURA
    # --------------------------------------------------------

    def crear(self, payload):

        """
        POST /api/museo/contenido  (@jwt_required)
        Todo contenido nace en estado pendiente.
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.crear(payload, usuario)

    def actualizar(self, contenido_id, payload):

        """
        PUT /api/museo/contenido/<id>  (@jwt_required)
        Autor del contenido o administrador.
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.actualizar(
            contenido_id,
            payload,
            usuario
        )

    def eliminar(self, contenido_id):

        """
        DELETE /api/museo/contenido/<id>
        (@jwt_required, solo admin)
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.eliminar(contenido_id, usuario)

    def agregar_evidencia(self, contenido_id, payload):

        """
        POST /api/museo/contenido/<id>/evidencias
        (@jwt_required)
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.agregar_evidencia(
            contenido_id,
            payload,
            usuario
        )

    # --------------------------------------------------------
    # SOCIAL
    # --------------------------------------------------------

    def listar_comentarios(self, contenido_id):

        """
        GET /api/museo/contenido/<id>/comentarios
        """

        return service.listar_comentarios(contenido_id)

    def comentar(self, contenido_id, payload):

        """
        POST /api/museo/contenido/<id>/comentarios
        (@jwt_required)
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.comentar(
            contenido_id,
            payload,
            usuario
        )

    def reaccionar(self, contenido_id, payload):

        """
        POST /api/museo/contenido/<id>/reaccion
        (@jwt_required) — alterna reaccionar/quitar.
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.toggle_reaccion(
            contenido_id,
            payload,
            usuario
        )

    def favorito(self, contenido_id):

        """
        POST /api/museo/contenido/<id>/favorito
        (@jwt_required) — alterna guardar/quitar.
        """

        usuario = usuario_actual()

        if not usuario:

            return error(
                "No autenticado",
                401
            )

        return service.toggle_favorito(
            contenido_id,
            usuario
        )

    # --------------------------------------------------------
    # INTERNOS
    # --------------------------------------------------------

    @staticmethod
    def _entero(valor):

        try:

            return int(valor) if valor else None

        except (TypeError, ValueError):

            return None
