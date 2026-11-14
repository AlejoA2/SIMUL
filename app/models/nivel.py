from app.extensions import db


class Nivel(db.Model):

    __tablename__ = "nivel"

    id_nivel = db.Column(
        db.Integer,
        primary_key=True
    )

    numero = db.Column(
        db.SmallInteger,
        nullable=False,
        unique=True
    )

    nombre = db.Column(
        db.String(40),
        nullable=False
    )

    puntos_min = db.Column(
        db.Integer,
        nullable=False
    )

    puntos_max = db.Column(
        db.Integer,
        nullable=False
    )

    usuarios = db.relationship(
        "Usuario",
        back_populates="nivel"
    )
