"""
=============================================================
RUTAS WEB - Museo Digital Interactivo (SIMUL)
=============================================================

Solo vistas HTML. La API REST del profesor (auth_bp y
product_bp) sigue intacta y convive con este blueprint.

Nota sobre los datos
--------------------
Este corte es frontend: todavía no hay base de datos
conectada, así que cada vista lee de `app/data/simul_data.py`
y entrega además el mismo JSON a la página mediante
`tojson`. Cuando se conecte MySQL se sustituye el
`import` por llamadas a `app/repositories` y el resto del
proyecto no cambia.

Las páginas privadas (dashboards, administración) no se
protegen en el servidor porque la sesión vive en
localStorage; la guarda real la aplica `guardPage()` en
app/static/js/app.js. Al migrar a JWT el token viaja en la
petición y la comprobación pasa a un decorador.
=============================================================
"""

from flask import (
    Blueprint,
    render_template,
    request
)

from app.data import simul_data as data


web_bp = Blueprint(
    "web",
    __name__
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

@web_bp.get("/")
def index():
    """
    Portada del museo: banner, acceso rápido por categoría,
    adelanto del Hall de la Fama y llamada a iniciar sesión.
    """
    return render_template(
        "pages/index.html",
        stats=data.HOME_STATS,
        quick_access=data.HOME_QUICK_ACCESS,
        hall_preview=data.HALL_OF_FAME,
        hero_image=data.HOME_HERO_IMAGE,
        **_common_context()
    )


@web_bp.get("/explorar")
def explorar():
    """
    Catálogo de categorías del museo (RF-EXP-01).
    """
    return render_template(
        "pages/explorar.html",
        categories=data.EXPLORE_CATEGORIES,
        selected_cat=request.args.get("cat"),
        **_common_context()
    )


@web_bp.get("/buscar")
def buscar():
    """
    Buscador con filtros por texto, categoría y año
    (RF-EXP-02). El filtrado ocurre en el navegador.
    """
    return render_template(
        "pages/buscar.html",
        categories=data.SEARCH_CATEGORIES,
        years=data.SEARCH_YEARS,
        selected_cat=request.args.get("cat"),
        initial_query=request.args.get("q", ""),
        **{
            "simul_content": data.CONTENT_ITEMS,
            "category_slug_map": data.CATEGORY_SLUG_MAP,
        },
        **_common_context()
    )


@web_bp.get("/contenido/<contenido_id>")
def detalle_contenido(contenido_id):
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
        return render_template(
            "pages/contenido_no_encontrado.html",
            contenido_id=contenido_id,
            **_common_context()
        ), 404

    relacionados = [
        c for c in data.CONTENT_ITEMS
        if c["id"] != contenido_id and c["status"] == "publicado"
    ][:3]

    return render_template(
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

@web_bp.get("/login")
def login():
    """
    Inicio de sesión (RF-USR-01).

    Ocupa la pantalla completa: no incluye la navbar.
    """
    return render_template(
        "pages/login.html",
        roles=data.ROLE_DATA,
        demo_password=data.DEMO_PASSWORD,
        **_common_context()
    )


@web_bp.get("/registro")
def registro():
    """
    Creación de cuenta (RF-USR-01).
    """
    return render_template(
        "pages/registro.html",
        role_data=data.ROLE_DATA,
        **_common_context()
    )


# ==========================================================
# ESTUDIANTE  (RF-DSH-01 / RF-DSH-02)
# ==========================================================

@web_bp.get("/dashboard/estudiante")
def dashboard_estudiante():
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

    return render_template(
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


@web_bp.get("/proponer-contenido")
def proponer_contenido():
    """
    Formulario de propuesta de proyecto (RF-PRY-01).
    """
    return render_template(
        "pages/proponer_contenido.html",
        teachers=data.TEACHERS,
        categories=data.PROPOSAL_CATEGORIES,
        technologies=data.PROPOSAL_TECHNOLOGIES,
        years=[2024, 2023, 2022, 2021, 2020],
        demo=data.ROLE_DATA["student"],
        **_common_context()
    )


@web_bp.get("/mis-aportes")
def mis_aportes():
    """
    Historial de aportes con el motivo de los rechazos
    (RF-DSH-02 + RNF-SEG-04).
    """
    return render_template(
        "pages/mis_aportes.html",
        items=data.MY_ITEMS,
        **_common_context()
    )


@web_bp.get("/favoritos")
def favoritos():
    """
    Contenido guardado por el usuario (RF-EXP-04).
    """
    semilla = [
        c["id"] for c in data.CONTENT_ITEMS
        if c["status"] == "publicado"
    ][:4]

    return render_template(
        "pages/favoritos.html",
        seed_favorites=semilla,
        **{
            "simul_content": data.CONTENT_ITEMS,
            "simul_reactions": data.SEED_REACTIONS,
        },
        **_common_context()
    )


@web_bp.get("/ranking")
def ranking():
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

    return render_template(
        "pages/ranking.html",
        ranking=ordenado,
        level_names=data.LEVEL_NAMES,
        demo=data.ROLE_DATA["student"],
        **_common_context()
    )


@web_bp.get("/mi-perfil")
def perfil():
    """
    Perfil del usuario con descripción editable (RF-USR-03).
    """
    return render_template(
        "pages/perfil.html",
        demo=data.ROLE_DATA["student"],
        badges_catalog=data.BADGES_CATALOG,
        **_common_context()
    )


# ==========================================================
# DOCENTE  (RF-COM-01 / RF-COM-02)
# ==========================================================

@web_bp.get("/dashboard/docente")
def dashboard_docente():
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

    return render_template(
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


@web_bp.get("/registrar-contenido")
def registrar_contenido():
    """
    Registro de contenido institucional por parte del docente.
    El formulario cambia según el tipo elegido (RF-COM-02).
    """
    return render_template(
        "pages/registrar_contenido.html",
        content_types=data.TEACHER_CONTENT_TYPES,
        forms=data.TEACHER_FORMS,
        demo=data.ROLE_DATA["teacher"],
        **_common_context()
    )


@web_bp.get("/adjuntar-evidencias")
def adjuntar_evidencias():
    """
    Carga de evidencias que respaldan el contenido (RNF-ACC-01).
    """
    return render_template(
        "pages/adjuntar_evidencias.html",
        icons=data.FILE_ICONS,
        demo=data.ROLE_DATA["teacher"],
        **_common_context()
    )


# ==========================================================
# ADMINISTRADOR  (RF-VAL / RF-DSH)
# ==========================================================

@web_bp.get("/dashboard/admin")
def dashboard_admin():
    """
    Panel administrativo con indicadores y gráfico mensual.
    """
    return render_template(
        "pages/dashboard_admin.html",
        kpis=data.KPI_DATA,
        monthly=data.MONTHLY_CONTENT,
        months=data.MONTHS_LABELS,
        impact=data.IMPACT_METRICS,
        pendientes=len(data.VALIDATION_QUEUE),
        demo=data.ROLE_DATA["admin"],
        **_common_context()
    )


@web_bp.get("/admin/contenido")
def admin_contenido():
    """
    Gestión del catálogo completo: ver, despublicar, eliminar.
    """
    return render_template(
        "pages/admin_contenido.html",
        **{
            "simul_content": data.CONTENT_ITEMS,
            "simul_reactions": data.SEED_REACTIONS,
        },
        **_common_context()
    )


@web_bp.get("/admin/validacion")
def admin_validacion():
    """
    Bandeja de validación: aprobar o rechazar con
    observaciones obligatorias (RF-VAL-01 / RF-VAL-03).
    """
    return render_template(
        "pages/admin_validacion.html",
        **{
            "simul_queue": data.VALIDATION_QUEUE,
            "simul_content": data.CONTENT_ITEMS,
        },
        **_common_context()
    )


@web_bp.get("/admin/publicacion")
def admin_publicacion():
    """
    Confirmación de publicación y acciones automáticas
    ejecutadas (RF-VAL-04).
    """
    return render_template(
        "pages/admin_publicacion.html",
        checklist=data.PUBLISH_CHECKLIST,
        demo=data.ROLE_DATA["admin"],
        **_common_context()
    )


@web_bp.get("/admin/usuarios")
def admin_usuarios():
    """
    Gestión de cuentas: cambio de rol y activación (RF-USR-05).
    """
    return render_template(
        "pages/admin_usuarios.html",
        roles=data.USER_ROLES,
        role_colors=data.ROLE_COLORS,
        **{
            "simul_users": data.SYSTEM_USERS,
            "simul_content": data.CONTENT_ITEMS,
        },
        **_common_context()
    )
