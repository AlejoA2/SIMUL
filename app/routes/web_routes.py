"""
=============================================================
RUTAS WEB - Museo Digital Interactivo (SIMUL)
=============================================================

Solo vistas HTML (Jinja2 vía FastAPI). Las URLs conservan
los mismos nombres de endpoint que el template de Flask
(web.index, web.explorar, ...) para que los `url_for()` de
los templates sigan funcionando tal cual.

Nota sobre los datos
--------------------
Este corte es frontend: cada vista lee de
`app/data/simul_data.py` y entrega además el mismo JSON a
la página mediante `tojson`. La rewiring a la API REST
(/api/museo/*) ocurre en el JavaScript de cada página; el
contexto del servidor queda como datos iniciales.

Las páginas privadas (dashboards, administración) no se
protegen en el servidor porque la sesión vive en
localStorage; la guarda real la aplica `guardPage()` en
app/static/js/app.js.
=============================================================
"""

from fastapi import APIRouter, Request

from app.data import simul_data as data
from app.utils.templados import renderizar


web_router = APIRouter(
    include_in_schema=False
)


# ==========================================================
# HELPERS
# ==========================================================

def _common_context():
    """
    Datos que casi todas las vistas necesitan.

    `role_labels` viaja al navegador para que la navbar
    pueda mostrar "Estudiante" / "Docente" / "Administrador"
    sin otro viaje al servidor.
    """
    return {
        "role_labels": data.ROLE_LABELS,
    }


# ==========================================================
# PÚBLICO
# ==========================================================

@web_router.get("/", name="web.index")
def index(request: Request):
    """
    Portada del museo: banner, acceso rápido por categoría,
    adelanto del Hall de la Fama y llamada a iniciar sesión.
    """
    return renderizar(
        request,
        "pages/index.html",
        stats=data.HOME_STATS,
        quick_access=data.HOME_QUICK_ACCESS,
        hall_preview=data.HALL_OF_FAME,
        hero_image=data.HOME_HERO_IMAGE,
        **_common_context()
    )


@web_router.get("/explorar", name="web.explorar")
def explorar(request: Request):
    """
    Catálogo de categorías del museo (RF-EXP-01).
    """
    return renderizar(
        request,
        "pages/explorar.html",
        categories=data.EXPLORE_CATEGORIES,
        selected_cat=request.query_params.get("cat"),
        **_common_context()
    )


@web_router.get("/buscar", name="web.buscar")
def buscar(request: Request):
    """
    Buscador con filtros por texto, categoría y año
    (RF-EXP-02). El filtrado ocurre en el navegador.
    """
    return renderizar(
        request,
        "pages/buscar.html",
        categories=data.SEARCH_CATEGORIES,
        years=data.SEARCH_YEARS,
        selected_cat=request.query_params.get("cat"),
        initial_query=request.query_params.get("q", ""),
        **{
            "simul_content": data.CONTENT_ITEMS,
            "category_slug_map": data.CATEGORY_SLUG_MAP,
        },
        **_common_context()
    )


@web_router.get(
    "/contenido/{contenido_id}",
    name="web.detalle_contenido"
)
def detalle_contenido(request: Request, contenido_id: str):
    """
    Detalle de una pieza del museo: galería, reacciones,
    comentarios, participantes, tecnologías y documentos.

    El JS completa las partes dinámicas (reacciones,
    comentarios, favoritos, línea del tiempo).
    """
    item = next(
        (
            c for c in data.CONTENT_ITEMS
            if c["id"] == contenido_id
        ),
        None
    )

    if item is None:
        return renderizar(
            request,
            "pages/contenido_no_encontrado.html",
            status_code=404,
            contenido_id=contenido_id,
            **_common_context()
        )

    relacionados = [
        c for c in data.CONTENT_ITEMS
        if c["id"] != contenido_id and c["status"] == "publicado"
    ][:3]

    return renderizar(
        request,
        "pages/contenido.html",
        item=item,
        relacionados=relacionados,
        # El contenido "3" lleva la línea del tiempo incrustada
        es_linea_tiempo=(contenido_id == "3"),
        timeline=data.TIMELINE_EVENTS,
        **{
            "simul_content": data.CONTENT_ITEMS,
            "simul_comments": data.SEED_COMMENTS,
            "simul_reactions": data.SEED_REACTIONS,
        },
        **_common_context()
    )


# ==========================================================
# AUTENTICACIÓN
# ==========================================================

