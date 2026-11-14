from datetime import datetime

from app.extensions import db


class Comentario(db.Model):

    __tablename__ = "comentario"

    id_coment = db.Column(
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

    # Árbol de respuestas: autoreferencia a la misma tabla.
    respuesta_a = db.Column(
        db.Integer,
        db.ForeignKey("comentario.id_coment"),
        nullable=True
    )

    texto = db.Column(
        db.Text,
        nullable=False
    )

    fecha = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    contenido = db.relationship(
        "Contenido",
        back_populates="comentarios"
    )

    autor = db.relationship(
        "Usuario",
        foreign_keys=[id_usuario]
    )

    padre = db.relationship(
        "Comentario",
        remote_side=[id_coment]
    )
