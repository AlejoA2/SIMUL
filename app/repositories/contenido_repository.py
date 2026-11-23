from dataclasses import dataclass, field

from sqlalchemy import (
    or_,
    select,
    extract
)

from app.extensions import db


@dataclass
class Pagina:

    """
    Resultado paginado con la interfaz .items, .page,
    .pages y .total, usada por el servicio de contenido.
    """

    items: list = field(default_factory=list)

    page: int = 1

    per_page: int = 12

    total: int = 0

    pages: int = 0

from app.models.contenido import Contenido
from app.models.contenido_tipos import (
    Acontecimiento,
    Premio,
    Proyecto,
    AvanceInvestigacion,
    Evento,
    Noticia,
    HallFama
)
from app.models.evidencia import Evidencia  # noqa: F401 (registro)
from app.models.investigacion import (
    proyecto_tecnologia,
    proyecto_integrante,
    Tecnologia as Tec
)


class ContenidoRepository:

    """Única capa que consulta la tabla contenido (y sus
    subtipos 1:1). Los filtros de la búsqueda usan EXISTS
    sobre los subtipos para no duplicar filas."""

    # --------------------------------------------------------
    # LECTURA
    # --------------------------------------------------------

    def get_by_id(self, contenido_id):

        return db.session.get(
            Contenido,
            contenido_id
        )

    def get_publicados(
        self,
        q=None,
        categoria=None,
        tipo=None,
        anio=None,
        page=1,
        per_page=12
    ):

        query = db.session.query(Contenido).filter(
            Contenido.estado == "publicado"
        )

        query = self._aplicar_filtros(
            query,
            q,
            categoria,
            tipo,
            anio
        )

        # Conteo + página (paginación explícita).
        total = query.count()

        items = (
            query
            .order_by(Contenido.fec_crea.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return Pagina(
            items=items,
            page=page,
            per_page=per_page,
            total=total,
            pages=-(-total // per_page)
        )

    def get_de_usuario(self, usuario_id):

        """Contenido creado por un usuario (mis aportes)."""

        return (
            db.session.query(Contenido)
            .filter(Contenido.id_autor == usuario_id)
            .order_by(Contenido.fec_crea.desc())
            .all()
        )

    def get_acontecimientos(self):

        """Línea del tiempo: subtipo acontecimiento
        publicado, ordenado por año."""

        return (
            db.session.query(Contenido)
            .join(
                Acontecimiento,
                Acontecimiento.id_contenido
                == Contenido.id_contenido
            )
            .filter(Contenido.estado == "publicado")
            .order_by(Acontecimiento.anio)
            .all()
        )

    def get_hall(self):

        """Hall de la fama publicado."""

        return (
            db.session.query(Contenido)
            .join(
                HallFama,
                HallFama.id_contenido == Contenido.id_contenido
            )
            .filter(Contenido.estado == "publicado")
            .order_by(Contenido.fec_crea)
            .all()
        )

    def get_tecnologias_de(self, proyecto):

        """Tecnologías de un proyecto (tabla intermedia)."""

        return (
            db.session.query(Tec)
            .join(
                proyecto_tecnologia,
                proyecto_tecnologia.c.id_tec == Tec.id_tec
            )
            .filter(
                proyecto_tecnologia.c.id_proyecto
                == proyecto.id_contenido
            )
            .order_by(Tec.nombre)
            .all()
        )

    def get_integrantes_de(self, proyecto):

        """Integrantes de un proyecto (tabla intermedia)."""

        from app.models.usuario import Usuario

        return (
            db.session.query(
                Usuario,
                proyecto_integrante.c.rol_en_proyecto
            )
            .join(
                proyecto_integrante,
                proyecto_integrante.c.id_usuario
                == Usuario.id_usuario
            )
            .filter(
                proyecto_integrante.c.id_proyecto
                == proyecto.id_contenido
            )
            .all()
        )

    def count_publicados(self):

        return db.session.query(Contenido).filter(
            Contenido.estado == "publicado"
        ).count()

    def count_por_tipo(self):

        """[(tipo, cantidad)] de todo el contenido."""

        return (
            db.session.query(
                Contenido.tipo,
                db.func.count(Contenido.id_contenido)
            )
            .group_by(Contenido.tipo)
            .all()
        )

    def get_favoritos_de(self, usuario_id):

        from app.models.favorito import Favorito

        return (
            db.session.query(Contenido)
            .join(
                Favorito,
                Favorito.id_contenido
                == Contenido.id_contenido
            )
            .filter(Favorito.id_usuario == usuario_id)
            .order_by(Favorito.fecha_guardado.desc())
            .all()
        )

    # --------------------------------------------------------
    # ESCRITURA (patrón del profesor: el repo hace commit)
    # --------------------------------------------------------

    def create_con_subtipo(
        self,
        contenido,
        subtipo,
        tecnologias=None,
        integrantes=None,
        evidencias=None
    ):

        """
        Crea el contenido y su fila de subtipo 1:1 en una
        sola transacción, más las relaciones simples
        (tecnologías, integrantes, evidencias).
        """

        db.session.add(contenido)

        db.session.flush()

        # ----------------------------------------------------
        # SUBTIPO 1:1 — su PK ES el id recién generado
        # ----------------------------------------------------

        if subtipo is not None:

            subtipo.id_contenido = contenido.id_contenido

            db.session.add(subtipo)

        # ----------------------------------------------------
        # TECNOLOGÍAS (proyecto_tecnologia N:M)
        # ----------------------------------------------------

        for nombre in tecnologias or []:

            tecnologia = self.get_tecnologia(nombre)

            if not tecnologia:

                tecnologia = Tec(nombre=nombre)

                db.session.add(tecnologia)

                db.session.flush()

            vinculo = db.session.execute(
                proyecto_tecnologia.select().where(
                    proyecto_tecnologia.c.id_proyecto
                    == contenido.id_contenido,
                    proyecto_tecnologia.c.id_tec
                    == tecnologia.id_tec
                )
            ).first()

            if not vinculo:

                db.session.execute(
                    proyecto_tecnologia.insert().values(
                        id_proyecto=contenido.id_contenido,
                        id_tec=tecnologia.id_tec
                    )
                )

        # ----------------------------------------------------
        # INTEGRANTES (proyecto_integrante N:M)
        # ----------------------------------------------------

        for usuario_id, rol in integrantes or []:

            vinculo = db.session.execute(
                proyecto_integrante.select().where(
                    proyecto_integrante.c.id_proyecto
                    == contenido.id_contenido,
                    proyecto_integrante.c.id_usuario
                    == usuario_id
                )
            ).first()

            if not vinculo:

                db.session.execute(
                    proyecto_integrante.insert().values(
                        id_proyecto=contenido.id_contenido,
                        id_usuario=usuario_id,
                        rol_en_proyecto=rol
                    )
                )

        # ----------------------------------------------------
        # EVIDENCIAS
        # ----------------------------------------------------

        for evidencia in evidencias or []:

            evidencia.id_contenido = contenido.id_contenido

            db.session.add(evidencia)

        db.session.commit()

        return contenido

    def create(self, contenido):

        db.session.add(contenido)

        db.session.commit()

        return contenido

    def add_evidencia(self, evidencia):

        db.session.add(evidencia)

        db.session.commit()

        return evidencia

    def update(self, contenido):

        db.session.commit()

        return contenido

    def delete(self, contenido):

        db.session.delete(contenido)

        db.session.commit()

    def get_tecnologia(self, nombre):

        return db.session.query(Tec).filter_by(
            nombre=nombre
        ).first()

    # --------------------------------------------------------
    # FILTROS COMUNES
    # --------------------------------------------------------

    def _aplicar_filtros(
        self,
        query,
        q,
        categoria,
        tipo,
        anio
    ):

        if q:

            like = f"%{q}%"

            query = query.filter(
                or_(
                    Contenido.titulo.ilike(like),
                    Contenido.categoria.ilike(like)
                )
            )

        if categoria:

            query = query.filter(
                Contenido.categoria == categoria
            )

        if tipo:

            query = query.filter(
                Contenido.tipo == tipo
            )

        if anio:

            # Cada subtipo guarda el año a su manera:
            # columna anio (4 subtipos) o fecha (evento,
            # noticia). EXISTS evita duplicar la fila base.
            conds = [
                Contenido.id_contenido.in_(
                    select(Acontecimiento.id_contenido).where(
                        Acontecimiento.anio == anio
                    )
                ),
                Contenido.id_contenido.in_(
                    select(Premio.id_contenido).where(
                        Premio.anio == anio
                    )
                ),
                Contenido.id_contenido.in_(
                    select(Proyecto.id_contenido).where(
                        Proyecto.anio == anio
                    )
                ),
                Contenido.id_contenido.in_(
                    select(
                        AvanceInvestigacion.id_contenido
                    ).where(
                        AvanceInvestigacion.anio == anio
                    )
                ),
                Contenido.id_contenido.in_(
                    select(Evento.id_contenido).where(
                        extract("year", Evento.fecha_evento)
                        == anio
                    )
                ),
                Contenido.id_contenido.in_(
                    select(Noticia.id_contenido).where(
                        extract(
                            "year",
                            Noticia.fecha_publicacion
                        )
                        == anio
                    )
                ),
            ]

            query = query.filter(or_(*conds))

        return query
