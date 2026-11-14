from app.models.types import YearType

from app.extensions import db


# ============================================================
# LOS 7 SUBTIPOS DE CONTENIDO — herencia 1:1 con PK
# compartida: la PK de cada una ES la FK a contenido.id.
# Cada tipo de contenido del ER tiene aquí su clase.
# ============================================================


class Acontecimiento(db.Model):

    __tablename__ = "acontecimiento"

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        primary_key=True
    )

    anio = db.Column(
        YearType,
        nullable=False,
        index=True
    )

    descripcion = db.Column(
        db.Text,
        nullable=False
    )

    contenido = db.relationship(
        "Contenido",
        back_populates="acontecimiento"
    )


class Premio(db.Model):

    __tablename__ = "premio"

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        primary_key=True
    )

    anio = db.Column(
        YearType,
        nullable=False
    )

    lugar = db.Column(
        db.String(150),
        nullable=True
    )

    descripcion = db.Column(
        db.Text,
        nullable=False
    )

    contenido = db.relationship(
        "Contenido",
        back_populates="premio"
    )

    halls = db.relationship(
        "HallFama",
        secondary="premio_hall",
        back_populates="premios"
    )


class Proyecto(db.Model):

    __tablename__ = "proyecto"

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        primary_key=True
    )

    anio = db.Column(
        YearType,
        nullable=False,
        index=True
    )

    linea_invest = db.Column(
        db.String(150),
        nullable=True
    )

    descripcion = db.Column(
        db.Text,
        nullable=False
    )

    resultados_impacto = db.Column(
        db.Text,
        nullable=True
    )

    id_asesor = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=True
    )

    contenido = db.relationship(
        "Contenido",
        back_populates="proyecto"
    )

    asesor = db.relationship(
        "Usuario",
        foreign_keys=[id_asesor]
    )

    tecnologias = db.relationship(
        "Tecnologia",
        secondary="proyecto_tecnologia",
        back_populates="proyectos"
    )

    integrantes = db.relationship(
        "Usuario",
        secondary="proyecto_integrante"
    )


class AvanceInvestigacion(db.Model):

    __tablename__ = "avance_investigacion"

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        primary_key=True
    )

    tipo = db.Column(
        db.Enum(
            "publicacion",
            "patente",
            "software",
            name="avance_tipo"
        ),
        nullable=False
    )

    anio = db.Column(
        YearType,
        nullable=False,
        index=True
    )

    referencia = db.Column(
        db.String(255),
        nullable=True
    )

    id_grupo = db.Column(
        db.Integer,
        db.ForeignKey("grupo_investigacion.id_grupo"),
        nullable=True
    )

    contenido = db.relationship(
        "Contenido",
        back_populates="avance"
    )

    grupo = db.relationship(
        "GrupoInvestigacion",
        back_populates="avances"
    )


class Evento(db.Model):

    __tablename__ = "evento"

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        primary_key=True
    )

    fecha_evento = db.Column(
        db.Date,
        nullable=False
    )

    lugar = db.Column(
        db.String(150),
        nullable=True
    )

    objetivo = db.Column(
        db.String(255),
        nullable=True
    )

    contenido = db.relationship(
        "Contenido",
        back_populates="evento"
    )


class Noticia(db.Model):

    __tablename__ = "noticia"

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        primary_key=True
    )

    contenido_texto = db.Column(
        "contenido",
        db.Text,
        nullable=False
    )

    fecha_publicacion = db.Column(
        db.Date,
        nullable=False
    )

    contenido = db.relationship(
        "Contenido",
        back_populates="noticia"
    )


class HallFama(db.Model):

    __tablename__ = "hall_fama"

    id_contenido = db.Column(
        db.Integer,
        db.ForeignKey("contenido.id_contenido"),
        primary_key=True
    )

    categoria = db.Column(
        db.Enum(
            "Docente",
            "Egresado",
            "Investigador",
            "Estudiante",
            name="hall_categoria"
        ),
        nullable=False
    )

    biografia = db.Column(
        db.Text,
        nullable=False
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    contenido = db.relationship(
        "Contenido",
        back_populates="hall"
    )

    persona = db.relationship(
        "Usuario",
        foreign_keys=[id_usuario]
    )

    premios = db.relationship(
        "Premio",
        secondary="premio_hall",
        back_populates="halls"
    )
