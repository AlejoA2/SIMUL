"""
=============================================================
SEED DE LA BASE DE DATOS SIMUL
=============================================================
Puebla las 25 tablas del modelo E-R con los datos del
museo (provenientes de app/data/simul_data.py, la misma
fuente que usa el frontend en este corte).

Uso:
    python db/seed.py            # sembrar si está vacía
    python db/seed.py --reset    # borrar y volver a sembrar

La contraseña de TODOS los usuarios de demo es "1234"
(DEMO_PASSWORD), igual que en el prototipo.
=============================================================
"""

import os
import sys
import unicodedata

# Que el script corra desde cualquier carpeta.
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

# Fuera de Docker no hay DATABASE_URL: el seed apunta al
# MySQL del docker-compose (puerto 3307). Hay que fijarlo
# ANTES de importar app, porque el motor se crea al
# importar app.extensions.
os.environ.setdefault(
    "DATABASE_URL",
    "mysql+pymysql://inventory_user:inventory_password"
    "@127.0.0.1:3307/inventory_db"
)

from app.extensions import db, sesion_bd  # noqa: E402

from app.data.simul_data import (  # noqa: E402
    ROLE_DATA,
    DEMO_PASSWORD,
    TEACHERS,
    LEVEL_TABLE,
    BADGES_CATALOG,
    TIMELINE_EVENTS,
    SEED_COMMENTS,
    SEED_REACTIONS,
    SYSTEM_USERS,
    RANKING_DATA,
)

from app.models.rol import Rol  # noqa: E402
from app.models.nivel import Nivel  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402
from app.models.insignia import Insignia  # noqa: E402
from app.models.contenido import Contenido  # noqa: E402
from app.models.contenido_tipos import (  # noqa: E402
    Acontecimiento,
    Premio,
    Proyecto,
    AvanceInvestigacion,
    Evento,
    Noticia,
    HallFama,
)
from app.models.evidencia import Evidencia  # noqa: E402
from app.models.comentario import Comentario  # noqa: E402
from app.models.reaccion import Reaccion  # noqa: E402
from app.models.favorito import Favorito  # noqa: E402
from app.models.notificacion import Notificacion  # noqa: E402
from app.models.validacion_log import ValidacionLog  # noqa: E402
from app.models.historial_puntos import HistorialPuntos  # noqa: E402
from app.models.investigacion import (  # noqa: E402
    GrupoInvestigacion,
    Tecnologia,
)


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://inventory_user:inventory_password"
    "@127.0.0.1:3307/inventory_db"
)

ROL_POR_ETIQUETA = {
    "Estudiante": "estudiante",
    "Egresado": "egresado",
    "Docente": "docente",
    "Administrador": "admin",
}


def normalizar(texto):
    """'Dr. Carlos Patiño' → 'dr. carlos patino' (sin
    acentos) para comparar nombres del mock que difieren
    solo en tildes/ñ entre secciones."""
    descompuesto = unicodedata.normalize("NFKD", texto)
    sin_tildes = "".join(
        c for c in descompuesto
        if not unicodedata.combining(c)
    )
    return sin_tildes.strip().lower()


def nivel_de(puntos):

    """Número de nivel que corresponde a unos puntos."""

    for fila in LEVEL_TABLE:

        if puntos >= fila["puntos_min"]:

            ultimo = fila["numero"] == LEVEL_TABLE[-1]["numero"]

            if puntos <= fila["puntos_max"] or ultimo:

                return fila["numero"]

    return 1


def slug_correo(nombre):

    base = normalizar(nombre)
    base = (
        base.replace("dr.", "")
        .replace("dra.", "")
        .replace("mg.", "")
        .replace("ing.", "")
        .strip()
    )

    partes = [p for p in base.replace("-", " ").split() if p]

    return (
        ".".join(partes) + "@unilibre.edu.co"
    )


# ==========================================================
# RESET (borra solo las tablas del museo)
# ==========================================================

TABLAS_MUSEO = [
    "reaccion",
    "comentario",
    "favorito",
    "notificacion",
    "historial_puntos",
    "evidencia",
    "usuario_insignia",
    "validacion_log",
    "proyecto_integrante",
    "proyecto_tecnologia",
    "premio_hall",
    "avance_investigacion",
    "hall_fama",
    "noticia",
    "evento",
    "proyecto",
    "premio",
    "acontecimiento",
    "contenido",
    "tecnologia",
    "grupo_investigacion",
    "insignia",
    "usuario",
    "nivel",
    "rol",
]


def resetear():

    print("Reseteando tablas del museo...")

    db.session.execute(
        db.text("SET FOREIGN_KEY_CHECKS = 0")
    )

    for tabla in TABLAS_MUSEO:

        db.session.execute(
            db.text(f"TRUNCATE TABLE {tabla}")
        )

    db.session.execute(
        db.text("SET FOREIGN_KEY_CHECKS = 1")
    )

    db.session.commit()


# ==========================================================
# 1. CATÁLOGOS: ROL, NIVEL, INSIGNIA
# ==========================================================

def sembrar_catalogos():

    roles = {}

    for nombre, descripcion in [
        ("estudiante", "Estudiante de la universidad"),
        ("docente", "Docente del programa"),
        ("admin", "Administrador del museo"),
        ("egresado", "Egresado del programa"),
    ]:

        rol = Rol(nombre=nombre, descripcion=descripcion)

        db.session.add(rol)

        roles[nombre] = rol

    db.session.flush()

    niveles = {}

    for fila in LEVEL_TABLE:

        nivel = Nivel(
            numero=fila["numero"],
            nombre=fila["nombre"],
            puntos_min=fila["puntos_min"],
            puntos_max=fila["puntos_max"],
        )

        db.session.add(nivel)

        niveles[fila["numero"]] = nivel

    db.session.flush()

    insignias = {}

    for fila in BADGES_CATALOG:

        insignia = Insignia(
            nombre=fila["name"],
            icono=fila["icon"],
            puntos_requeridos=fila["puntos_requeridos"],
        )

        db.session.add(insignia)

        insignias[fila["name"]] = insignia

    db.session.flush()

    return roles, niveles, insignias