@web_router.get("/login", name="web.login")
def login(request: Request):
    """
    Inicio de sesión (RF-USR-01).

    Ocupa la pantalla completa: no incluye la navbar.
    """
    return renderizar(
        request,
        "pages/login.html",
        roles=data.ROLE_DATA,
        demo_password=data.DEMO_PASSWORD,
        **_common_context()
    )


@web_router.get("/registro", name="web.registro")
def registro(request: Request):
    """
    Creación de cuenta (RF-USR-01).
    """
    return renderizar(
        request,
        "pages/registro.html",
        role_data=data.ROLE_DATA,
        **_common_context()
    )


# ==========================================================
# ESTUDIANTE  (RF-DSH-01 / RF-DSH-02)
# ==========================================================

@web_router.get(
    "/dashboard/estudiante",
    name="web.dashboard_estudiante"
)
def dashboard_estudiante(request: Request):
    """
    Panel del estudiante: nivel, puntos, aportes y acciones.
    """
    aportes = [
        c for c in data.CONTENT_ITEMS
        if "Valentina" in c["author"]
    ]

    # Posición del usuario en el ranking. Se calcula en Python
    # para no dejar lógica de negocio dentro del template.
    ordenados = sorted(
        data.RANKING_DATA,
        key=lambda r: r["points"],
        reverse=True
    )

    posicion = next(
        (
            i for i, fila in enumerate(ordenados, start=1)
            if fila["name"] == data.ROLE_DATA["student"]["name"]
        ),
        None
    )

    return renderizar(
        request,
        "pages/dashboard_estudiante.html",
        aportes=aportes,
        activity=data.STUDENT_ACTIVITY,
        max_points=data.STUDENT_MAX_POINTS,
        ranking=ordenados,
        my_rank=posicion,
        level_names=data.LEVEL_NAMES,
        demo=data.ROLE_DATA["student"],
        **{
            "simul_content": data.CONTENT_ITEMS,
            "simul_reactions": data.SEED_REACTIONS,
        },
        **_common_context()
    )


@web_router.get(
    "/proponer-contenido",
    name="web.proponer_contenido"
)
def proponer_contenido(request: Request):
    """
    Formulario de propuesta de proyecto (RF-PRY-01).
    """
    return renderizar(
        request,
        "pages/proponer_contenido.html",
        teachers=data.TEACHERS,
        categories=data.PROPOSAL_CATEGORIES,
        technologies=data.PROPOSAL_TECHNOLOGIES,
        years=[2024, 2023, 2022, 2021, 2020],
        demo=data.ROLE_DATA["student"],
        **_common_context()
    )


@web_router.get("/mis-aportes", name="web.mis_aportes")
def mis_aportes(request: Request):
    """
    Historial de aportes con el motivo de los rechazos
    (RF-DSH-02 + RNF-SEG-04).
    """
    return renderizar(
        request,
        "pages/mis_aportes.html",
        items=data.MY_ITEMS,
        **_common_context()
    )


@web_router.get("/favoritos", name="web.favoritos")
def favoritos(request: Request):
    """
    Contenido guardado por el usuario (RF-EXP-04).
    """
    semilla = [
        c["id"] for c in data.CONTENT_ITEMS
        if c["status"] == "publicado"
    ][:4]

    return renderizar(
        request,
        "pages/favoritos.html",
        seed_favorites=semilla,
        **{
            "simul_content": data.CONTENT_ITEMS,
            "simul_reactions": data.SEED_REACTIONS,
        },
        **_common_context()
    )


@web_router.get("/ranking", name="web.ranking")
def ranking(request: Request):
    """
    Clasificación de la comunidad por puntos (RF-GAM-04).
    """
    # El prototipo ordena de mayor a menor y recalcula la
    # posición, así que el `rank` guardado no se usa.
    ordenado = []
    for posicion, fila in enumerate(
        sorted(
            data.RANKING_DATA,
            key=lambda r: r["points"],
            reverse=True
        ),
        start=1
    ):
        ordenado.append(dict(fila, rank=posicion))

    return renderizar(
        request,
        "pages/ranking.html",
        ranking=ordenado,
        level_names=data.LEVEL_NAMES,
        demo=data.ROLE_DATA["student"],
        **_common_context()
    )


@web_router.get("/mi-perfil", name="web.perfil")
def perfil(request: Request):
    """
    Perfil del usuario con descripción editable (RF-USR-03).
    """
    return renderizar(
        request,
        "pages/perfil.html",
        demo=data.ROLE_DATA["student"],
        badges_catalog=data.BADGES_CATALOG,
        **_common_context()
    )


# ==========================================================
# DOCENTE  (RF-COM-01 / RF-COM-02)
# ==========================================================

