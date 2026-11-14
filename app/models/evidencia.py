from datetime import datetime

from app.extensions import db


class Evidencia(db.Model):

    __tablename__ = "evidencia"

    id_evid = db.Column(
        db.Integer,
        primary_key=True
    )

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        nullable=False,
        index=True
    )

    tipo = db.Column(
        db.Enum(
            "foto",
            "video",
            "doc",
            name="evidencia_tipo"
        ),
        nullable=False
    )

    url_archivo = db.Column(
        db.String(500),
        nullable=False
    )

    # Requisito de accesibilidad RNF-ACC-01.
    alt_text = db.Column(
        db.String(255),
        nullable=True
    )

    fecha_subida = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    contenido = db.relationship(
        "Contenido",
        back_populates="evidencias"
    )