# ==========================================================
# 2. USUARIOS (unifica ROLE_DATA + TEACHERS +
#    SYSTEM_USERS + RANKING_DATA, deduplicando por correo)
# ==========================================================

def sembrar_usuarios(roles, niveles, insignias):

    usuarios = {}

    def crear(nombre, correo, rol_nombre, **kwargs):

        usuario = Usuario(
            nombre=nombre,
            correo=correo,
            id_rol=roles[rol_nombre].id_rol,
            id_nivel=nivel_de(kwargs.get("puntos", 0)),
            foto=kwargs.get("foto"),
            biografia=kwargs.get("biografia"),
            programa_cohorte=kwargs.get("programa_cohorte"),
            estado=kwargs.get("estado", True),
            puntos_total=kwargs.get("puntos", 0),
        )

        usuario.set_password(DEMO_PASSWORD)

        if kwargs.get("fecha"):

            usuario.fecha_registro = kwargs["fecha"]

        db.session.add(usuario)

        usuarios[correo] = usuario

        return usuario

    # ----------------------------------------------------
    # 2a. SYSTEM_USERS (7 cuentas del panel admin)
    # ----------------------------------------------------

    for fila in SYSTEM_USERS:

        crear(
            nombre=fila["name"],
            correo=fila["email"],
            rol_nombre=ROL_POR_ETIQUETA[fila["role"]],
            foto=fila["avatar"],
            estado=fila["active"],
            fecha=fila["joined"],
        )

    db.session.flush()

    # ----------------------------------------------------
    # 2b. Docentes de TEACHERS que falten (deduplicar
    #     c.patino con SYSTEM_USERS)
    # ----------------------------------------------------

    for fila in TEACHERS:

        if fila["email"] in usuarios:

            continue

        crear(
            nombre=fila["name"],
            correo=fila["email"],
            rol_nombre="docente",
            foto=fila["avatar"],
            programa_cohorte=fila["department"],
        )

    # ----------------------------------------------------
    # 2c. RANKING_DATA (deduplicar por NOMBRE normalizado
    #     con SYSTEM_USERS: "Andrés Felipe Ríos" == id 6,
    #     "Dr. Carlos Patiño" == id 3, "Valentina
    #     Moreno" == id 1 — solo cambian acentos/correo)
    # ----------------------------------------------------

    for fila in RANKING_DATA:

        existente = buscar_por_nombre(
            usuarios, fila["name"]
        )

        if existente:

            existente.puntos_total = fila["points"]
            existente.id_nivel = nivel_de(fila["points"])

        else:

            crear(
                nombre=fila["name"],
                correo=slug_correo(fila["name"]),
                rol_nombre="estudiante",
                foto=fila["avatar"],
                puntos=fila["points"],
            )

    # ----------------------------------------------------
    # 2d. Perfiles demo (ROLE_DATA): puntos, nivel,
    #     biografía y avatar reales del prototipo
    # ----------------------------------------------------

    for clave, fila in ROLE_DATA.items():

        usuario = usuarios.get(fila["email"])

        if not usuario:

            continue

        usuario.puntos_total = fila["points"]
        usuario.id_nivel = nivel_de(fila["points"])
        usuario.biografia = fila["description"]
        usuario.foto = fila["avatar"]

    # ----------------------------------------------------
    # 2e. Personas del Hall y candidatos (id_usuario
    #     NOT NULL de hall_fama) + autores externos
    # ----------------------------------------------------

    crear(
        "Mg. Patricia Salcedo",
        "p.salcedo@unilibre.edu.co",
        "docente",
        puntos=0,
    )

    crear(
        "Ing. Camila Vargas",
        "c.vargas@correo.unilibre.edu.co",
        "egresado",
        puntos=0,
    )

    crear(
        "Dr. Alejandro Ospina",
        "a.ospina@correo.unilibre.edu.co",
        "egresado",
        puntos=0,
    )

    # Autores institucionales / equipos externos que
    # aparecen como autor de contenido en el mock.
    for nombre, rol in [
        ("Coordinacion Academica", "docente"),
        ("Centro de Innovacion Digital", "docente"),
        ("Semillero SISTEC", "estudiante"),
        ("Grupo EcoSistemas", "estudiante"),
        ("Equipo CodeBankers", "estudiante"),
        ("Comite SISTEC", "docente"),
        ("Felipe Castro", "estudiante"),
        ("Maria Gonzalez", "estudiante"),
    ]:

        if nombre not in [
            u.nombre for u in usuarios.values()
        ]:

            crear(
                nombre=nombre,
                correo=slug_correo(nombre),
                rol_nombre=rol,
                puntos=0,
            )

    db.session.flush()

    # ----------------------------------------------------
    # 2f. Insignias según la MISMA regla del servicio:
    #     todo insignia con puntos_requeridos <= puntos
    # ----------------------------------------------------

    for usuario in usuarios.values():

        for insignia in insignias.values():

            if (
                insignia.puntos_requeridos
                <= usuario.puntos_total
            ):

                usuario.insignias.append(insignia)

    db.session.flush()

    return usuarios


# ==========================================================
# 3. CONTENIDO + SUBTIPOS + SATELITES
# ==========================================================

