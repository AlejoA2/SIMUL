from app.extensions import db

from app.models.nivel import Nivel
from app.models.insignia import Insignia
from app.models.historial_puntos import HistorialPuntos
from app.models.usuario import Usuario


class GamificacionRepository:

    """Catálogos de gamificación: niveles, insignias,
    ranking e historial de puntos."""

    # --------------------------------------------------------
    # CATÁLOGOS
    # --------------------------------------------------------

    def get_niveles(self):

        return db.session.query(Nivel).order_by(
            Nivel.numero
        ).all()

    def get_nivel_por_puntos(self, puntos):

        """Nivel cuyo rango contiene los puntos dados.
        Regla de frontera: >= min y < max (el último
        nivel incluye su máximo)."""

        niveles = self.get_niveles()

        for nivel in niveles:

            if nivel.numero == len(niveles):

                if puntos >= nivel.puntos_min:

                    return nivel

            elif (
                puntos >= nivel.puntos_min
                and puntos < nivel.puntos_max
            ):

                return nivel

        return niveles[0] if niveles else None

    def get_insignias(self):

        return db.session.query(Insignia).order_by(
            Insignia.puntos_requeridos
        ).all()

    # --------------------------------------------------------
    # USUARIO ↔ INSIGNIA (N:M)
    # --------------------------------------------------------

    def tiene_insignia(self, usuario, insignia_id):

        return any(
            i.id_insig == insignia_id
            for i in usuario.insignias
        )

    def otorgar_insignia(self, usuario, insignia):

        """Vincula la insignia al usuario. NO hace commit:
        el servicio cierra la transacción completa (puntos,
        nivel, insignias y notificación en un solo commit)."""

        if self.tiene_insignia(
            usuario,
            insignia.id_insig
        ):

            return False

        usuario.insignias.append(insignia)

        return True

    # --------------------------------------------------------
    # RANKING
    # --------------------------------------------------------

    def get_ranking(self, limite=100):

        return (
            db.session.query(Usuario)
            .filter(Usuario.estado.is_(True))
            .order_by(Usuario.puntos_total.desc())
            .limit(limite)
            .all()
        )

    # --------------------------------------------------------
    # HISTORIAL DE PUNTOS
    # --------------------------------------------------------

    def get_historial(self, usuario_id, limite=50):

        return (
            db.session.query(HistorialPuntos)
            .filter(
                HistorialPuntos.id_usuario == usuario_id
            )
            .order_by(HistorialPuntos.fecha.desc())
            .limit(limite)
            .all()
        )

    def registrar_movimiento(
        self,
        usuario,
        puntos,
        motivo,
        contenido_id=None
    ):

        """Suma puntos al usuario y guarda el movimiento.
        Debe invocarse dentro de la misma transacción que
        el cambio de estado que lo origina."""

        movimiento = HistorialPuntos(
            id_usuario=usuario.id_usuario,
            id_contenido=contenido_id,
            puntos=puntos,
            motivo=motivo
        )

        usuario.puntos_total += puntos

        db.session.add(movimiento)

        return movimiento

    def commit(self):

        db.session.commit()
