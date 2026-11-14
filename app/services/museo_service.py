from sqlalchemy import func

from app.extensions import db

from app.models.contenido import Contenido
from app.models.usuario import Usuario
from app.models.notificacion import Notificacion

from app.repositories.contenido_repository import (
    ContenidoRepository
)
from app.repositories.usuario_repository import (
    UsuarioRepository
)
from app.repositories.social_repository import (
    SocialRepository
)

from app.utils.response import (
    success,
    error
)


class MuseoService:

    """Vistas transversales del museo: portada, línea
    del tiempo, hall de la fama, categorías y
    notificaciones del usuario."""

    def __init__(self):

        self.contenidos = ContenidoRepository()

        self.usuarios = UsuarioRepository()

        self.social = SocialRepository()

    # --------------------------------------------------------
    # PORTADA
    # --------------------------------------------------------

    def home(self):

        total_contenido = self.contenidos.count_publicados()

        por_tipo = dict(
            self.contenidos.count_por_tipo()
        )

        total_usuarios = (
            db.session.query(
                func.count(Usuario.id_usuario)
            )
            .filter(Usuario.estado.is_(True))
            .scalar()
        )

        # Destacados: los últimos 6 publicados.
        destacados = self.contenidos.get_publicados(
            page=1,
            per_page=6
        )

        return success(
            {
                "stats": [
                    {
                        "valor": str(total_contenido),
                        "etiqueta": "Contenidos del museo",
                    },
                    {
                        "valor": str(total_usuarios),
                        "etiqueta": "Usuarios activos",
                    },
                    {
                        "valor": str(
                            por_tipo.get("proyecto", 0)
                        ),
                        "etiqueta": "Proyectos",
                    },
                    {
                        "valor": str(
                            por_tipo.get("premio", 0)
                        ),
                        "etiqueta": "Premios",
                    },
                ],
                "destacados": [
                    {
                        "id_contenido": c.id_contenido,
                        "titulo": c.titulo,
                        "tipo": c.tipo,
                        "categoria": c.categoria,
                        "fec_crea": c.fec_crea.isoformat(),
                    }
                    for c in destacados.items
                ],
            }
        )

    # --------------------------------------------------------
    # LÍNEA DEL TIEMPO (RF-HIS-01)
    # --------------------------------------------------------

    def timeline(self):

        contenidos = self.contenidos.get_acontecimientos()

        items = []

        for contenido in contenidos:

            acont = contenido.acontecimiento

            items.append(
                {
                    "id_contenido": contenido.id_contenido,
                    "anio": int(acont.anio),
                    "titulo": contenido.titulo,
                    "descripcion": acont.descripcion,
                    "categoria": contenido.categoria,
                }
            )

        return success(items)

    # --------------------------------------------------------
    # HALL DE LA FAMA
    # --------------------------------------------------------

    def hall(self):

        contenidos = self.contenidos.get_hall()

        items = []

        for contenido in contenidos:

            hall = contenido.hall

            items.append(
                {
                    "id_contenido": contenido.id_contenido,
                    "titulo": contenido.titulo,
                    "categoria": hall.categoria,
                    "biografia": hall.biografia,
                    "persona": {
                        "id_usuario": hall.persona.id_usuario,
                        "nombre": hall.persona.nombre,
                        "foto": hall.persona.foto,
                    },
                    "premios": [
                        p.contenido.titulo
                        for p in hall.premios
                        if p.contenido
                    ],
                }
            )

        return success(items)

    # --------------------------------------------------------
    # CATEGORÍAS (para explorar / buscador)
    # --------------------------------------------------------

    def categorias(self):

        filas = (
            db.session.query(
                Contenido.categoria,
                func.count(Contenido.id_contenido)
            )
            .filter(Contenido.estado == "publicado")
            .group_by(Contenido.categoria)
            .order_by(
                func.count(Contenido.id_contenido).desc()
            )
            .all()
        )

        return success(
            [
                {
                    "categoria": categoria,
                    "total": total,
                }
                for categoria, total in filas
            ]
        )

    def anios(self):

        """Años disponibles (derivado de los subtipos)."""

        contenidos = (
            db.session.query(Contenido)
            .filter(Contenido.estado == "publicado")
            .all()
        )

        anios = set()

        for contenido in contenidos:

            subtipo_map = {
                "acontecimiento": (
                    contenido.acontecimiento
                ),
                "premio": contenido.premio,
                "proyecto": contenido.proyecto,
                "avance_investigacion": (
                    contenido.avance
                ),
                "evento": contenido.evento,
                "noticia": contenido.noticia,
            }

            subtipo = subtipo_map.get(contenido.tipo)

            if subtipo is None:

                continue

            if hasattr(subtipo, "anio"):

                anios.add(int(subtipo.anio))

            elif contenido.tipo == "evento":

                anios.add(subtipo.fecha_evento.year)

            elif contenido.tipo == "noticia":

                anios.add(
                    subtipo.fecha_publicacion.year
                )

        return success(
            sorted(anios, reverse=True)
        )

    # --------------------------------------------------------
    # NOTIFICACIONES (RF-NOT-01)
    # --------------------------------------------------------

    def notificaciones(
        self,
        usuario,
        solo_no_leidas=False
    ):

        notificaciones = (
            self.social.get_notificaciones(
                usuario.id_usuario,
                solo_no_leidas=solo_no_leidas
            )
        )

        return success(
            {
                "total": len(notificaciones),
                "no_leidas": sum(
                    1 for n in notificaciones
                    if not n.leida
                ),
                "items": [
                    {
                        "id_notif": n.id_notif,
                        "id_contenido": n.id_contenido,
                        "tipo": n.tipo,
                        "mensaje": n.mensaje,
                        "leida": n.leida,
                        "fecha_envio": (
                            n.fecha_envio.isoformat()
                        ),
                    }
                    for n in notificaciones
                ],
            }
        )

    def marcar_leida(self, usuario, notif_id):

        notificacion = db.session.get(
            Notificacion,
            notif_id
        )

        if not notification_exists(
            notificacion,
            usuario
        ):

            return error(
                "Notificación no encontrada",
                404
            )

        self.social.marcar_leida(notificacion)

        return success(
            None,
            "Notificación marcada como leída"
        )


def notification_exists(notificacion, usuario):

    return (
        notificacion is not None
        and notificacion.id_usuario
        == usuario.id_usuario
    )