def buscar_por_nombre(usuarios, nombre):

    """Coincidencia por nombre normalizado (tolerante a
    acentos: 'Daniel Suarez' encuentra a 'Daniel
    Suárez')."""

    objetivo = normalizar(nombre)

    for usuario in usuarios.values():

        if normalizar(usuario.nombre) == objetivo:

            return usuario

    return None


def por_nombre(usuarios, nombre):

    usuario = buscar_por_nombre(usuarios, nombre)

    if usuario is None:

        raise KeyError(f"Usuario no encontrado: {nombre}")

    return usuario


def crear_contenido(
    usuarios,
    tipo,
    titulo,
    categoria,
    autor_nombre,
    estado,
    anio=None,
    fec_crea=None,
    fec_valid=None,
    validador=None,
    observaciones=None,
    imagen=None,
    docs=None,
    tecnologias=None,
    participantes=None,
    asesor=None,
    subtipo_extra=None,
):

    autor = por_nombre(usuarios, autor_nombre)

    contenido = Contenido(
        tipo=tipo,
        titulo=titulo,
        categoria=categoria,
        id_autor=autor.id_usuario,
        estado=estado,
        observaciones=observaciones,
        fec_crea=(
            fec_crea or "2024-06-01"
        ),
    )

    if fec_valid:

        contenido.fec_valid = fec_valid

    if validador:

        contenido.id_validador = (
            por_nombre(usuarios, validador).id_usuario
        )

    db.session.add(contenido)

    db.session.flush()

    extra = subtipo_extra or {}

    # ----------------------------------------------------
    # SUBTIPO 1:1 (PK compartida)
    # ----------------------------------------------------

    if tipo == "acontecimiento":

        db.session.add(
            Acontecimiento(
                id_contenido=contenido.id_contenido,
                anio=anio,
                descripcion=extra["descripcion"],
            )
        )

    elif tipo == "premio":

        db.session.add(
            Premio(
                id_contenido=contenido.id_contenido,
                anio=anio,
                lugar=extra.get("lugar"),
                descripcion=extra["descripcion"],
            )
        )

    elif tipo == "proyecto":

        proyecto = Proyecto(
            id_contenido=contenido.id_contenido,
            anio=anio,
            linea_invest=extra.get("linea_invest"),
            descripcion=extra["descripcion"],
            resultados_impacto=extra.get(
                "resultados_impacto"
            ),
            id_asesor=(
                por_nombre(usuarios, asesor).id_usuario
                if asesor else None
            ),
        )

        db.session.add(proyecto)

    elif tipo == "avance_investigacion":

        db.session.add(
            AvanceInvestigacion(
                id_contenido=contenido.id_contenido,
                tipo=extra.get(
                    "tipo_avance",
                    "publicacion",
                ),
                anio=anio,
                referencia=extra.get("referencia"),
                id_grupo=extra.get("id_grupo"),
            )
        )

    elif tipo == "evento":

        db.session.add(
            Evento(
                id_contenido=contenido.id_contenido,
                fecha_evento=extra.get(
                    "fecha_evento",
                    f"{anio}-01-01",
                ),
                lugar=extra.get("lugar"),
                objetivo=extra.get("objetivo"),
            )
        )

    elif tipo == "noticia":

        db.session.add(
            Noticia(
                id_contenido=contenido.id_contenido,
                contenido_texto=extra["descripcion"],
                fecha_publicacion=(
                    extra.get("fecha_publicacion")
                    or f"{anio}-01-01"
                ),
            )
        )

    elif tipo == "hall":

        db.session.add(
            HallFama(
                id_contenido=contenido.id_contenido,
                categoria=extra["categoria_hall"],
                biografia=extra["descripcion"],
                id_usuario=por_nombre(
                    usuarios,
                    extra["persona"],
                ).id_usuario,
            )
        )

    # ----------------------------------------------------
    # IMAGEN PRINCIPAL → evidencia tipo foto
    #    (alt_text obligatorio — RNF-ACC-01)
    # ----------------------------------------------------

    if imagen:

        db.session.add(
            Evidencia(
                id_contenido=contenido.id_contenido,
                tipo="foto",
                url_archivo=imagen,
                alt_text=f"Imagen ilustrativa: {titulo}",
            )
        )

    # ----------------------------------------------------
    # DOCUMENTOS → evidencia tipo doc
    # ----------------------------------------------------

    for nombre_doc in docs or []:

        db.session.add(
            Evidencia(
                id_contenido=contenido.id_contenido,
                tipo="doc",
                url_archivo=nombre_doc,
                alt_text=None,
            )
        )

    # ----------------------------------------------------
    # TECNOLOGÍAS (solo proyectos — tabla intermedia)
    # ----------------------------------------------------

    if tipo == "proyecto":

        for nombre_tec in tecnologias or []:

            tecnologia = db.session.query(Tecnologia).filter_by(
                nombre=nombre_tec
            ).first()

            if not tecnologia:

                tecnologia = Tecnologia(
                    nombre=nombre_tec
                )

                db.session.add(tecnologia)

                db.session.flush()

            db.session.execute(
                db.text(
                    "INSERT IGNORE INTO "
                    "proyecto_tecnologia "
                    "(id_proyecto, id_tec) "
                    "VALUES (:p, :t)"
                ),
                {
                    "p": contenido.id_contenido,
                    "t": tecnologia.id_tec,
                },
            )

        # ------------------------------------------------
        # INTEGRANTES (autor + participantes)
        # ------------------------------------------------

        db.session.execute(
            db.text(
                "INSERT IGNORE INTO "
                "proyecto_integrante "
                "(id_proyecto, id_usuario, rol_en_proyecto) "
                "VALUES (:p, :u, 'autor')"
            ),
            {
                "p": contenido.id_contenido,
                "u": autor.id_usuario,
            },
        )

        for nombre_int in participantes or []:

            db.session.execute(
                db.text(
                    "INSERT IGNORE INTO "
                    "proyecto_integrante "
                    "(id_proyecto, id_usuario, "
                    "rol_en_proyecto) "
                    "VALUES (:p, :u, 'participante')"
                ),
                {
                    "p": contenido.id_contenido,
                    "u": por_nombre(
                        usuarios, nombre_int
                    ).id_usuario,
                },
            )

    return contenido


