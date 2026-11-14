from app.extensions import db


class Rol(db.Model):

    __tablename__ = "rol"

    id_rol = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.Enum(
            "estudiante",
            "docente",
            "admin",
            "egresado",
            name="rol_nombre"
        ),
        nullable=False,
        unique=True
    )

    descripcion = db.Column(
        db.String(255),
        nullable=True
    )

    usuarios = db.relationship(
        "Usuario",
        back_populates="rol"
    )
