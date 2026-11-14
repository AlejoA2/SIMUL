from datetime import datetime

from app.extensions import db


class Contenido(db.Model):

    """
    Núcleo del modelo: cada fila representa una pieza del
    museo. El campo `tipo` indica cuál de los 7 subtipos
    (1:1, PK compartida) tiene fila propia: acontecimiento,
    premio, proyecto, avance_investigacion, evento, noticia
    o hall.
    """

    __tablename__ = "contenido"

    id_contenido = db.Column(
        db.Integer,
        primary_key=True
    )

    tipo = db.Column(
        db.Enum(
            "acontecimiento",
            "premio",
            "proyecto",
            "avance_investigacion",
            "evento",
            "noticia",
            "hall",
            name="contenido_tipo"
        ),
        nullable=False
    )

    titulo = db.Column(
        db.String(200),
        nullable=False
    )

    categoria = db.Column(
        db.String(80),
        nullable=False
    )

    id_autor = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    estado = db.Column(
        db.Enum(
            "pendiente",
            "publicado",
            "rechazado",
            name="contenido_estado"
        ),
        nullable=False,
        default="pendiente"
    )

    observaciones = db.Column(
        db.Text,
        nullable=True
    )

    id_validador = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=True
    )

    fec_crea = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    fec_valid = db.Column(
        db.DateTime,
        nullable=True
    )

    # --------------------------------------------------------
    # RELACIONES
    # --------------------------------------------------------

    autor = db.relationship(
        "Usuario",
        foreign_keys=[id_autor],
        back_populates="contenidos_creados"
    )

    validador = db.relationship(
        "Usuario",
        foreign_keys=[id_validador],
        back_populates="contenidos_validados"
    )

    evidencias = db.relationship(
        "Evidencia",
        back_populates="contenido",
        cascade="all, delete-orphan"
    )

    comentarios = db.relationship(
        "Comentario",
        back_populates="contenido",
        cascade="all, delete-orphan"
    )

    reacciones = db.relationship(
        "Reaccion",
        back_populates="contenido",
        cascade="all, delete-orphan"
    )

    favoritos = db.relationship(
        "Favorito",
        back_populates="contenido",
        cascade="all, delete-orphan"
    )

    # Subtipos 1:1 (PK compartida)
    acontecimiento = db.relationship(
        "Acontecimiento",
        back_populates="contenido",
        uselist=False,
        cascade="all, delete-orphan"
    )

    premio = db.relationship(
        "Premio",
        back_populates="contenido",
        uselist=False,
        cascade="all, delete-orphan"
    )

    proyecto = db.relationship(
        "Proyecto",
        back_populates="contenido",
        uselist=False,
        cascade="all, delete-orphan"
    )

    avance = db.relationship(
        "AvanceInvestigacion",
        back_populates="contenido",
        uselist=False,
        cascade="all, delete-orphan"
    )

    evento = db.relationship(
        "Evento",
        back_populates="contenido",
        uselist=False,
        cascade="all, delete-orphan"
    )

    noticia = db.relationship(
        "Noticia",
        back_populates="contenido",
        uselist=False,
        cascade="all, delete-orphan"
    )

    hall = db.relationship(
        "HallFama",
        back_populates="contenido",
        uselist=False,
        cascade="all, delete-orphan"
    )
