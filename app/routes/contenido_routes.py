from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.controllers.contenido_controller import (
    ContenidoController
)
from app.schemas.contenido_schema import (
    ComentarioCreateIn,
    ContenidoCreateIn,
    ContenidoUpdateIn,
    EvidenciaCreateIn,
    ReaccionIn
)
from app.utils.roles import (
    requiere_usuario,
    usuario_opcional
)


# ============================================================
# APIRouter — contenido del museo
# ============================================================

contenido_router = APIRouter(
    tags=["Contenido"]
)


controller = ContenidoController()


# ============================================================
# LISTAR (público, con filtros de búsqueda)
# ============================================================

@contenido_router.get(
    "/",
    summary="Listar contenido (con filtros)",
    description=(
        "Por defecto solo publicado. El filtro estado=pendiente|"
        "rechazado requiere sesión de administrador."
    ),
    dependencies=[Depends(usuario_opcional)]
)
def listar(
    q: str | None = Query(
        None,
        description="Texto a buscar en título/descripción"
    ),
    categoria: str | None = Query(
        None,
        description="Filtrar por categoría exacta"
    ),
    tipo: str | None = Query(
        None,
        description=(
            "acontecimiento|premio|proyecto|"
            "avance_investigacion|evento|noticia|hall"
        )
    ),
    anio: int | None = Query(
        None,
        ge=1900,
        le=2100,
        description="Año del contenido"
    ),
    estado: Literal[
        "publicado", "pendiente", "rechazado"
    ] | None = Query(
        None,
        description="Estado del contenido (solo admin si no es publicado)"
    ),
    page: int | None = Query(
        None,
        ge=1,
        description="Página (por defecto 1)"
    ),
    per_page: int | None = Query(
        None,
        ge=1,
        le=100,
        description="Ítems por página (por defecto 12)"
    ),
):

    """
    GET /api/museo/contenido
    Filtros: ?q= &categoria= &tipo= &anio= &estado= &page= &per_page=
    """

    return controller.listar({
        "q": q,
        "categoria": categoria,
        "tipo": tipo,
        "anio": anio,
        "estado": estado,
        "page": page,
        "per_page": per_page,
    })


# ============================================================
# MIS APORTES / FAVORITOS (rutas fijas antes de /{id})
# ============================================================

@contenido_router.get(
    "/mis-aportes",
    summary="Contenido creado por el usuario",
    dependencies=[Depends(requiere_usuario)]
)
def mis_aportes():

    """
    GET /api/museo/contenido/mis-aportes
    """

    return controller.mis_aportes()


@contenido_router.get(
    "/favoritos",
    summary="Favoritos del usuario",
    dependencies=[Depends(requiere_usuario)]
)
def favoritos():

    """
    GET /api/museo/contenido/favoritos
    """

    return controller.favoritos()


# ============================================================
# CREAR (todo contenido nace pendiente)
# ============================================================

@contenido_router.post(
    "/",
    summary="Crear contenido (nace pendiente)",
    description=(
        "Asocia el subtipo según el campo tipo. "
        "RNF-ACC-01: si viene imagen, alt_text es "
        "obligatorio (422). Suma 100 puntos al publicarse."
    ),
    dependencies=[Depends(requiere_usuario)]
)
def crear(payload: ContenidoCreateIn):

    """
    POST /api/museo/contenido
    """

    return controller.crear(payload.model_dump())


# ============================================================
# DETALLE / EDITAR / ELIMINAR
# ============================================================

@contenido_router.get(
    "/{contenido_id}",
    summary="Detalle de un contenido",
    description=(
        "Público: con sesión válida agrega es_favorito "
        "del usuario actual."
    ),
    dependencies=[Depends(usuario_opcional)]
)
def detalle(contenido_id: int):

    """
    GET /api/museo/contenido/<id>
    """

    return controller.detalle(contenido_id)


