"""
Esquemas de autenticación y usuario del museo.

- ENTRADA: modelos pydantic que FastAPI valida en la ruta
  (documentados en Swagger/OpenAPI y generan 422 con el
  sobre {success, message, details}).
- SALIDA: modelos pydantic serializados por los services
  con la interfaz .dump() (sin exponer password_hash).
"""

from datetime import datetime
from typing import Literal

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import Esquema, ModeloSalida


# ============================================================
# ENTRADA
# ============================================================

class SimulRegisterIn(ModeloSalida):

    """POST /api/museo/auth/register"""

    nombre: str = Field(
        min_length=3,
        max_length=120,
        description="Nombre completo (mínimo 3 caracteres)"
    )

    correo: EmailStr = Field(
        description="Correo institucional válido"
    )

    password: str = Field(
        min_length=8,
        description="Contraseña (mínimo 8 caracteres)"
    )

    # Opcionales: la rewiring del frontend puede enviarlos.
    # El rol solo admite cuentas de usuario (nunca admin
    # por autoregistro).
    programa_cohorte: str | None = Field(
        default=None,
        max_length=80
    )

    rol: Literal["estudiante", "docente"] | None = None


class SimulLoginIn(ModeloSalida):

    """POST /api/museo/auth/login"""

    correo: EmailStr
    password: str


class UsuarioUpdateIn(ModeloSalida):

    """
    PUT / PATCH /api/museo/admin/usuarios/<id>
    Cambio de estado / rol / nombre (parcial).
    """

    estado: bool | None = None

    id_rol: int | None = None

    nombre: str | None = Field(
        default=None,
        min_length=3,
        max_length=120
    )

    biografia: str | None = Field(
        default=None,
        max_length=1000
    )


# ============================================================
# SALIDA
# ============================================================

class NivelInfo(ModeloSalida):

    numero: int
    nombre: str
    puntos_min: int
    puntos_max: int


class UsuarioOut(ModeloSalida):

    """Serialización de usuario SIN password_hash."""

    id_usuario: int

    nombre: str

    correo: str

    foto: str | None = None

    biografia: str | None = None

    programa_cohorte: str | None = None

    estado: bool

    puntos_total: int

    fecha_registro: datetime

    rol: str | None = None

    nivel: NivelInfo | None = None

    # ---- Transformaciones desde los modelos ORM ----

    @field_validator("rol", mode="before")
    @classmethod
    def _nombre_del_rol(cls, valor):

        # El ORM trae la relación Rol; la salida va como
        # texto ("admin", "estudiante", ...).
        return valor.nombre if valor is not None else None

    @field_validator("nivel", mode="before")
    @classmethod
    def _datos_del_nivel(cls, valor):

        if valor is None:

            return None

        return {
            "numero": valor.numero,
            "nombre": valor.nombre,
            "puntos_min": valor.puntos_min,
            "puntos_max": valor.puntos_max,
        }


class UsuarioSchema(Esquema):

    """Interfaz .dump() que consumen los services."""

    modelo = UsuarioOut
