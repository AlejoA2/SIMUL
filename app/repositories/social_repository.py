from app.extensions import db

from app.models.comentario import Comentario
from app.models.reaccion import Reaccion
from app.models.favorito import Favorito
from app.models.notificacion import Notificacion


class SocialRepository:

    """Comentarios, reacciones, favoritos y notificaciones."""

    # --------------------------------------------------------
    # COMENTARIOS
    # --------------------------------------------------------

    def get_comentarios(self, contenido_id):

        return (
            db.session.query(Comentario)
            .filter(
                Comentario.id_contenido == contenido_id
            )
            .order_by(Comentario.fecha)
            .all()
        )

    def add_comentario(self, comentario):

        db.session.add(comentario)

        db.session.commit()

        return comentario

    # --------------------------------------------------------
    # REACCIONES
    # --------------------------------------------------------

    def get_reacciones(self, contenido_id):

        return (
            db.session.query(Reaccion)
            .filter(
                Reaccion.id_contenido == contenido_id
            )
            .all()
        )

    def contar_por_tipo(self, contenido_id):

        """[(tipo_reaccion, total)] agregado."""

        return (
            db.session.query(
                Reaccion.tipo_reaccion,
                db.func.count(Reaccion.id_reac)
            )
            .filter(
                Reaccion.id_contenido == contenido_id
            )
            .group_by(Reaccion.tipo_reaccion)
            .all()
        )

    def get_reaccion(
        self,
        usuario_id,
        contenido_id,
        tipo_reaccion
    ):

        return db.session.query(Reaccion).filter_by(
            id_usuario=usuario_id,
            id_contenido=contenido_id,
            tipo_reaccion=tipo_reaccion
        ).first()

    def add_reaccion(self, reaccion):

        db.session.add(reaccion)

        db.session.commit()

        return reaccion

    def remove_reaccion(self, reaccion):

        db.session.delete(reaccion)

        db.session.commit()

    # --------------------------------------------------------
    # FAVORITOS
    # --------------------------------------------------------

    def get_favorito(self, usuario_id, contenido_id):

        return db.session.query(Favorito).filter_by(
            id_usuario=usuario_id,
            id_contenido=contenido_id
        ).first()

    def add_favorito(self, favorito):

        db.session.add(favorito)

        db.session.commit()

        return favorito

    def remove_favorito(self, favorito):

        db.session.delete(favorito)

        db.session.commit()

    # --------------------------------------------------------
    # NOTIFICACIONES
    # --------------------------------------------------------

    def get_notificaciones(
        self,
        usuario_id,
        solo_no_leidas=False
    ):

        query = db.session.query(Notificacion).filter(
            Notificacion.id_usuario == usuario_id
        )

        if solo_no_leidas:

            query = query.filter(
                Notificacion.leida.is_(False)
            )

        return query.order_by(
            Notificacion.fecha_envio.desc()
        ).all()

    def add_notificacion(self, notificacion):

        db.session.add(notificacion)

        return notificacion

    def marcar_leida(self, notificacion):

        notificacion.leida = True

        db.session.commit()

        return notificacion