@web_router.get(
    "/dashboard/docente",
    name="web.dashboard_docente"
)
def dashboard_docente(request: Request):
    """
    Panel del docente: contenido registrado, distribución por
    estado y proyectos que asesora.
    """
    contenido = [
        c for c in data.CONTENT_ITEMS
        if "Patiño" in c["author"] or "Patino" in c["author"]
        or "Ruiz" in c["author"]
    ]

    estados = {
        estado: [c for c in contenido if c["status"] == estado]
        for estado in ("publicado", "pendiente", "rechazado")
    }

    return renderizar(
        request,
        "pages/dashboard_docente.html",
        contenido=contenido,
        estados=estados,
        tipos_permitidos=data.TEACHER_CONTENT_TYPES,
        demo=data.ROLE_DATA["teacher"],
        **{
            "simul_content": data.CONTENT_ITEMS,
            "simul_reactions": data.SEED_REACTIONS,
        },
        **_common_context()
    )


@web_router.get(
    "/registrar-contenido",
    name="web.registrar_contenido"
)
def registrar_contenido(request: Request):
    """
    Registro de contenido institucional por parte del docente.
    El formulario cambia según el tipo elegido (RF-COM-02).
    """
    return renderizar(
        request,
        "pages/registrar_contenido.html",
        content_types=data.TEACHER_CONTENT_TYPES,
        forms=data.TEACHER_FORMS,
        demo=data.ROLE_DATA["teacher"],
        **_common_context()
    )


@web_router.get(
    "/adjuntar-evidencias",
    name="web.adjuntar_evidencias"
)
def adjuntar_evidencias(request: Request):
    """
    Carga de evidencias que respaldan el contenido (RNF-ACC-01).
    """
    return renderizar(
        request,
        "pages/adjuntar_evidencias.html",
        icons=data.FILE_ICONS,
        demo=data.ROLE_DATA["teacher"],
        **_common_context()
    )


# ==========================================================
# ADMINISTRADOR  (RF-VAL / RF-DSH)
# ==========================================================

@web_router.get(
    "/dashboard/admin",
    name="web.dashboard_admin"
)
def dashboard_admin(request: Request):
    """
    Panel administrativo con indicadores y gráfico mensual.
    """
    return renderizar(
        request,
        "pages/dashboard_admin.html",
        kpis=data.KPI_DATA,
        monthly=data.MONTHLY_CONTENT,
        months=data.MONTHS_LABELS,
        impact=data.IMPACT_METRICS,
        pendientes=len(data.VALIDATION_QUEUE),
        demo=data.ROLE_DATA["admin"],
        **_common_context()
    )


@web_router.get(
    "/admin/contenido",
    name="web.admin_contenido"
)
def admin_contenido(request: Request):
    """
    Gestión del catálogo completo: ver, despublicar, eliminar.
    """
    return renderizar(
        request,
        "pages/admin_contenido.html",
        **{
            "simul_content": data.CONTENT_ITEMS,
            "simul_reactions": data.SEED_REACTIONS,
        },
        **_common_context()
    )


@web_router.get(
    "/admin/validacion",
    name="web.admin_validacion"
)
def admin_validacion(request: Request):
    """
    Bandeja de validación: aprobar o rechazar con
    observaciones obligatorias (RF-VAL-01 / RF-VAL-03).
    """
    return renderizar(
        request,
        "pages/admin_validacion.html",
        **{
            "simul_queue": data.VALIDATION_QUEUE,
            "simul_content": data.CONTENT_ITEMS,
        },
        **_common_context()
    )


@web_router.get(
    "/admin/publicacion",
    name="web.admin_publicacion"
)
def admin_publicacion(request: Request):
    """
    Confirmación de publicación y acciones automáticas
    ejecutadas (RF-VAL-04).
    """
    return renderizar(
        request,
        "pages/admin_publicacion.html",
        checklist=data.PUBLISH_CHECKLIST,
        demo=data.ROLE_DATA["admin"],
        **_common_context()
    )


@web_router.get(
    "/admin/usuarios",
    name="web.admin_usuarios"
)
def admin_usuarios(request: Request):
    """
    Gestión de cuentas: cambio de rol y activación (RF-USR-05).
    """
    return renderizar(
        request,
        "pages/admin_usuarios.html",
        roles=data.USER_ROLES,
        role_colors=data.ROLE_COLORS,
        **{
            "simul_users": data.SYSTEM_USERS,
            "simul_content": data.CONTENT_ITEMS,
        },
        **_common_context()
    )
