from sqlalchemy import func

from app.extensions import db

from app.models.contenido import Contenido
from app.models.usuario import Usuario
from app.models.notificacion import Notificacion

from app.services.usuario_service import UsuarioService

from app.utils.roles import usuario_actual

from app.utils.response import (
    success,
    error
)


service = UsuarioService()


class AdminController:

    """Gestión de usuarios (RF-USR-05) e indicadores
    del panel de administración (RF-DSH-03)."""

    # --------------------------------------------------------
    # USUARIOS
    # --------------------------------------------------------

    def usuarios(self, args):

        """
        GET /api/museo/admin/usuarios  (@jwt_required,
        solo admin). Filtros: q, rol, estado.
        """

        usuario = usuario_actual()

        respuesta = self._como_admin(usuario)

        if respuesta:

            return respuesta

        estado = args.get("estado")

        if estado in ("0", "1"):

            estado = estado == "1"

        else:

            estado = None

        return service.listar(
            q=args.get("q") or None,
            rol=args.get("rol") or None,
            estado=estado
        )

    def actualizar_usuario(self, usuario_id, payload):

        """
        PUT /api/museo/admin/usuarios/<id>
        (@jwt_required, solo admin) — estado / rol /
        nombre.
        """

        usuario = usuario_actual()

        respuesta = self._como_admin(usuario)

        if respuesta:

            return respuesta

        return service.actualizar(
            usuario_id,
            payload
        )

    # --------------------------------------------------------
    # INDICADORES
    # --------------------------------------------------------

    def kpis(self):

        """
        GET /api/museo/admin/kpis  (@jwt_required,
        solo admin) — conteos reales de la base.
        """

        usuario = usuario_actual()

        respuesta = self._como_admin(usuario)

        if respuesta:

            return respuesta

        por_tipo = dict(
            db.session.query(
                Contenido.tipo,
                func.count(Contenido.id_contenido)
            )
            .filter(Contenido.estado == "publicado")
            .group_by(Contenido.tipo)
            .all()
        )

        por_estado = dict(
            db.session.query(
                Contenido.estado,
                func.count(Contenido.id_contenido)
            )
            .group_by(Contenido.estado)
            .all()
        )

        usuarios_activos = (
            db.session.query(
                func.count(Usuario.id_usuario)
            )
            .filter(Usuario.estado.is_(True))
            .scalar()
        )

        notificaciones_pendientes = (
            db.session.query(
                func.count(Notificacion.id_notif)
            )
            .filter(Notificacion.leida.is_(False))
            .scalar()
        )

        return success(
            {
                "contenido": {
                    "publicado": por_estado.get(
                        "publicado", 0
                    ),
                    "pendiente": por_estado.get(
                        "pendiente", 0
                    ),
                    "rechazado": por_estado.get(
                        "rechazado", 0
                    ),
                    "por_tipo": {
                        tipo: total
                        for tipo, total in por_tipo.items()
                    },
                },
                "usuarios_activos": usuarios_activos,
                "notificaciones_pendientes": (
                    notificaciones_pendientes
                ),
            }
        )

    # --------------------------------------------------------
    # INTERNOS
    # --------------------------------------------------------

    @staticmethod
    def _como_admin(usuario):

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

        return None
