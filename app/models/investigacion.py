from app.extensions import db


# ============================================================
# ÁMBITO DE INVESTIGACIÓN: grupos, tecnologías y las dos
# tablas intermedias N:M (proyecto_tecnologia y premio_hall)
# ============================================================


class GrupoInvestigacion(db.Model):

    __tablename__ = "grupo_investigacion"

    id_grupo = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    tipo = db.Column(
        db.Enum(
            "semillero",
            "grupo",
            name="grupo_tipo"
        ),
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
        nullable=True
    )

    id_lider = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=True
    )

    lider = db.relationship(
        "Usuario",
        foreign_keys=[id_lider]
    )

    avances = db.relationship(
        "AvanceInvestigacion",
        back_populates="grupo"
    )


class Tecnologia(db.Model):

    __tablename__ = "tecnologia"

    id_tec = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(80),
        nullable=False,
        unique=True
    )

    proyectos = db.relationship(
        "Proyecto",
        secondary="proyecto_tecnologia",
        back_populates="tecnologias"
    )


# ------------------------------------------------------------
# PROYECTO_TECNOLOGIA (N:M) — PK compuesta
# ------------------------------------------------------------

proyecto_tecnologia = db.Table(
    "proyecto_tecnologia",

    db.Column(
        "id_proyecto",
        db.Integer,
        db.ForeignKey("proyecto.id_contenido"),
        primary_key=True
    ),

    db.Column(
        "id_tec",
        db.Integer,
        db.ForeignKey("tecnologia.id_tec"),
        primary_key=True
    )
)


# ------------------------------------------------------------
# PREMIO_HALL (N:M premio ↔ hall) — PK compuesta
# ------------------------------------------------------------

premio_hall = db.Table(
    "premio_hall",

    db.Column(
        "id_premio",
        db.Integer,
        db.ForeignKey("premio.id_contenido"),
        primary_key=True
    ),

    db.Column(
        "id_hall",
        db.Integer,
        db.ForeignKey("hall_fama.id_contenido"),
        primary_key=True
    )
)


# ------------------------------------------------------------
# PROYECTO_INTEGRANTE (N:M proyecto ↔ usuario) — PK compuesta
# ------------------------------------------------------------

proyecto_integrante = db.Table(
    "proyecto_integrante",

    db.Column(
        "id_proyecto",
        db.Integer,
        db.ForeignKey("proyecto.id_contenido"),
        primary_key=True
    ),

    db.Column(
        "id_usuario",
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        primary_key=True
    ),

    db.Column(
        "rol_en_proyecto",
        db.String(80),
        nullable=True
    )
)
