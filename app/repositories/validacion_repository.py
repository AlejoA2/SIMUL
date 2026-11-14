from app.extensions import db

from app.models.contenido import Contenido
from app.models.validacion_log import ValidacionLog


class ValidacionRepository:

    """Bandeja de validación y bitácora de decisiones."""

    def get_bandeja(self):

        """Contenido pendiente de revisión (lo que la
        vista v_bandeja_validacion muestra)."""

        return (
            Contenido.query
            .filter(Contenido.estado == "pendiente")
            .order_by(Contenido.fec_crea.desc())
            .all()
        )

    def get_log(self, log_id):

        return db.session.get(
            ValidacionLog,
            log_id
        )

    def get_logs_de(self, contenido_id):

        return (
            ValidacionLog.query
            .filter(
                ValidacionLog.id_contenido == contenido_id
            )
            .order_by(
                ValidacionLog.fecha_decision.desc()
            )
            .all()
        )

    def add_log(self, log):

        db.session.add(log)

        return log

    def commit(self):

        db.session.commit()
