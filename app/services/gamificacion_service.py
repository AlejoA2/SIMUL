from app.repositories.gamificacion_repository import (
    GamificacionRepository
)

from app.repositories.usuario_repository import (
    UsuarioRepository
)

from app.schemas.simul_auth_schema import UsuarioSchema

from app.utils.response import (
    success,
    error
)


usuario_schema = UsuarioSchema()


class GamificacionService:

    def __init__(self):

        self.gamificacion = GamificacionRepository()

        self.usuarios = UsuarioRepository()

    # --------------------------------------------------------
    # RANKING (RF-GAM-03) — ordenado por puntos_total
    # --------------------------------------------------------

    def ranking(self, limite=100):

        usuarios = self.gamificacion.get_ranking(
            limite=limite
        )

        items = []

        for posicion, usuario in enumerate(
            usuarios,
            start=1
        ):

            items.append(
                {
                    "posicion": posicion,
                    "id_usuario": usuario.id_usuario,
                    "nombre": usuario.nombre,
                    "foto": usuario.foto,
                    "puntos_total": usuario.puntos_total,
                    "nivel": {
                        "numero": usuario.nivel_numero,
                        "nombre": usuario.nivel_nombre,
                    },
                    "insignias": [
                        {
                            "nombre": i.nombre,
                            "icono": i.icono,
                        }
                        for i in usuario.insignias
                    ],
                }
            )

        return success(items)

    # --------------------------------------------------------
    # CATÁLOGOS
    # --------------------------------------------------------

    def niveles(self):

        return success(
            [
                {
                    "numero": n.numero,
                    "nombre": n.nombre,
                    "puntos_min": n.puntos_min,
                    "puntos_max": n.puntos_max,
                }
                for n in self.gamificacion.get_niveles()
            ]
        )

    def insignias(self, usuario=None):

        """Catálogo completo; si hay sesión se marca
        cuáles posee el usuario actual."""

        items = []

        for insignia in self.gamificacion.get_insignias():

            items.append(
                {
                    "id_insig": insignia.id_insig,
                    "nombre": insignia.nombre,
                    "icono": insignia.icono,
                    "puntos_requeridos": (
                        insignia.puntos_requeridos
                    ),
                    "obtenida": (
                        usuario is not None
                        and self.gamificacion
                        .tiene_insignia(
                            usuario,
                            insignia.id_insig
                        )
                    ),
                }
            )

        return success(items)

    # --------------------------------------------------------
    # HISTORIAL DE PUNTOS
    # --------------------------------------------------------

    def historial(self, usuario_id):

        usuario = self.usuarios.get_by_id(usuario_id)

        if not usuario:

            return error(
                "Usuario no encontrado",
                404
            )

        movimientos = self.gamificacion.get_historial(
            usuario_id
        )

        return success(
            {
                "usuario": usuario_schema.dump(usuario),
                "movimientos": [
                    {
                        "id_mov": m.id_mov,
                        "id_contenido": m.id_contenido,
                        "puntos": m.puntos,
                        "motivo": m.motivo,
                        "fecha": m.fecha.isoformat(),
                    }
                    for m in movimientos
                ],
            }
        )
