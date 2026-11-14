"""
Esquemas de contenido del museo (y sus subtipos).

- ENTRADA: modelos pydantic que FastAPI valida en la ruta
  (documentados en Swagger/OpenAPI y generan 422 con el
  sobre {success, message, details}).
- SALIDA: modelos pydantic serializados por los services
  con la interfaz .dump().
"""

from datetime import date, datetime
from typing import Literal

from pydantic import Field

from app.schemas.base import Esquema, ModeloSalida


# ============================================================
# ENTRADA
# ============================================================

TipoContenido = Literal[
    "acontecimiento",
    "premio",
    "proyecto",
    "avance_investigacion",
    "evento",
    "noticia",
    "hall",
]


class ContenidoCreateIn(ModeloSalida):

    """POST /api/museo/contenido — todo contenido nace
    pendiente de validación."""

    titulo: str = Field(
        min_length=3,
        max_length=200
    )

    tipo: TipoContenido

    categoria: str = Field(
        min_length=2,
        max_length=80
    )

    anio: int = Field(
        ge=1900,
        le=2100
    )

    descripcion: str = Field(
        min_length=10
    )

    # Campos adicionales según el subtipo (opcionales).
    lugar: str | None = None

    linea_invest: str | None = None

    resultados_impacto: str | None = None

    id_asesor: int | None = None

    tipo_avance: (
        Literal["publicacion", "patente", "software"] | None
    ) = None

    referencia: str | None = None

    id_grupo: int | None = None

    fecha_evento: date | None = None

    objetivo: str | None = None

    categoria_hall: (
        Literal["Docente", "Egresado", "Investigador",
                "Estudiante"] | None
    ) = None

    # Relaciones simples recibidas como texto.
    tecnologias: list[str] = Field(default_factory=list)

    participantes: list[str] = Field(default_factory=list)

    # Imagen principal (RNF-ACC-01: alt_text obligatorio
    # cuando imagen está presente).
    imagen: str | None = None

    alt_text: str | None = None


class ContenidoUpdateIn(ModeloSalida):

    """PUT /api/museo/contenido/<id> — campos parciales
    (solo los enviados se aplican)."""

    titulo: str | None = Field(
        default=None,
        min_length=3,
        max_length=200
    )

    categoria: str | None = Field(
        default=None,
        min_length=2,
        max_length=80
    )

    descripcion: str | None = None

    anio: int | None = Field(
        default=None,
        ge=1900,
        le=2100
    )


class EvidenciaCreateIn(ModeloSalida):

    """POST /api/museo/contenido/<id>/evidencias"""

    tipo: Literal["foto", "video", "doc"]

    url_archivo: str = Field(
        min_length=1,
        max_length=500
    )

    # RNF-ACC-01: obligatorio para imágenes.
    alt_text: str | None = None


class ComentarioCreateIn(ModeloSalida):

    """POST /api/museo/contenido/<id>/comentarios"""

    texto: str = Field(
        min_length=1,
        max_length=2000
    )

    respuesta_a: int | None = None


class ReaccionIn(ModeloSalida):

    """POST /api/museo/contenido/<id>/reacciones"""

    tipo_reaccion: str = Field(
        min_length=1,
        max_length=16
    )


class DecisionIn(ModeloSalida):

    """POST /api/museo/validacion/<id>/aprobar | /rechazar"""

    observaciones: str | None = None


# ============================================================
# SALIDA
# ============================================================

class AutorOut(ModeloSalida):

    id_usuario: int

    nombre: str

    foto: str | None = None


class EvidenciaOut(ModeloSalida):

    id_evid: int

    tipo: str

    url_archivo: str

    alt_text: str | None = None

    fecha_subida: datetime


class ComentarioOut(ModeloSalida):

    id_coment: int

    id_contenido: int

    id_usuario: int

    respuesta_a: int | None = None

    texto: str

    fecha: datetime

    autor: AutorOut | None = None


class ReaccionConteoOut(ModeloSalida):

    tipo_reaccion: str

    total: int

    reaccionado: bool


class ContenidoOut(ModeloSalida):

    id_contenido: int

    tipo: str

    titulo: str

    categoria: str

    estado: str

    observaciones: str | None = None

    fec_crea: datetime

    fec_valid: datetime | None = None

    autor: AutorOut | None = None

    validador: AutorOut | None = None


# ------------------------------------------------------------
# Interfaz .dump() que consumen los services
# ------------------------------------------------------------

class AutorSchema(Esquema):

    modelo = AutorOut


class EvidenciaSchema(Esquema):

    modelo = EvidenciaOut


class ComentarioSchema(Esquema):

    modelo = ComentarioOut


class ReaccionConteoSchema(Esquema):

    modelo = ReaccionConteoOut


class ContenidoSchema(Esquema):

    modelo = ContenidoOut
