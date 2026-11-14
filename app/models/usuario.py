from datetime import datetime

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app.extensions import db


class Usuario(db.Model):

    __tablename__ = "usuario"

    id_usuario = db.Column(
        db.Integer,
        primary_key=True
    )

    id_rol = db.Column(
        db.Integer,
        db.ForeignKey("rol.id_rol"),
        nullable=False
    )

    id_nivel = db.Column(
        db.Integer,
        db.ForeignKey("nivel.id_nivel"),
        nullable=False,
        default=1
    )

    nombre = db.Column(
        db.String(120),
        nullable=False
    )

    correo = db.Column(
        db.String(180),
        nullable=False,
        unique=True,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    foto = db.Column(
        db.String(255),
        nullable=True
    )

    biografia = db.Column(
        db.Text,
        nullable=True
    )

    programa_cohorte = db.Column(
        db.String(120),
        nullable=True
    )

    estado = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    puntos_total = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    fecha_registro = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # --------------------------------------------------------
    # RELACIONES
    # --------------------------------------------------------

    rol = db.relationship(
        "Rol",
        back_populates="usuarios"
    )

    nivel = db.relationship(
        "Nivel",
        back_populates="usuarios"
    )

    insignias = db.relationship(
        "Insignia",
        secondary="usuario_insignia",
        back_populates="usuarios"
    )

    contenidos_creados = db.relationship(
        "Contenido",
        foreign_keys="Contenido.id_autor",
        back_populates="autor"
    )

    contenidos_validados = db.relationship(
        "Contenido",
        foreign_keys="Contenido.id_validador",
        back_populates="validador"
    )

    movimientos = db.relationship(
        "HistorialPuntos",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    # --------------------------------------------------------
    # MÉTODOS
    # --------------------------------------------------------

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )

    @property
    def rol_nombre(self):

        return self.rol.nombre if self.rol else None

    @property
    def nivel_numero(self):

        return self.nivel.numero if self.nivel else None

    @property
    def nivel_nombre(self):

        return self.nivel.nombre if self.nivel else None
