"""
Capa de datos del backend (FastAPI + SQLAlchemy puro).

Se conserva la fachada `db` que usan los modelos
(db.Model, db.Column, db.relationship, ...) y los
repositorios (db.session.add/commit), de modo que la
arquitectura por capas del proyecto no cambia.

La sesión de cada petición la instala un middleware de
FastAPI (ver create_app); los scripts fuera de una
petición (seed, pruebas) usan `sesion_bd()`.
"""

from contextlib import contextmanager
from contextvars import ContextVar, Token

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Table as _TablaSQL,
    Text,
    TypeDecorator,
    UniqueConstraint,
    create_engine,
    func
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    relationship,
    sessionmaker
)

from app.config import Config


class Base(DeclarativeBase):

    """Base declarativa compartida por las 25 tablas del
    museo (relaciones, subtipos 1:1 y tablas intermedias)."""


_sesion_actual: ContextVar[Session | None] = ContextVar(
    "sesion_bd",
    default=None
)


class _FachadaDB:

    """
    Fachada con la API de flask-sqlalchemy sobre
    SQLAlchemy puro: modelos, tipos y sesión activa.
    """

    # ---- Modelos ----
    Model = Base
    metadata = Base.metadata

    # ---- Tipos y construcciones usadas por los modelos ----
    Boolean = Boolean
    Column = Column
    Date = Date
    DateTime = DateTime
    Enum = Enum
    ForeignKey = ForeignKey
    Integer = Integer
    Numeric = Numeric
    SmallInteger = SmallInteger
    String = String
    Text = Text
    TypeDecorator = TypeDecorator
    UniqueConstraint = UniqueConstraint
    func = func
    # staticmethod: relationship() es una función y, sin
    # esto, db.relationship(...) recibiría db como primer
    # argumento (enlace de descriptor).
    relationship = staticmethod(relationship)

    @staticmethod
    def Table(nombre, *columnas, **kwargs):

        """Como en flask-sqlalchemy: los modelos declaran
        db.Table(nombre, db.Column(...)) sin pasar la
        metadata; aquí se inyecta automáticamente."""

        return _TablaSQL(
            nombre,
            Base.metadata,
            *columnas,
            **kwargs
        )

    @property
    def session(self) -> Session:

        """Sesión de la petición actual (la instala el
        middleware; ver create_app)."""

        sesion = _sesion_actual.get()

        if sesion is None:

            raise RuntimeError(
                "No hay sesión de base de datos activa: "
                "db.session solo funciona dentro de una "
                "petición (middleware) o de sesion_bd()."
            )

        return sesion


db = _FachadaDB()


# ------------------------------------------------------------
# Motor y fábrica de sesiones
# ------------------------------------------------------------

engine = create_engine(
    Config.DATABASE_URL,
    pool_pre_ping=True,
    future=True
)

SesionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)


@contextmanager
def sesion_bd():

    """
    Sesión para scripts fuera de peticiones (db/seed.py,
    pruebas): instala la sesión, confirma al terminar y
    revierte si algo falla.
    """

    sesion = SesionLocal()

    token = _sesion_actual.set(sesion)

    try:

        yield sesion

        sesion.commit()

    except Exception:

        sesion.rollback()

        raise

    finally:

        _sesion_actual.reset(token)

        sesion.close()


def instalar_sesion() -> tuple[Session, Token]:

    """Crea la sesión de una petición y devuelve (sesión,
    token) para que el middleware pueda restaurarla al
    terminar."""

    sesion = SesionLocal()

    token = _sesion_actual.set(sesion)

    return sesion, token


def restaurar_sesion(token) -> None:

    _sesion_actual.reset(token)


def cerrar_sesion(sesion: Session, token) -> None:

    """Restaura el contexto y cierra la sesión de la
    petición (siempre, haya ido bien o mal)."""

    _sesion_actual.reset(token)

    sesion.close()