# ==========================================================
# 4. SEMBRADO DEL CONTENIDO (mock → tablas)
# ==========================================================

def sembrar_contenido(usuarios, grupos):

    # ----------------------------------------------------
    # Contenido publicado (1-6, 9-11 del mock + "mis
    # aportes" old1) — nace validado por la admin
    # ----------------------------------------------------

    IMG = "https://images.unsplash.com/photo-{}?w=800&h=500&fit=crop&auto=format"

    creados = {}

    creados["1"] = crear_contenido(
        usuarios,
        tipo="proyecto",
        titulo=(
            "Sistema de Monitoreo Ambiental con IoT "
            "para Campus Universitario"
        ),
        categoria="Proyecto",
        autor_nombre="Valentina Moreno",
        estado="publicado",
        anio=2023,
        fec_crea="2023-11-10",
        fec_valid="2023-11-18",
        validador="Ing. Laura Jimenez",
        imagen=IMG.format("1518770660439-4636190af475"),
        docs=[
            "Informe Final.pdf",
            "Codigo Fuente.zip",
            "Manual de Usuario.pdf",
        ],
        tecnologias=[
            "Arduino", "LoRaWAN", "Node.js",
            "React", "MongoDB",
        ],
        participantes=["Felipe Castro", "Andrea Lopez"],
        asesor="Dr. Carlos Patino",
        subtipo_extra={
            "descripcion": (
                "Plataforma integral de monitoreo en "
                "tiempo real de variables ambientales "
                "(temperatura, humedad, CO2, particulas "
                "PM2.5) distribuida en 24 puntos del "
                "campus mediante sensores IoT conectados "
                "a una red LoRaWAN. Los datos se "
                "procesan en un backend Node.js y se "
                "visualizan en un dashboard React "
                "accesible para toda la comunidad "
                "universitaria."
            ),
            "linea_invest": "Internet de las Cosas",
        },
    )

    creados["2"] = crear_contenido(
        usuarios,
        tipo="premio",
        titulo=(
            "Premio Nacional de Innovacion Tecnologica "
            "- Categoria Software"
        ),
        categoria="Premio",
        autor_nombre="Semillero SISTEC",
        estado="publicado",
        anio=2022,
        fec_crea="2022-10-05",
        fec_valid="2022-10-06",
        validador="Ing. Laura Jimenez",
        imagen=IMG.format("1567427017947-545c5f8d16ad"),
        docs=["Diploma Premio ACIS 2022.pdf"],
        subtipo_extra={
            "lugar": "ACIS",
            "descripcion": (
                "El semillero SISTEC obtuvo el primer "
                "lugar en el Premio Nacional de "
                "Innovacion Tecnologica organizado por "
                'ACIS con el proyecto "Diagnostico '
                'temprano de enfermedades respiratorias '
                'mediante aprendizaje automatico", '
                "compitiendo contra 87 equipos de 34 "
                "universidades del pais."
            ),
        },
    )

    creados["3"] = crear_contenido(
        usuarios,
        tipo="acontecimiento",
        titulo=(
            "Linea del Tiempo - 35 Anos de Historia "
            "del Programa"
        ),
        categoria="Historia",
        autor_nombre="Coordinacion Academica",
        estado="publicado",
        anio=2024,
        fec_crea="2024-01-15",
        fec_valid="2024-01-16",
        validador="Ing. Laura Jimenez",
        imagen=IMG.format("1481627834876-b7833e8f5570"),
        docs=["Resena Historica Completa.pdf"],
        subtipo_extra={
            "descripcion": (
                "Recorrido historico interactivo por "
                "los hitos mas importantes del Programa "
                "de Ingenieria de Sistemas desde su "
                "fundacion en 1989: primeras promociones, "
                "acreditaciones, expansion curricular, "
                "incorporacion de areas como IA y "
                "ciberseguridad, y proyeccion "
                "internacional."
            ),
        },
    )

    creados["4"] = crear_contenido(
        usuarios,
        tipo="evento",
        titulo=(
            "Hackathon Unilibre 2024 - DataDriven "
            "Challenge"
        ),
        categoria="Evento",
        autor_nombre="Centro de Innovacion Digital",
        estado="publicado",
        anio=2024,
        fec_crea="2024-09-25",
        fec_valid="2024-09-26",
        validador="Ing. Laura Jimenez",
        imagen=IMG.format("1504384308090-c894fdcc538d"),
        docs=["Resultados Hackathon 2024.pdf"],
        subtipo_extra={
            "fecha_evento": "2024-10-11",
            "lugar": "Campus Unilibre - Bloque C",
            "objetivo": (
                "72 horas de desarrollo donde 38 "
                "equipos crearon soluciones de analisis "
                "de datos para problematicas reales."
            ),
        },
    )

    creados["5"] = crear_contenido(
        usuarios,
        tipo="avance_investigacion",
        titulo=(
            "Plataforma de Gestion Academica con "
            "Inteligencia Artificial"
        ),
        categoria="Investigacion",
        autor_nombre="Dr. Carlos Patino",
        estado="publicado",
        anio=2023,
        fec_crea="2023-08-20",
        fec_valid="2023-08-22",
        validador="Dr. Carlos Patino",
        imagen=IMG.format("1555949963-aa79dcee981c"),
        docs=[
            "Articulo IEEE LAT.pdf",
            "Dataset Anonimizado.csv",
        ],
        subtipo_extra={
            "tipo_avance": "publicacion",
            "referencia": (
                "IEEE Latin America Transactions"
            ),
            "id_grupo": grupos["DataEd"].id_grupo,
            "descripcion": (
                "Sistema inteligente para prediccion de "
                "desercion estudiantil y recomendacion "
                "personalizada de rutas de "
                "aprendizaje. Publicado en IEEE Latin "
                "America Transactions con factor de "
                "impacto 1.5. El modelo alcanza 89.3% "
                "de precision en identificacion de "
                "riesgo academico."
            ),
        },
    )

    creados["6"] = crear_contenido(
        usuarios,
        tipo="premio",
        titulo=(
            "App Movil para Gestion de Residuos "
            "Solidos - Premio Verde 2021"
        ),
        categoria="Premio",
        autor_nombre="Grupo EcoSistemas",
        estado="publicado",
        anio=2021,
        fec_crea="2021-12-01",
        fec_valid="2021-12-02",
        validador="Ing. Laura Jimenez",
        imagen=IMG.format("1532996122724-e3c354a0b15b"),
        docs=["Diploma Premio Verde 2021.pdf"],
        subtipo_extra={
            "lugar": (
                "Ministerio de Ciencia, Tecnologia e "
                "Innovacion"
            ),
            "descripcion": (
                "Aplicacion multiplataforma ganadora "
                "del Premio Verde 2021. Facilita la "
                "clasificacion, recoleccion y "
                "seguimiento de residuos solidos en 15 "
                "municipios piloto, con +50.000 "
                "descargas en su primer ano."
            ),
        },
    )

    # ----------------------------------------------------
    # 7 y 8: mis aportes de Valentina (el mock los
    # atribuye a ella en MY_ITEMS; aquí se unifica)
    # ----------------------------------------------------

    creados["7"] = crear_contenido(
        usuarios,
        tipo="proyecto",
        titulo=(
            "Propuesta: Sistema Blockchain para "
            "Titulos Academicos"
        ),
        categoria="Proyecto",
        autor_nombre="Valentina Moreno",
        estado="pendiente",
        anio=2024,
        fec_crea="2024-11-15",
        imagen=IMG.format("1639762681057-408e52192e55"),
        tecnologias=[
            "Solidity", "Hardhat", "React", "MetaMask",
        ],
        participantes=["Juan Perez", "Maria Gonzalez"],
        subtipo_extra={
            "descripcion": (
                "Propuesta de sistema descentralizado "
                "para emision y verificacion de "
                "titulos academicos usando smart "
                "contracts en Ethereum, eliminando "
                "fraudes de credenciales."
            ),
        },
    )

    creados["8"] = crear_contenido(
        usuarios,
        tipo="proyecto",
        titulo=(
            "Chatbot de Orientacion para Estudiantes "
            "de Primer Semestre"
        ),
        categoria="Proyecto",
        autor_nombre="Valentina Moreno",
        estado="rechazado",
        anio=2024,
        fec_crea="2024-09-03",
        fec_valid="2024-09-05",
        validador="Ing. Laura Jimenez",
        observaciones=(
            "El proyecto no incluye evidencias "
            "suficientes de pruebas con usuarios "
            "reales. Revisar metricas de evaluacion "
            "del modelo y adjuntar al menos 2 "
            "sesiones de testing documentadas."
        ),
        imagen=IMG.format("1677442136019-21780ecad995"),
        tecnologias=[
            "Python", "LangChain", "OpenAI API",
        ],
        participantes=["Andrea Lopez"],
        subtipo_extra={
            "descripcion": (
                "Asistente conversacional impulsado "
                "por LLM para guiar a estudiantes "
                "nuevos en tramites, horarios y "
                "recursos academicos."
            ),
        },
    )

    # ----------------------------------------------------
    # Hall de la fama (9-11) + "mis aportes" old1
    # ----------------------------------------------------

    creados["9"] = crear_contenido(
        usuarios,
        tipo="hall",
        titulo="Mg. Patricia Salcedo - Fundadora del Programa",
        categoria="Hall de la Fama",
        autor_nombre="Mg. Patricia Salcedo",
        estado="publicado",
        anio=1989,
        fec_crea="2020-03-01",
        fec_valid="2020-03-02",
        validador="Ing. Laura Jimenez",
        imagen=IMG.format("1587614382346-4ec70e388b28"),
        docs=["Trayectoria Patricia Salcedo.pdf"],
        subtipo_extra={
            "categoria_hall": "Docente",
            "persona": "Mg. Patricia Salcedo",
            "descripcion": (
                "Pionera en la fundacion del Programa "
                "de Ingenieria de Sistemas de la "
                "Universidad Libre, dirigio por 12 anos "
                "consecutivos la consolidacion "
                "academica y la primera acreditacion "
                "institucional."
            ),
        },
    )

    creados["10"] = crear_contenido(
        usuarios,
        tipo="hall",
        titulo="Dr. Ricardo Montoya - Investigador Distinguido",
        categoria="Hall de la Fama",
        autor_nombre="Dr. Ricardo Montoya",
        estado="publicado",
        anio=2015,
        fec_crea="2020-03-01",
        fec_valid="2020-03-02",
        validador="Ing. Laura Jimenez",
        imagen=IMG.format("1612349317150-e413f6a5b16d"),
        docs=["Hoja de Vida Dr. Montoya.pdf"],
        subtipo_extra={
            "categoria_hall": "Investigador",
            "persona": "Dr. Ricardo Montoya",
            "descripcion": (
                "Autor de 38 articulos indexados en "
                "WoS/Scopus, creador del laboratorio "
                "de ciberseguridad y mentor de mas de "
                "200 egresados en programas de "
                "maestria y doctorado."
            ),
        },
    )

    creados["11"] = crear_contenido(
        usuarios,
        tipo="hall",
        titulo="Ing. Camila Vargas - Egresada Emprendedora",
        categoria="Hall de la Fama",
        autor_nombre="Ing. Camila Vargas",
        estado="publicado",
        anio=2020,
        fec_crea="2021-05-10",
        fec_valid="2021-05-11",
        validador="Ing. Laura Jimenez",
        imagen=IMG.format("1573497019940-1c28c88b4f3e"),
        docs=["Perfil Camila Vargas.pdf"],
        subtipo_extra={
            "categoria_hall": "Egresado",
            "persona": "Ing. Camila Vargas",
            "descripcion": (
                "Egresada 2014, fundo TechSocial - "
                "startup colombiana de impacto social "
                "con presencia en 8 paises, "
                "reconocida por Forbes Colombia como "
                "una de las 30 menores de 30."
            ),
        },
    )

    creados["old1"] = crear_contenido(
        usuarios,
        tipo="proyecto",
        titulo="App para gestion de notas academicas",
        categoria="Proyecto",
        autor_nombre="Valentina Moreno",
        estado="publicado",
        anio=2023,
        fec_crea="2023-05-20",
        fec_valid="2023-05-25",
        validador="Ing. Laura Jimenez",
        subtipo_extra={
            "descripcion": (
                "Aplicacion movil para el registro y "
                "consulta de notas academicas con "
                "sincronizacion en la nube."
            ),
        },
    )

    # ----------------------------------------------------
    # Bandeja de validación (VALIDATION_QUEUE p1-p5)
    # ----------------------------------------------------

    creados["p1"] = crear_contenido(
        usuarios,
        tipo="proyecto",
        titulo=(
            "Sistema Blockchain para Verificacion de "
            "Titulos Academicos"
        ),
        categoria="Proyecto",
        autor_nombre="Juan Perez",
        estado="pendiente",
        anio=2024,
        fec_crea="2024-11-15",
        imagen=IMG.format("1639762681057-408e52192e55"),
        docs=["Informe.pdf", "Codigo.zip"],
        tecnologias=["Blockchain", "Solidity", "React"],
        subtipo_extra={
            "descripcion": (
                "Sistema descentralizado para emision "
                "y verificacion de diplomas "
                "universitarios mediante smart "
                "contracts en Ethereum. El proyecto "
                "incluye un frontend React y contratos "
                "Solidity desplegados en testnet."
            ),
        },
    )

    creados["p2"] = crear_contenido(
        usuarios,
        tipo="avance_investigacion",
        titulo=(
            "Semillero NLP Lab - Analisis de "
            "Sentimientos en Redes Sociales"
        ),
        categoria="Investigacion",
        autor_nombre="Dra. Ana Ramirez",
        estado="pendiente",
        anio=2024,
        fec_crea="2024-11-12",
        imagen=IMG.format("1677442136019-21780ecad995"),
        docs=["Preprint.pdf"],
        subtipo_extra={
            "tipo_avance": "publicacion",
            "referencia": "Preprint NLP Lab 2024",
            "id_grupo": grupos["NLP Lab"].id_grupo,
            "descripcion": (
                "Avance de investigacion del semillero "
                "NLP Lab sobre clasificacion de "
                "sentimientos en Twitter usando "
                "transformers fine-tuned en espanol. "
                "F1-score de 91.2% en dataset "
                "colombiano."
            ),
        },
    )

    creados["p3"] = crear_contenido(
        usuarios,
        tipo="premio",
        titulo=(
            "Hackathon FinTech 2024 - Primer Lugar"
        ),
        categoria="Premio",
        autor_nombre="Equipo CodeBankers",
        estado="pendiente",
        anio=2024,
        fec_crea="2024-11-08",
        imagen=IMG.format("1567427017947-545c5f8d16ad"),
        docs=["Diploma.pdf", "Presentacion.pdf"],
        subtipo_extra={
            "lugar": "Hackathon FinTech Colombia 2024",
            "descripcion": (
                "El equipo CodeBankers obtuvo el "
                "primer lugar en el Hackathon "
                "FinTech Colombia 2024 con una "
                "solucion de microcreditos basada en "
                "scoring alternativo."
            ),
        },
    )

    creados["p4"] = crear_contenido(
        usuarios,
        tipo="evento",
        titulo=(
            "Congreso SISTEC 2024 - Convocatoria y "
            "Resultados"
        ),
        categoria="Evento",
        autor_nombre="Comite SISTEC",
        estado="pendiente",
        anio=2024,
        fec_crea="2024-11-05",
        imagen=IMG.format("1504384308090-c894fdcc538d"),
        docs=["Memorias.pdf"],
        subtipo_extra={
            "fecha_evento": "2024-11-05",
            "lugar": "Auditorio Mayor Unilibre",
            "objetivo": (
                "El XVIII Congreso Nacional SISTEC "
                "reunio a 320 ponentes de 28 "
                "universidades en lineas de IA, "
                "ciberseguridad, IoT y computacion "
                "en la nube."
            ),
        },
    )

    creados["p5"] = crear_contenido(
        usuarios,
        tipo="hall",
        titulo=(
            "Dr. Alejandro Ospina - Candidato Hall "
            "de la Fama"
        ),
        categoria="Hall de la Fama",
        autor_nombre="Coordinacion Academica",
        estado="pendiente",
        anio=2024,
        fec_crea="2024-11-01",
        imagen=IMG.format("1612349317150-e413f6a5b16d"),
        docs=["Hoja_de_vida.pdf"],
        subtipo_extra={
            "categoria_hall": "Egresado",
            "persona": "Dr. Alejandro Ospina",
            "descripcion": (
                "Candidatura del Dr. Alejandro Ospina, "
                "egresado 1998 y CEO de DataBridge, "
                "firma de analisis de datos con "
                "operaciones en 5 paises "
                "latinoamericanos."
            ),
        },
    )

    # ----------------------------------------------------
    # LÍNEA DEL TIEMPO → contenido tipo acontecimiento
    # ----------------------------------------------------

    for evento_mock in TIMELINE_EVENTS:

        clave = f"tl{evento_mock['year']}"

        creados[clave] = crear_contenido(
            usuarios,
            tipo="acontecimiento",
            titulo=evento_mock["title"],
            categoria="Historia",
            autor_nombre="Coordinacion Academica",
            estado="publicado",
            anio=evento_mock["year"],
            fec_crea=f"{evento_mock['year']}-01-01",
            fec_valid=f"{evento_mock['year']}-01-02",
            validador="Ing. Laura Jimenez",
            subtipo_extra={
                "descripcion": evento_mock["description"],
            },
        )

    db.session.flush()

    return creados


