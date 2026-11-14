from datetime import datetime

from app.extensions import db


class Notificacion(db.Model):

    __tablename__ = "notificacion"

    # Índice compuesto del DDL: (id_usuario, leida) — la
    # consulta típica es "mis notificaciones sin leer".
    __table_args__ = (
        db.Index(
            "idx_notif_usuario_leida",
            "id_usuario",
            "leida"
        ),
    )

    id_notif = db.Column(
        db.Integer,
        primary_key=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        nullable=True
    )

    tipo = db.Column(
        db.String(40),
        nullable=False
    )

    mensaje = db.Column(
        db.String(255),
        nullable=False
    )

    leida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    fecha_envio = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    destinatario = db.relationship(
        "Usuario",
        foreign_keys=[id_usuario]
    )

    contenido = db.relationship(
        "Contenido",
        foreign_keys=[id_contenido]
    )
