from datetime import datetime

from app.extensions import db


class HistorialPuntos(db.Model):

    """
    Movimientos de puntos de un usuario: cada fila es un
    gana/pierde con motivo. La suma de los movimientos
    debe coincidir con usuario.puntos_total.
    """

    __tablename__ = "historial_puntos"

    id_mov = db.Column(
        db.Integer,
        primary_key=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=False,
        index=True
    )

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        nullable=True
    )

    puntos = db.Column(
        db.Integer,
        nullable=False
    )

    motivo = db.Column(
        db.String(150),
        nullable=False
    )

    fecha = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="movimientos"
    )

    contenido = db.relationship(
        "Contenido",
        foreign_keys=[id_contenido]
    )