# ==========================================================
# 5. SOCIAL, VALIDACIÓN, GAMIFICACIÓN
# ==========================================================

def sembrar_grupos(usuarios):

    grupos = {}

    for nombre, tipo, lider, descripcion in [
        (
            "SISTEC",
            "semillero",
            "Dr. Ricardo Montoya",
            "Software educativo, ciberseguridad y "
            "tecnologias emergentes.",
        ),
        (
            "DataEd",
            "semillero",
            "Dr. Carlos Patino",
            "Educacion con datos e inteligencia "
            "artificial.",
        ),
        (
            "NLP Lab",
            "semillero",
            "Dra. Ana Ramirez",
            "Procesamiento de lenguaje natural en "
            "espanol.",
        ),
        (
            "EcoSistemas",
            "grupo",
            "Ing. Mariana Torres",
            "Tecnologias para la sostenibilidad "
            "ambiental.",
        ),
    ]:

        grupo = GrupoInvestigacion(
            nombre=nombre,
            tipo=tipo,
            descripcion=descripcion,
            id_lider=por_nombre(
                usuarios, lider
            ).id_usuario,
        )

        db.session.add(grupo)

        grupos[nombre] = grupo

    db.session.flush()

    return grupos


def sembrar_logs_y_notificaciones(usuarios, creados):

    admin = por_nombre(usuarios, "Ing. Laura Jimenez")

    # ----------------------------------------------------
    # VALIDACION_LOG: cada contenido ya decidido deja
    # trazabilidad (RF-SEG-04)
    # ----------------------------------------------------

    for clave, contenido in creados.items():

        if contenido.estado == "pendiente":

            continue

        db.session.add(
            ValidacionLog(
                id_contenido=contenido.id_contenido,
                id_admin=admin.id_usuario,
                accion=(
                    "aprueba"
                    if contenido.estado == "publicado"
                    else "rechaza"
                ),
                observaciones=(
                    contenido.observaciones or ""
                ),
                fecha_decision=(
                    contenido.fec_valid
                    or contenido.fec_crea
                ),
            )
        )

    # ----------------------------------------------------
    # NOTIFICACIONES (STUDENT_ACTIVITY del mock + las
    # generadas por las decisiones)
    # ----------------------------------------------------

    valentina = por_nombre(usuarios, "Valentina Moreno")

    notificaciones = [
        (
            valentina,
            "revision",
            'Tu proyecto "Sistema Blockchain para '
            'Titulos" esta en revision',
            creados["7"],
            False,
            "2024-11-15",
        ),
        (
            valentina,
            "insignia",
            'Ganaste la insignia "Primer Aporte" por '
            "tu contribucion",
            None,
            False,
            "2024-11-12",
        ),
        (
            valentina,
            "comentario",
            'Comentaste en "Plataforma de Gestion '
            'Academica con IA"',
            creados["5"],
            True,
            "2024-11-08",
        ),
        (
            valentina,
            "nivel",
            "Subiste al Nivel 4 - Sigue asi!",
            None,
            True,
            "2024-11-01",
        ),
        (
            valentina,
            "rechazado",
            'El contenido "Chatbot de Orientacion" '
            "fue rechazado. Revisa las observaciones",
            creados["8"],
            True,
            "2024-09-05",
        ),
        (
            por_nombre(usuarios, "Juan Perez"),
            "revision",
            'Tu propuesta "Sistema Blockchain para '
            'Verificacion" entro a la bandeja',
            creados["p1"],
            False,
            "2024-11-15",
        ),
    ]

    for usuario, tipo, mensaje, contenido, leida, fecha in (
        notificaciones
    ):

        db.session.add(
            Notificacion(
                id_usuario=usuario.id_usuario,
                id_contenido=(
                    contenido.id_contenido
                    if contenido else None
                ),
                tipo=tipo,
                mensaje=mensaje,
                leida=leida,
                fecha_envio=fecha,
            )
        )

    # ----------------------------------------------------
    # COMENTARIOS (SEED_COMMENTS + una respuesta)
    # ----------------------------------------------------

    contenido_1 = creados["1"]

    comentarios = []

    for fila in SEED_COMMENTS:

        comentario = Comentario(
            id_contenido=(
                creados[fila["contentId"]].id_contenido
            ),
            id_usuario=por_nombre(
                usuarios, fila["author"]
            ).id_usuario,
            texto=fila["text"],
            fecha="2024-11-10",
        )

        db.session.add(comentario)

        comentarios.append(comentario)

    db.session.flush()

    # Respuesta de la autora al primer comentario.
    db.session.add(
        Comentario(
            id_contenido=contenido_1.id_contenido,
            id_usuario=valentina.id_usuario,
            respuesta_a=comentarios[0].id_coment,
            texto=(
                "Gracias! El codigo fuente estara "
                "disponible en el repositorio del "
                "semillero."
            ),
            fecha="2024-11-11",
        )
    )

    # ----------------------------------------------------
    # REACCIONES: el conteo del mock (12/8/5/3) se
    # materializa como una fila por usuario reaccion
    # ----------------------------------------------------

    activos = [
        u for u in usuarios.values() if u.estado
    ]

    for contenido_clave, info in SEED_REACTIONS.items():

        contenido = creados[contenido_clave]

        for usuario in activos[: info["count"]]:

            db.session.add(
                Reaccion(
                    id_contenido=(
                        contenido.id_contenido
                    ),
                    id_usuario=usuario.id_usuario,
                    tipo_reaccion=info["emoji"],
                )
            )

    # ----------------------------------------------------
    # FAVORITOS
    # ----------------------------------------------------

    favoritos = [
        ("Valentina Moreno", "1"),
        ("Valentina Moreno", "5"),
        ("Valentina Moreno", "9"),
        ("Dr. Carlos Patino", "5"),
        ("Daniel Suarez", "1"),
        ("Daniel Suarez", "2"),
    ]

    for nombre, clave in favoritos:

        db.session.add(
            Favorito(
                id_usuario=por_nombre(
                    usuarios, nombre
                ).id_usuario,
                id_contenido=creados[clave].id_contenido,
            )
        )


