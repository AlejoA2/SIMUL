from datetime import datetime

from app.extensions import db


# ------------------------------------------------------------
# Tabla intermedia USUARIO_INSIGNIA (N:M) — declarada como
# modelo para que aparezca en create_all() y en el ER.
# ------------------------------------------------------------

usuario_insignia = db.Table(
    "usuario_insignia",

    db.Column(
        "id_usuario",
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        primary_key=True
    ),

    db.Column(
        "id_insig",
        db.Integer,
        db.ForeignKey("insignia.id_insig"),
        primary_key=True
    ),

    db.Column(
        "fecha_otorgada",
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
)


class Insignia(db.Model):

    __tablename__ = "insignia"

    id_insig = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(60),
        nullable=False,
        unique=True
    )

    icono = db.Column(
        db.String(8),
        nullable=False
    )

    puntos_requeridos = db.Column(
        db.Integer,
        nullable=False
    )

    usuarios = db.relationship(
        "Usuario",
        secondary=usuario_insignia,
        back_populates="insignias"
    )
