from fastapi import APIRouter, Depends, Query

from app.controllers.admin_controller import (
    AdminController
)
from app.schemas.simul_auth_schema import UsuarioUpdateIn
from app.utils.roles import requiere_usuario


# ============================================================
# APIRouter — administración (RF-USR-05 / RF-DSH-03)
# ============================================================

admin_router = APIRouter(
    tags=["Administración"],
    dependencies=[Depends(requiere_usuario)]
)


controller = AdminController()


# ============================================================
# GESTIÓN DE USUARIOS
# ============================================================

@admin_router.get(
    "/usuarios",
    summary="Listar usuarios (solo admin)",
    description="Filtros: ?q= &rol= &estado=0|1"
)
def usuarios(
    q: str | None = Query(
        None,
        description="Búsqueda por nombre o correo"
    ),
    rol: str | None = Query(
        None,
        description="admin|docente|estudiante"
    ),
    estado: str | None = Query(
        None,
        description="1=activo | 0=inactivo"
    ),
):

    """
    GET /api/museo/admin/usuarios
    """

    return controller.usuarios({
        "q": q,
        "rol": rol,
        "estado": estado,
    })


@admin_router.put(
    "/usuarios/{usuario_id}",
    summary="Actualizar usuario (PUT, solo admin)",
    description="Cambia estado / rol / nombre."
)
def actualizar_usuario(
    usuario_id: int,
    payload: UsuarioUpdateIn
):

    """
    PUT /api/museo/admin/usuarios/<id>
    """

    return controller.actualizar_usuario(
        usuario_id,
        payload.model_dump(exclude_unset=True)
    )


@admin_router.patch(
    "/usuarios/{usuario_id}",
    summary="Actualizar usuario (PATCH, parcial, solo admin)",
    description="Actualización parcial de estado / rol / nombre."
)
def actualizar_usuario_parcial(
    usuario_id: int,
    payload: UsuarioUpdateIn
):

    """
    PATCH /api/museo/admin/usuarios/<id>
    """

    return controller.actualizar_usuario(
        usuario_id,
        payload.model_dump(exclude_unset=True)
    )


# ============================================================
# INDICADORES
# ============================================================

@admin_router.get(
    "/kpis",
    summary="Indicadores del panel (solo admin)"
)
def kpis():

    """
    GET /api/museo/admin/kpis
    """

    return controller.kpis()