def sembrar_historial(usuarios, creados):

    """
    Reparte los puntos de cada usuario en movimientos
    que SUMAN EXACTAMENTE su puntos_total (coherencia
    consultable en DBeaver: SUM(historial) == puntos).
    """

    enlaces = {
        normalizar("Valentina Moreno"): creados["1"],
        normalizar("Dr. Carlos Patino"): creados["5"],
    }

    for usuario in usuarios.values():

        total = usuario.puntos_total

        if total <= 0:

            continue

        if total >= 400:

            partes = [
                (round(total * 0.55), "Aportes publicados"),
                (round(total * 0.30), "Participacion en discusiones"),
            ]

            partes.append(
                (
                    total - partes[0][0] - partes[1][0],
                    "Reconocimientos y actividades",
                )
            )

        else:

            partes = [
                (total, "Aportes y participacion"),
            ]

        vinculado = enlaces.get(
            normalizar(usuario.nombre)
        )

        for indice, (puntos, motivo) in enumerate(partes):

            if puntos <= 0:

                continue

            db.session.add(
                HistorialPuntos(
                    id_usuario=usuario.id_usuario,
                    id_contenido=(
                        vinculado.id_contenido
                        if indice == 0 and vinculado
                        else None
                    ),
                    puntos=puntos,
                    motivo=motivo,
                    fecha="2024-11-10",
                )
            )


