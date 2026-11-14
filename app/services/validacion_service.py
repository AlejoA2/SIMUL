from datetime import datetime

from app.extensions import db

from app.models.contenido import Contenido
from app.models.validacion_log import ValidacionLog
from app.models.notificacion import Notificacion

from app.repositories.contenido_repository import (
    ContenidoRepository
)
from app.repositories.usuario_repository import (
    UsuarioRepository
)
from app.repositories.validacion_repository import (
    ValidacionRepository
)
from app.repositories.gamificacion_repository import (
    GamificacionRepository
)

from app.schemas.contenido_schema import (
    ContenidoSchema
)

from app.utils.response import (
    success,
    error
)


# Gamificación: puntos al publicar (RF-GAM-01).
PUNTOS_PUBLICAR = 100

contenido_schema = ContenidoSchema()


class ValidacionService:

    def __init__(self):

        self.contenidos = ContenidoRepository()

        self.usuarios = UsuarioRepository()

        self.validacion = ValidacionRepository()

        self.gamificacion = GamificacionRepository()

    # --------------------------------------------------------
    # BANDEJA (RF-VAL-01)
    # --------------------------------------------------------

    def bandeja(self):

        pendientes = self.validacion.get_bandeja()

        return success(
            [
                {
                    "id_contenido": c.id_contenido,
                    "titulo": c.titulo,
                    "tipo": c.tipo,
                    "categoria": c.categoria,
                    "fec_crea": c.fec_crea.isoformat(),
                    "autor": (
                        c.autor.nombre
                        if c.autor else None
                    ),
                    "descripcion": self._descripcion(c),
                    "imagen": self._imagen(c),
                }
                for c in pendientes
            ]
        )

    # --------------------------------------------------------
    # APROBAR (RF-VAL-02) — UNA sola transacción
    # --------------------------------------------------------

    def aprobar(self, contenido_id, admin, data=None):

        contenido, respuesta = self._cargar(
            contenido_id,
            admin
        )

        if respuesta:

            return respuesta

        # Las observaciones son opcionales al aprobar.
        observaciones = self._observaciones(data)

        # ----------------------------------------------------
        # 1. ESTADO DEL CONTENIDO
        # ----------------------------------------------------

        contenido.estado = "publicado"
        contenido.id_validador = admin.id_usuario
        contenido.fec_valid = datetime.utcnow()
        contenido.observaciones = observaciones

        # ----------------------------------------------------
        # 2. BITÁCORA DE LA DECISIÓN (RF-SEG-04)
        # ----------------------------------------------------

        self.validacion.add_log(
            ValidacionLog(
                id_contenido=contenido.id_contenido,
                id_admin=admin.id_usuario,
                accion="aprueba",
                observaciones=observaciones
            )
        )

        # ----------------------------------------------------
        # 3. NOTIFICACIÓN AL AUTOR
        # ----------------------------------------------------

        self._notificar(
            contenido,
            "aprobado",
            f'El contenido "{contenido.titulo}" '
            "fue publicado en el museo"
        )

        # ----------------------------------------------------
        # 4. PUNTOS + NIVEL + INSIGNIAS DEL AUTOR
        # ----------------------------------------------------

        autor = contenido.autor

        if autor:

            self.gamificacion.registrar_movimiento(
                usuario=autor,
                puntos=PUNTOS_PUBLICAR,
                motivo=(
                    "Publicación en el museo: "
                    f"{contenido.titulo}"
                ),
                contenido_id=contenido.id_contenido
            )

            self._refrescar_gamificacion(autor)

        # ----------------------------------------------------
        # 5. UN SOLO COMMIT PARA TODO
        # ----------------------------------------------------

        db.session.commit()

        return success(
            contenido_schema.dump(contenido),
            "Contenido aprobado y publicado"
        )

    # --------------------------------------------------------
    # RECHAZAR (RF-VAL-03) — UNA sola transacción
    # --------------------------------------------------------

    def rechazar(self, contenido_id, admin, data=None):

        contenido, respuesta = self._cargar(
            contenido_id,
            admin
        )

        if respuesta:

            return respuesta

        # RNF-SEG-04: el motivo del rechazo es obligatorio.
        observaciones = self._observaciones(data)

        if not observaciones:

            return error(
                "Datos inválidos",
                422,
                {
                    "observaciones": [
                        "El motivo del rechazo es obligatorio"
                    ]
                }
            )

        contenido.estado = "rechazado"
        contenido.id_validador = admin.id_usuario
        contenido.fec_valid = datetime.utcnow()
        contenido.observaciones = observaciones

        self.validacion.add_log(
            ValidacionLog(
                id_contenido=contenido.id_contenido,
                id_admin=admin.id_usuario,
                accion="rechaza",
                observaciones=observaciones
            )
        )

        self._notificar(
            contenido,
            "rechazado",
            f'El contenido "{contenido.titulo}" '
            "fue rechazado. Revisa las observaciones"
        )

        db.session.commit()

        return success(
            contenido_schema.dump(contenido),
            "Contenido rechazado"
        )

    # --------------------------------------------------------
    # HISTÓRICO DE DECISIONES
    # --------------------------------------------------------

    def historial(self, contenido_id):

        logs = self.validacion.get_logs_de(
            contenido_id
        )

        return success(
            [
                {
                    "id_log": log.id_log,
                    "id_contenido": log.id_contenido,
                    "accion": log.accion,
                    "observaciones": log.observaciones,
                    "fecha_decision": (
                        log.fecha_decision.isoformat()
                    ),
                    "validador": (
                        log.validador.nombre
                        if log.validador else None
                    ),
                }
                for log in logs
            ]
        )

    # --------------------------------------------------------
    # INTERNOS
    # --------------------------------------------------------

    def _cargar(self, contenido_id, admin):

        if admin is None or admin.rol_nombre != "admin":

            return None, error(
                "Se requiere rol administrador",
                403
            )

        contenido = self.contenidos.get_by_id(
            contenido_id
        )

        if not contenido:

            return None, error(
                "Contenido no encontrado",
                404
            )

        if contenido.estado != "pendiente":

            return None, error(
                "El contenido no está en la bandeja",
                409
            )

        return contenido, None

    def _observaciones(self, data):

        """Motivo opcional al aprobar, obligatorio al
        rechazar (RF-SEG-04). Devuelve siempre una cadena
        (posiblemente vacía); la obligatoriedad se valida
        en `rechazar`."""

        if not data:

            return ""

        return str(data.get("observaciones") or "").strip()

    def _notificar(self, contenido, tipo, mensaje):

        if not contenido.autor:

            return

        db.session.add(
            Notificacion(
                id_usuario=contenido.autor.id_usuario,
                id_contenido=contenido.id_contenido,
                tipo=tipo,
                mensaje=mensaje
            )
        )

    def _refrescar_gamificacion(self, usuario):

        nivel = self.gamificacion.get_nivel_por_puntos(
            usuario.puntos_total
        )

        if nivel:

            usuario.id_nivel = nivel.id_nivel

        for insignia in self.gamificacion.get_insignias():

            if (
                insignia.puntos_requeridos
                <= usuario.puntos_total
            ):

                self.gamificacion.otorgar_insignia(
                    usuario,
                    insignia
                )

    def _descripcion(self, contenido):

        subtipo_map = {
            "acontecimiento": contenido.acontecimiento,
            "premio": contenido.premio,
            "proyecto": contenido.proyecto,
            "avance_investigacion": contenido.avance,
            "evento": contenido.evento,
            "noticia": contenido.noticia,
            "hall": contenido.hall,
        }

        subtipo = subtipo_map.get(contenido.tipo)

        if subtipo is None:

            return None

        if contenido.tipo == "evento":

            return subtipo.objetivo

        if contenido.tipo == "avance_investigacion":

            return subtipo.referencia

        if contenido.tipo == "noticia":

            return subtipo.contenido_texto[:300]

        if hasattr(subtipo, "descripcion"):

            return subtipo.descripcion

        if hasattr(subtipo, "biografia"):

            return subtipo.biografia

        return None

    def _imagen(self, contenido):

        for evidencia in contenido.evidencias:

            if evidencia.tipo == "foto":

                return evidencia.url_archivo

        return None