@contenido_router.put(
    "/{contenido_id}",
    summary="Actualizar contenido (PUT)",
    description="Aplica solo los campos enviados.",
    dependencies=[Depends(requiere_usuario)]
)
def actualizar(
    contenido_id: int,
    payload: ContenidoUpdateIn
):

    """
    PUT /api/museo/contenido/<id>
    """

    return controller.actualizar(
        contenido_id,
        payload.model_dump(exclude_unset=True)
    )


@contenido_router.patch(
    "/{contenido_id}",
    summary="Actualizar contenido (PATCH, parcial)",
    description="Actualización parcial de campos del contenido.",
    dependencies=[Depends(requiere_usuario)]
)
def actualizar_parcial(
    contenido_id: int,
    payload: ContenidoUpdateIn
):

    """
    PATCH /api/museo/contenido/<id>
    """

    return controller.actualizar(
        contenido_id,
        payload.model_dump(exclude_unset=True)
    )


@contenido_router.delete(
    "/{contenido_id}",
    summary="Eliminar contenido (solo admin)",
    dependencies=[Depends(requiere_usuario)]
)
def eliminar(contenido_id: int):

    """
    DELETE /api/museo/contenido/<id>
    """

    return controller.eliminar(contenido_id)


# ============================================================
# EVIDENCIAS (RF-EVD-01)
# ============================================================

@contenido_router.get(
    "/{contenido_id}/evidencias",
    summary="Listar evidencias de un contenido"
)
def listar_evidencias(contenido_id: int):

    """
    GET /api/museo/contenido/<id>/evidencias
    """

    return controller.listar_evidencias(contenido_id)


@contenido_router.post(
    "/{contenido_id}/evidencias",
    summary="Adjuntar evidencia a un contenido",
    description=(
        "RNF-ACC-01: si tipo==foto, alt_text es "
        "obligatorio (422)."
    ),
    dependencies=[Depends(requiere_usuario)]
)
def agregar_evidencia(
    contenido_id: int,
    payload: EvidenciaCreateIn
):

    """
    POST /api/museo/contenido/<id>/evidencias
    """

    return controller.agregar_evidencia(
        contenido_id,
        payload.model_dump()
    )


# ============================================================
# COMENTARIOS (RF-CMT-01)
# ============================================================

@contenido_router.get(
    "/{contenido_id}/comentarios",
    summary="Listar comentarios de un contenido"
)
def listar_comentarios(contenido_id: int):

    """
    GET /api/museo/contenido/<id>/comentarios
    """

    return controller.listar_comentarios(contenido_id)


@contenido_router.post(
    "/{contenido_id}/comentarios",
    summary="Comentar contenido (+10 puntos la primera vez)",
    dependencies=[Depends(requiere_usuario)]
)
def comentar(
    contenido_id: int,
    payload: ComentarioCreateIn
):

    """
    POST /api/museo/contenido/<id>/comentarios
    """

    return controller.comentar(
        contenido_id,
        payload.model_dump()
    )


# ============================================================
# REACCIONES (RF-REA-01) — alterna
# ============================================================

@contenido_router.post(
    "/{contenido_id}/reaccion",
    summary="Reaccionar o quitar reacción (alterna)",
    dependencies=[Depends(requiere_usuario)]
)
def reaccionar(
    contenido_id: int,
    payload: ReaccionIn
):

    """
    POST /api/museo/contenido/<id>/reaccion
    """

    return controller.reaccionar(
        contenido_id,
        payload.model_dump()
    )


# ============================================================
# FAVORITOS — alterna
# ============================================================

@contenido_router.post(
    "/{contenido_id}/favorito",
    summary="Guardar o quitar de favoritos (alterna)",
    dependencies=[Depends(requiere_usuario)]
)
def favorito(contenido_id: int):

    """
    POST /api/museo/contenido/<id>/favorito
    """

    return controller.favorito(contenido_id)
