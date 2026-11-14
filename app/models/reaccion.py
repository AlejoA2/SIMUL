from app.extensions import db


class Reaccion(db.Model):

    __tablename__ = "reaccion"

    id_reac = db.Column(
        db.Integer,
        primary_key=True
    )

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        nullable=False,
        index=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    tipo_reaccion = db.Column(
        db.String(16),
        nullable=False
    )

    # Un usuario no puede reaccionar dos veces igual
    # al mismo contenido (UQ usuario + contenido + tipo).
    __table_args__ = (
        db.UniqueConstraint(
            "id_usuario",
            "id_contenido",
            "tipo_reaccion",
            name="uq_reaccion_usuario_contenido_tipo"
        ),
    )

    contenido = db.relationship(
        "Contenido",
        back_populates="reacciones"
    )

    autor = db.relationship(
        "Usuario",
        foreign_keys=[id_usuario]
    )
