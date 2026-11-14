# Modelos del dominio SIMUL (25 tablas del modelo E-R)
from app.models.rol import Rol
from app.models.nivel import Nivel
from app.models.usuario import Usuario
from app.models.insignia import Insignia, usuario_insignia
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
from app.models.evidencia import Evidencia
from app.models.comentario import Comentario
from app.models.reaccion import Reaccion
from app.models.favorito import Favorito
from app.models.notificacion import Notificacion
from app.models.validacion_log import ValidacionLog
from app.models.historial_puntos import HistorialPuntos
from app.models.investigacion import (
    GrupoInvestigacion,
    Tecnologia,
    proyecto_tecnologia,
    premio_hall,
    proyecto_integrante
)


__all__ = [
    "Rol",
    "Nivel",
    "Usuario",
    "Insignia",
    "usuario_insignia",
    "Contenido",
    "Acontecimiento",
    "Premio",
    "Proyecto",
    "AvanceInvestigacion",
    "Evento",
    "Noticia",
    "HallFama",
    "Evidencia",
    "Comentario",
    "Reaccion",
    "Favorito",
    "Notificacion",
    "ValidacionLog",
    "HistorialPuntos",
    "GrupoInvestigacion",
    "Tecnologia",
    "proyecto_tecnologia",
    "premio_hall",
    "proyecto_integrante",
]