def sembrar_premio_hall(creados):

    """N:M premio ↔ hall: el premio ACIS (2) del
    semillero SISTEC vinculado a su investigador
    distinguido (10)."""

    db.session.execute(
        db.text(
            "INSERT IGNORE INTO premio_hall "
            "(id_premio, id_hall) VALUES (:p, :h)"
        ),
        {
            "p": creados["2"].id_contenido,
            "h": creados["10"].id_contenido,
        },
    )


# ==========================================================
# PRINCIPAL
# ==========================================================

def main():

    with sesion_bd():

        hay_datos = (
            db.session.query(Rol).count() > 0
        )

        if "--reset" in sys.argv:

            resetear()

            hay_datos = False

        if hay_datos:

            print(
                "La base ya tiene datos del museo. "
                "Usa 'python db/seed.py --reset' para "
                "volver a sembrar."
            )

            return

        print("Sembrando catálogos (rol, nivel, insignia)...")

        roles, niveles, insignias = sembrar_catalogos()

        print("Sembrando usuarios...")

        usuarios = sembrar_usuarios(
            roles, niveles, insignias
        )

        print("Sembrando grupos de investigación...")

        grupos = sembrar_grupos(usuarios)

        print("Sembrando contenido + subtipos...")

        creados = sembrar_contenido(usuarios, grupos)

        print("Sembrando validación, social y gamificación...")

        sembrar_logs_y_notificaciones(usuarios, creados)

        sembrar_historial(usuarios, creados)

        sembrar_premio_hall(creados)

        db.session.commit()

        # ------------------------------------------------
        # RESUMEN
        # ------------------------------------------------

        print()
        print("=" * 50)
        print("SEED COMPLETADO")
        print("=" * 50)

        from app.models.contenido import Contenido

        print(f"  usuarios ....... {len(usuarios)}")
        print(
            f"  contenido ...... "
            f"{db.session.query(Contenido).count()}"
        )
        print(f"  niveles ........ {len(niveles)}")
        print(f"  insignias ...... {len(insignias)}")
        print(
            "  evidencias ..... "
            f"{db.session.query(Evidencia).count()}"
        )
        print(
            "  comentarios .... "
            f"{db.session.query(Comentario).count()}"
        )
        print(
            "  reacciones ..... "
            f"{db.session.query(Reaccion).count()}"
        )
        print(
            "  favoritos ...... "
            f"{db.session.query(Favorito).count()}"
        )
        print(
            "  notificaciones . "
            f"{db.session.query(Notificacion).count()}"
        )
        print(
            "  validacion_log . "
            f"{db.session.query(ValidacionLog).count()}"
        )
        print(
            "  historial ...... "
            f"{db.session.query(HistorialPuntos).count()}"
        )
        print()
        print(
            "Contraseña de todos los usuarios: "
            f"{DEMO_PASSWORD}"
        )


if __name__ == "__main__":

    main()
