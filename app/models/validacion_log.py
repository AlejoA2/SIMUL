from datetime import datetime

from app.extensions import db


class ValidacionLog(db.Model):

    """
    Trazabilidad de cada decisión del validador
    (RF-SEG-04): quién aprobó/rechazó, cuándo y por qué.
    """

    __tablename__ = "validacion_log"

    id_log = db.Column(
        db.Integer,
        primary_key=True
    )

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        nullable=False,
        index=True
    )

    id_admin = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    accion = db.Column(
        db.Enum(
            "aprueba",
            "rechaza",
            name="validacion_accion"
        ),
        nullable=False
    )

    observaciones = db.Column(
        db.Text,
        nullable=True
    )

    fecha_decision = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    contenido = db.relationship(
        "Contenido",
        foreign_keys=[id_contenido]
    )

    validador = db.relationship(
        "Usuario",
        foreign_keys=[id_admin]
    )
