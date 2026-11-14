from app.extensions import db
from app.models.rol import Rol
from app.models.usuario import Usuario


class UsuarioRepository:

    """Única capa que consulta la tabla usuario."""

    def get_by_id(self, usuario_id):

        return db.session.get(
            Usuario,
            usuario_id
        )

    def get_by_correo(self, correo):

        return db.session.query(Usuario).filter_by(
            correo=correo
        ).first()

    def get_by_nombre(self, nombre):

        """Primera coincidencia por nombre exacto (para
        vincular participantes de un proyecto)."""

        return db.session.query(Usuario).filter_by(
            nombre=nombre
        ).first()

    def get_all(
        self,
        q=None,
        rol=None,
        estado=None
    ):

        query = db.session.query(Usuario)

        if q:

            like = f"%{q}%"

            query = query.filter(
                Usuario.nombre.ilike(like)
                | Usuario.correo.ilike(like)
            )

        if rol:

            query = query.join(Usuario.rol).filter(
                Rol.nombre == rol
            )

        if estado is not None:

            query = query.filter(
                Usuario.estado == estado
            )

        return query.order_by(
            Usuario.nombre
        ).all()

    def get_by_rol(self, nombre_rol):

        """Usuarios con un rol concreto ('admin', ...)."""

        return (
            db.session.query(Usuario)
            .join(Usuario.rol)
            .filter(Usuario.rol.has(nombre=nombre_rol))
            .all()
        )

    def count(self):

        return db.session.query(Usuario).count()

    def create(self, usuario):

        db.session.add(usuario)

        db.session.commit()

        return usuario

    def update(self, usuario):

        db.session.commit()

        return usuario
