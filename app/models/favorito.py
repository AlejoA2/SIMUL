from datetime import datetime

from app.extensions import db


class Favorito(db.Model):

    __tablename__ = "favorito"

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        primary_key=True
    )

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        primary_key=True
    )

    fecha_guardado = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    usuario = db.relationship(
        "Usuario",
        foreign_keys=[id_usuario]
    )

    contenido = db.relationship(
        "Contenido",
        back_populates="favoritos"
    )
