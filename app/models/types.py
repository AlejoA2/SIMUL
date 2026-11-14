from sqlalchemy.dialects import mysql

from app.extensions import db


class YearType(db.TypeDecorator):

    """
    Tipo YEAR portable: en MySQL se crea como YEAR
    (como en el diagrama E-R) y en el fallback SQLite
    de Config se crea como SMALLINT para no romper.
    """

    impl = db.SmallInteger

    cache_ok = True

    def load_dialect_impl(self, dialect):

        if dialect.name == "mysql":

            return dialect.type_descriptor(
                mysql.YEAR()
            )

        return dialect.type_descriptor(
            db.SmallInteger()
        )
