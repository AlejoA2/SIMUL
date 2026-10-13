# ==========================================================
# 1. USUARIOS DE DEMOSTRACIÓN (RF-USR-01 / RF-USR-02)
# ==========================================================

# Los tres perfiles del prototipo. El "password_hash"
# simulado viaja solo en el frontend de este corte; en
# producción NUNCA se manda una contraseña al navegador.
ROLE_DATA = {
    "student": {
        "name": "Valentina Moreno",
        "email": "v.moreno@unilibre.edu.co",
        "role": "student",
        "avatar": (
            "https://images.unsplash.com/photo-1494790108377"
            "-be9c29b29330?w=80&h=80&fit=crop&auto=format"
        ),
        "points": 1240,
        "level": 4,
        "badges": ["Explorador", "Primer Aporte", "Top 10"],
        "description": (
            "Estudiante de Historia apasionada por la cultura "
            "colombiana y el patrimonio arquitectonico."
        ),
    },
    "teacher": {
        "name": "Dr. Carlos Patiño",
        "email": "c.patino@unilibre.edu.co",
        "role": "teacher",
        "avatar": (
            "https://images.unsplash.com/photo-1507003211169"
            "-0a1dd7228f2d?w=80&h=80&fit=crop&auto=format"
        ),
        "points": 3800,
        "level": 8,
        "badges": ["Docente Activo", "Investigador", "Mentor"],
        "description": (
            "Profesor de Historia del Arte con enfoque en "
            "arte colonial latinoamericano."
        ),
    },
    "admin": {
        "name": "Ing. Laura Jiménez",
        "email": "l.jimenez@unilibre.edu.co",
        "role": "admin",
        "avatar": (
            "https://images.unsplash.com/photo-1438761681033"
            "-6461ffad8d80?w=80&h=80&fit=crop&auto=format"
        ),
        "points": 9999,
        "level": 10,
        "badges": ["Administrador", "Fundador", "Leyenda"],
        "description": (
            "Administradora del museo digital SIMUL. "
            "Ingeniera en Sistemas."
        ),
    },
}

# Contraseña única compartida por los tres perfiles de
# demostración (coincide con el prototipo).
DEMO_PASSWORD = "1234"


# ==========================================================
# 2. DOCENTES ASESORES DISPONIBLES (tabla USUARIO)
# ==========================================================

TEACHERS = [
    {
        "id": "t1",
        "name": "Dr. Carlos Patiño",
        "email": "c.patino@unilibre.edu.co",
        "department": "Ingeniería de Sistemas",
        "avatar": (
            "https://images.unsplash.com/photo-1507003211169"
            "-0a1dd7228f2d?w=80&h=80&fit=crop&auto=format"
        ),
    },
    {
        "id": "t2",
        "name": "Mg. Sandra Ruiz",
        "email": "s.ruiz@unilibre.edu.co",
        "department": "Ingeniería de Sistemas",
        "avatar": (
            "https://images.unsplash.com/photo-1580489944761"
            "-15a19d654956?w=80&h=80&fit=crop&auto=format"
        ),
    },
    {
        "id": "t3",
        "name": "Ing. Mariana Torres",
        "email": "m.torres@unilibre.edu.co",
        "department": "Ingeniería de Sistemas",
        "avatar": (
            "https://images.unsplash.com/photo-1573496359142"
            "-b8d87734a5a2?w=80&h=80&fit=crop&auto=format"
        ),
    },
    {
        "id": "t4",
        "name": "Dr. Ricardo Montoya",
        "email": "r.montoya@unilibre.edu.co",
        "department": "Ingeniería de Sistemas",
        "avatar": (
            "https://images.unsplash.com/photo-1560250097"
            "-0b93528c311a?w=80&h=80&fit=crop&auto=format"
        ),
    },
]


# ==========================================================
# 3. GAMIFICACIÓN (RF-GAM-01 / RF-GAM-03)
# ==========================================================

# Catálogo NIVEL de la base de datos. El índice es el
# número de nivel, por eso la lista arranca en la posición 1.
LEVEL_NAMES = {
    0: "",
    1: "Curioso",
    2: "Explorador",
    3: "Colaborador",
    4: "Contribuidor",
    5: "Innovador",
    6: "Investigador",
    7: "Referente",
    8: "Experto",
    9: "Maestro",
    10: "Leyenda",
}

# Puntos objetivo por nivel (columnas puntos_min / puntos_max).
LEVEL_TABLE = [
    {"numero": 1, "nombre": "Curioso", "puntos_min": 0, "puntos_max": 200},
    {"numero": 2, "nombre": "Explorador", "puntos_min": 200, "puntos_max": 500},
    {"numero": 3, "nombre": "Colaborador", "puntos_min": 500, "puntos_max": 900},
    {"numero": 4, "nombre": "Contribuidor", "puntos_min": 900, "puntos_max": 1500},
    {"numero": 5, "nombre": "Innovador", "puntos_min": 1500, "puntos_max": 2200},
    {"numero": 6, "nombre": "Investigador", "puntos_min": 2200, "puntos_max": 3000},
    {"numero": 7, "nombre": "Referente", "puntos_min": 3000, "puntos_max": 3600},
    {"numero": 8, "nombre": "Experto", "puntos_min": 3600, "puntos_max": 4400},
    {"numero": 9, "nombre": "Maestro", "puntos_min": 4400, "puntos_max": 6000},
    {"numero": 10, "nombre": "Leyenda", "puntos_min": 6000, "puntos_max": 9999},
]

RANKING_DATA = [
    {
        "rank": 1,
        "name": "Daniel Suárez",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=60&h=60&fit=crop&auto=format",
        "points": 4820,
        "level": 9,
        "badges": ["🏆", "🔬", "⭐"],
    },
    {
        "rank": 2,
        "name": "Dr. Carlos Patiño",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=60&h=60&fit=crop&auto=format",
        "points": 3800,
        "level": 8,
        "badges": ["🎖️", "🔬", "🏆"],
    },
    {
        "rank": 3,
        "name": "Andrés Felipe Ríos",
        "avatar": "https://images.unsplash.com/photo-1527980965255-d3b416303d12?w=60&h=60&fit=crop&auto=format",
        "points": 3290,
        "level": 8,
        "badges": ["🥉", "💡"],
    },
    {
        "rank": 4,
        "name": "Lorena Castro",
        "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=60&h=60&fit=crop&auto=format",
        "points": 2870,
        "level": 7,
        "badges": ["🎖️", "🚀"],
    },
    {
        "rank": 5,
        "name": "Miguel Herrera",
        "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=60&h=60&fit=crop&auto=format",
        "points": 2340,
        "level": 6,
        "badges": ["⭐", "📝"],
    },
    {
        "rank": 6,
        "name": "Sara Jiménez",
        "avatar": "https://images.unsplash.com/photo-1542596594-649edbc13630?w=60&h=60&fit=crop&auto=format",
        "points": 1980,
        "level": 5,
        "badges": ["🔥"],
    },
    {
        "rank": 7,
        "name": "Camilo Reyes",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=60&h=60&fit=crop&auto=format",
        "points": 1650,
        "level": 5,
        "badges": ["📖"],
    },
    {
        "rank": 8,
        "name": "Natalia Vega",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=60&h=60&fit=crop&auto=format",
        "points": 1420,
        "level": 4,
        "badges": ["🌟"],
    },
    {
        "rank": 9,
        "name": "Valentina Moreno",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=60&h=60&fit=crop&auto=format",
        "points": 1240,
        "level": 4,
        "badges": ["🥈", "📚"],
    },
]

# Insignias disponibles (tabla INSIGNIA).
BADGES_CATALOG = [
    {"icon": "🏆", "name": "Top 10", "puntos_requeridos": 1500},
    {"icon": "🔬", "name": "Investigador", "puntos_requeridos": 2200},
    {"icon": "⭐", "name": "Constancia", "puntos_requeridos": 900},
    {"icon": "📖", "name": "First Aporte", "puntos_requeridos": 200},
    {"icon": "🚀", "name": "Innovador", "puntos_requeridos": 1800},
    {"icon": "🔥", "name": "En racha", "puntos_requeridos": 1100},
    {"icon": "💡", "name": "Idea Brillante", "puntos_requeridos": 800},
    {"icon": "📝", "name": "Docente Activo", "puntos_requeridos": 600},
]


# ==========================================================
# 4. LÍNEA DEL TIEMPO (RF-HIS-01)
# ==========================================================

TIMELINE_EVENTS = [
    {
        "year": 1989,
        "title": "Fundación del Programa",
        "description": (
            "Se funda el Programa de Ingeniería de Sistemas bajo la "
            "dirección de Mg. Patricia Salcedo, con 35 estudiantes en la "
            "primera cohorte."
        ),
        "icon": "🏫",
    },
    {
        "year": 1993,
        "title": "Primera Promoción",
        "description": (
            "Se gradúan los primeros 28 ingenieros de sistemas, marcando "
            "el inicio de una tradición académica que perduraría por décadas."
        ),
        "icon": "🎓",
    },
    {
        "year": 1998,
        "title": "Primera Acreditación",
        "description": (
            "El programa obtiene su primera acreditación institucional por "
            "el CNA, validando la calidad de su propuesta académica."
        ),
        "icon": "✅",
    },
    {
        "year": 2004,
        "title": "Creación del Semillero SISTEC",
        "description": (
            "Se funda el semillero de investigación SISTEC, enfocado en "
            "software educativo y tecnologías emergentes."
        ),
        "icon": "🔬",
    },
    {
        "year": 2008,
        "title": "Expansión Curricular",
        "description": (
            "Se incorporan líneas de investigación en Inteligencia "
            "Artificial y Seguridad Informática al currículo."
        ),
        "icon": "🤖",
    },
    {
        "year": 2012,
        "title": "Primer Programa de Maestría",
        "description": (
            "Se inaugura la Maestría en Ingeniería de Sistemas con "
            "énfasis en Gestión de Tecnologías."
        ),
        "icon": "📚",
    },
    {
        "year": 2015,
        "title": "Laboratorio de Ciberseguridad",
        "description": (
            "Se inaugura el laboratorio especializado, dirigido por "
            "Dr. Ricardo Montoya, con equipamiento de última generación."
        ),
        "icon": "🔒",
    },
    {
        "year": 2018,
        "title": "Acreditación de Alta Calidad",
        "description": (
            "El programa obtiene la acreditación de alta calidad por 8 años, "
            "el máximo reconocimiento del CNA."
        ),
        "icon": "🏆",
    },
    {
        "year": 2020,
        "title": "Virtualización Urgente",
        "description": (
            "Ante la pandemia, el programa transiciona exitosamente a "
            "modalidad virtual, manteniendo la calidad académica."
        ),
        "icon": "💻",
    },
    {
        "year": 2022,
        "title": "Hackathon Unilibre",
        "description": (
            "Se realiza la primera Hackathon con participación internacional "
            "de 7 países latinoamericanos."
        ),
        "icon": "🚀",
    },
    {
        "year": 2024,
        "title": "35 Años de Historia",
        "description": (
            "Celebración de tres décadas y media de formación de ingenieros, "
            "con más de 2,000 egresados activos."
        ),
        "icon": "🎉",
    },
]


# ==========================================================
# 5. CONTENIDO DEL MUSEO (tabla CONTENIDO + subtipos)
# ==========================================================

CONTENT_ITEMS = [
    {
        "id": "1",
        "title": "Sistema de Monitoreo Ambiental con IoT para Campus Universitario",
        "year": 2023,
        "category": "Proyecto",
        "categoryTag": "tag-blue",
        "description": (
            "Plataforma integral de monitoreo en tiempo real de variables "
            "ambientales (temperatura, humedad, CO2, particulas PM2.5) "
            "distribuida en 24 puntos del campus mediante sensores IoT "
            "conectados a una red LoRaWAN. Los datos se procesan en un "
            "backend Node.js y se visualizan en un dashboard React "
            "accesible para toda la comunidad universitaria."
        ),
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&h=500&fit=crop&auto=format",
        "author": "Valentina Moreno, Felipe Castro, Andrea López",
        "tags": ["IoT", "Node.js", "React", "LoRaWAN"],
        "status": "publicado",
        "participants": ["Valentina Moreno", "Felipe Castro", "Andrea López"],
        "technologies": ["Arduino", "LoRaWAN", "Node.js", "React", "MongoDB"],
        "documents": [
            {"name": "Informe Final.pdf", "size": "3.2 MB"},
            {"name": "Codigo Fuente.zip", "size": "12.7 MB"},
            {"name": "Manual de Usuario.pdf", "size": "1.1 MB"},
        ],
        "observations": "",
    },
    {
        "id": "2",
        "title": "Premio Nacional de Innovacion Tecnologica - Categoria Software",
        "year": 2022,
        "category": "Premio",
        "categoryTag": "tag-orange",
        "description": (
            "El semillero SISTEC obtuvo el primer lugar en el Premio Nacional "
            "de Innovacion Tecnologica organizado por ACIS con el proyecto "
            '"Diagnostico temprano de enfermedades respiratorias mediante '
            'aprendizaje automatico", compitiendo contra 87 equipos de 34 '
            "universidades del pais."
        ),
        "image": "https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?w=800&h=500&fit=crop&auto=format",
        "author": "Semillero SISTEC",
        "tags": ["IA", "Machine Learning", "Salud"],
        "status": "publicado",
        "participants": ["Semillero SISTEC", "Dr. Carlos Patino (tutor)"],
        "technologies": ["Python", "TensorFlow", "scikit-learn", "FastAPI"],
        "documents": [{"name": "Diploma Premio ACIS 2022.pdf", "size": "0.8 MB"}],
        "observations": "",
    },
    {
        "id": "3",
        "title": "Linea del Tiempo - 35 Anos de Historia del Programa",
        "year": 2024,
        "category": "Historia",
        "categoryTag": "tag-purple",
        "description": (
            "Recorrido historico interactivo por los hitos mas importantes "
            "del Programa de Ingenieria de Sistemas desde su fundacion en "
            "1989: primeras promociones, acreditaciones, expansion "
            "curricular, incorporacion de areas como IA y ciberseguridad, y "
            "proyeccion internacional."
        ),
        "image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800&h=500&fit=crop&auto=format",
        "author": "Coordinacion Academica",
        "tags": ["Historia", "Institucional", "35 anos"],
        "status": "publicado",
        "participants": ["Coordinacion Academica", "Archivo Historico"],
        "technologies": [],
        "documents": [{"name": "Resena Historica Completa.pdf", "size": "5.4 MB"}],
        "observations": "",
    },
    {
        "id": "4",
        "title": "Hackathon Unilibre 2024 - DataDriven Challenge",
        "year": 2024,
        "category": "Evento",
        "categoryTag": "tag-green",
        "description": (
            "72 horas de intenso desarrollo donde 38 equipos de estudiantes "
            "crearon soluciones de analisis de datos para problematicas "
            "reales de empresas aliadas. Primera edicion presencial-virtual "
            "con participantes de 7 paises latinoamericanos."
        ),
        "image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&h=500&fit=crop&auto=format",
        "author": "Centro de Innovacion Digital",
        "tags": ["Hackathon", "Data Science", "Competencia"],
        "status": "publicado",
        "participants": [
            "38 equipos participantes",
            "Centro de Innovacion Digital",
        ],
        "technologies": ["Python", "R", "Tableau", "Power BI"],
        "documents": [{"name": "Resultados Hackathon 2024.pdf", "size": "2.3 MB"}],
        "observations": "",
    },
    {
        "id": "5",
        "title": "Plataforma de Gestion Academica con Inteligencia Artificial",
        "year": 2023,
        "category": "Investigacion",
        "categoryTag": "tag-red",
        "description": (
            "Sistema inteligente para prediccion de desercion estudiantil y "
            "recomendacion personalizada de rutas de aprendizaje. Publicado "
            "en IEEE Latin America Transactions con factor de impacto 1.5. El "
            "modelo alcanza 89.3% de precision en identificacion de riesgo "
            "academico."
        ),
        "image": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&h=500&fit=crop&auto=format",
        "author": "Dr. Carlos Patino, Mg. Sandra Ruiz",
        "tags": ["IA", "Educacion", "IEEE", "Investigacion"],
        "status": "publicado",
        "participants": ["Dr. Carlos Patino", "Mg. Sandra Ruiz", "Semillero DataEd"],
        "technologies": ["Python", "XGBoost", "FastAPI", "PostgreSQL"],
        "documents": [
            {"name": "Articulo IEEE LAT.pdf", "size": "1.8 MB"},
            {"name": "Dataset Anonimizado.csv", "size": "4.5 MB"},
        ],
        "observations": "",
    },
    {
        "id": "6",
        "title": "App Movil para Gestion de Residuos Solidos - Premio Verde 2021",
        "year": 2021,
        "category": "Premio",
        "categoryTag": "tag-orange",
        "description": (
            "Aplicacion multiplataforma ganadora del Premio Verde 2021 "
            "otorgado por el Ministerio de Ciencia, Tecnologia e "
            "Innovacion. Facilita la clasificacion, recoleccion y "
            "seguimiento de residuos solidos en 15 municipios piloto, con "
            "+50.000 descargas en su primer ano."
        ),
        "image": "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=800&h=500&fit=crop&auto=format",
        "author": "Grupo EcoSistemas",
        "tags": ["Movil", "Sostenibilidad", "Flutter", "Premio"],
        "status": "publicado",
        "participants": ["Grupo EcoSistemas", "Ing. Mariana Torres (tutora)"],
        "technologies": ["Flutter", "Firebase", "Google Maps API"],
        "documents": [{"name": "Diploma Premio Verde 2021.pdf", "size": "0.6 MB"}],
        "observations": "",
    },
    {
        "id": "7",
        "title": "Propuesta: Sistema Blockchain para Titulos Academicos",
        "year": 2024,
        "category": "Proyecto",
        "categoryTag": "tag-blue",
        "description": (
            "Propuesta de sistema descentralizado para emision y verificacion "
            "de titulos academicos usando smart contracts en Ethereum, "
            "eliminando fraudes de credenciales."
        ),
        "image": "https://images.unsplash.com/photo-1639762681057-408e52192e55?w=800&h=500&fit=crop&auto=format",
        "author": "Juan Perez",
        "tags": ["Blockchain", "Ethereum", "Educacion"],
        "status": "pendiente",
        "participants": ["Juan Perez", "Maria Gonzalez"],
        "technologies": ["Solidity", "Hardhat", "React", "MetaMask"],
        "documents": [],
        "observations": "",
    },
    {
        "id": "8",
        "title": "Chatbot de Orientacion para Estudiantes de Primer Semestre",
        "year": 2024,
        "category": "Proyecto",
        "categoryTag": "tag-blue",
        "description": (
            "Asistente conversacional impulsado por LLM para guiar a "
            "estudiantes nuevos en tramites, horarios y recursos academicos."
        ),
        "image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=500&fit=crop&auto=format",
        "author": "Andrea Lopez",
        "tags": ["LLM", "Chatbot", "NLP"],
        "status": "rechazado",
        "participants": ["Andrea Lopez"],
        "technologies": ["Python", "LangChain", "OpenAI API"],
        "documents": [],
        "observations": (
            "El proyecto no incluye evidencias suficientes de pruebas con "
            "usuarios reales. Revisar metricas de evaluacion del modelo y "
            "adjuntar al menos 2 sesiones de testing documentadas."
        ),
    },
    {
        "id": "9",
        "title": "Mg. Patricia Salcedo - Fundadora del Programa",
        "year": 1989,
        "category": "Hall de la Fama",
        "categoryTag": "tag-gold",
        "description": (
            "Pionera en la fundacion del Programa de Ingenieria de Sistemas "
            "de la Universidad Libre, dirigio por 12 anos consecutivos la "
            "consolidacion academica y la primera acreditacion institucional."
        ),
        "image": "https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=800&h=500&fit=crop&auto=format",
        "author": "Mg. Patricia Salcedo",
        "tags": ["Pionera", "Fundadora", "Docente"],
        "status": "publicado",
        "participants": ["Mg. Patricia Salcedo"],
        "technologies": [],
        "documents": [
            {"name": "Trayectoria Patricia Salcedo.pdf", "size": "2.1 MB"}
        ],
        "observations": "",
    },
    {
        "id": "10",
        "title": "Dr. Ricardo Montoya - Investigador Distinguido",
        "year": 2015,
        "category": "Hall de la Fama",
        "categoryTag": "tag-gold",
        "description": (
            "Autor de 38 articulos indexados en WoS/Scopus, creador del "
            "laboratorio de ciberseguridad y mentor de mas de 200 egresados "
            "en programas de maestria y doctorado."
        ),
        "image": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=800&h=500&fit=crop&auto=format",
        "author": "Dr. Ricardo Montoya",
        "tags": ["Investigacion", "Ciberseguridad", "Mentor"],
        "status": "publicado",
        "participants": ["Dr. Ricardo Montoya"],
        "technologies": [],
        "documents": [{"name": "Hoja de Vida Dr. Montoya.pdf", "size": "1.4 MB"}],
        "observations": "",
    },
    {
        "id": "11",
        "title": "Ing. Camila Vargas - Egresada Emprendedora",
        "year": 2020,
        "category": "Hall de la Fama",
        "categoryTag": "tag-gold",
        "description": (
            "Egresada 2014, fundo TechSocial - startup colombiana de impacto "
            "social con presencia en 8 paises, reconocida por Forbes Colombia "
            "como una de las 30 menores de 30."
        ),
        "image": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=800&h=500&fit=crop&auto=format",
        "author": "Ing. Camila Vargas",
        "tags": ["Emprendimiento", "Impacto Social", "Forbes 30"],
        "status": "publicado",
        "participants": ["Ing. Camila Vargas"],
        "technologies": [],
        "documents": [{"name": "Perfil Camila Vargas.pdf", "size": "0.9 MB"}],
        "observations": "",
    },
]


# ==========================================================
# 6. HALL DE LA FAMA (subtipo HALL_FAMA)
# ==========================================================

HALL_OF_FAME = [
    {
        "id": "h1",
        "name": "Mg. Patricia Salcedo",
        "role": "Fundadora del Programa",
        "year": 1989,
        "category": "Docente",
        "description": (
            "Pionera en la fundacion del Programa de Ingenieria de Sistemas "
            "de la Universidad Libre, dirigio por 12 anos consecutivos la "
            "consolidacion academica y la primera acreditacion institucional."
        ),
        "image": "https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=400&h=400&fit=crop&auto=format",
        "achievements": [
            "Fundadora 1989",
            "Primera Acreditacion",
            "12 anos de direccion",
        ],
    },
    {
        "id": "h2",
        "name": "Dr. Ricardo Montoya",
        "role": "Investigador Distinguido",
        "year": 2015,
        "category": "Investigador",
        "description": (
            "Autor de 38 articulos indexados en WoS/Scopus, creador del "
            "laboratorio de ciberseguridad y mentor de mas de 200 egresados "
            "en programas de maestria y doctorado."
        ),
        "image": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400&h=400&fit=crop&auto=format",
        "achievements": [
            "38 articulos Scopus",
            "Lab Ciberseguridad",
            "200+ egresados mentorizados",
        ],
    },
    {
        "id": "h3",
        "name": "Ing. Camila Vargas",
        "role": "Egresada Emprendedora",
        "year": 2020,
        "category": "Egresado",
        "description": (
            "Egresada 2014, fundo TechSocial - startup colombiana de impacto "
            "social con presencia en 8 paises, reconocida por Forbes Colombia "
            "como una de las 30 menores de 30."
        ),
        "image": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=400&h=400&fit=crop&auto=format",
        "achievements": [
            "Forbes 30 under 30",
            "8 paises",
            "TechSocial CEO",
        ],
    },
]


# ==========================================================
# 7. CATEGORÍAS DE EXPLORACIÓN (RF-EXP-01)
# ==========================================================

EXPLORE_CATEGORIES = [
    {
        "id": "historia",
        "label": "Historia",
        "icon": "📜",
        "desc": "Hitos, fundacion y evolucion del programa desde 1989",
        "count": 18,
        "color": "#7C3AED",
    },
    {
        "id": "premios",
        "label": "Premios",
        "icon": "🏆",
        "desc": "Reconocimientos nacionales e internacionales obtenidos",
        "count": 47,
        "color": "#D97706",
    },
    {
        "id": "proyectos",
        "label": "Proyectos",
        "icon": "💡",
        "desc": "Proyectos estudiantiles destacados de grado y semillero",
        "count": 134,
        "color": "#2563EB",
    },
    {
        "id": "investigacion",
        "label": "Investigacion",
        "icon": "🔬",
        "desc": "Publicaciones, semilleros y avances cientificos",
        "count": 62,
        "color": "#DC2626",
    },
    {
        "id": "eventos",
        "label": "Eventos",
        "icon": "📅",
        "desc": "Hackathons, conferencias, simposios y actividades",
        "count": 89,
        "color": "#059669",
    },
    {
        "id": "hall",
        "label": "Hall de la Fama",
        "icon": "⭐",
        "desc": "Docentes, egresados y personas que dejaron huella",
        "count": 24,
        "color": "#C9A84C",
    },
    {
        "id": "galeria",
        "label": "Galeria Historica",
        "icon": "🖼️",
        "desc": "Fotografias y documentos historicos del programa",
        "count": 203,
        "color": "#DB2777",
    },
]

# Traduce el slug de la URL al nombre real de la categoría
# que usa cada elemento de CONTENT_ITEMS.
CATEGORY_SLUG_MAP = {
    "historia": "Historia",
    "premios": "Premio",
    "proyectos": "Proyecto",
    "investigacion": "Investigacion",
    "eventos": "Evento",
    "hall": "Hall de la Fama",
}

# Opciones del filtro lateral en el buscador (RF-EXP-02).
SEARCH_CATEGORIES = [
    "Todos",
    "Historia",
    "Premio",
    "Proyecto",
    "Investigacion",
    "Evento",
    "Hall de la Fama",
]

SEARCH_YEARS = [
    "Todos",
    "2024",
    "2023",
    "2022",
    "2021",
    "2020",
    "2019",
    "Antes de 2019",
]


# ==========================================================
# 8. PORTADA
# ==========================================================

HOME_STATS = [
    {"value": "35+", "label": "Anos de historia"},
    {"value": "4.800+", "label": "Egresados"},
    {"value": "120+", "label": "Premios y reconocimientos"},
    {"value": "340+", "label": "Proyectos registrados"},
]

HOME_QUICK_ACCESS = [
    {
        "title": "Historia del Programa",
        "desc": "35 anos de excelencia academica y hitos institucionales",
        "icon": "📜",
        "cat": "historia",
        "image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=600&h=400&fit=crop&auto=format",
    },
    {
        "title": "Logros y Premios",
        "desc": "Reconocimientos nacionales e internacionales",
        "icon": "🏆",
        "cat": "premios",
        "image": "https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?w=600&h=400&fit=crop&auto=format",
    },
    {
        "title": "Proyectos Destacados",
        "desc": "Innovaciones tecnologicas de nuestros estudiantes",
        "icon": "💡",
        "cat": "proyectos",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&h=400&fit=crop&auto=format",
    },
    {
        "title": "Investigacion",
        "desc": "Semilleros, publicaciones y avances cientificos",
        "icon": "🔬",
        "cat": "investigacion",
        "image": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=600&h=400&fit=crop&auto=format",
    },
    {
        "title": "Eventos",
        "desc": "Hackathons, conferencias y actividades academicas",
        "icon": "📅",
        "cat": "eventos",
        "image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&h=400&fit=crop&auto=format",
    },
    {
        "title": "Hall de la Fama",
        "desc": "Personas que han marcado la historia del programa",
        "icon": "⭐",
        "cat": "hall",
        "image": "https://images.unsplash.com/photo-1532629345422-7515f3d16bb6?w=600&h=400&fit=crop&auto=format",
    },
]

# Imagen de fondo del banner principal.
HOME_HERO_IMAGE = (
    "https://images.unsplash.com/photo-1562774053-701939374585"
    "?w=1440&h=600&fit=crop&auto=format"
)


# ==========================================================
# 9. APORTES DEL ESTUDIANTO (RF-DSH-02)
# ==========================================================

MY_ITEMS = [
    {
        "id": "7",
        "title": "Sistema Blockchain para Titulos Academicos",
        "type": "Proyecto",
        "date": "2024-11-15",
        "status": "pendiente",
        "observations": "",
    },
    {
        "id": "8",
        "title": (
            "Chatbot de Orientacion para Estudiantes de Primer Semestre"
        ),
        "type": "Proyecto",
        "date": "2024-09-03",
        "status": "rechazado",
        "observations": (
            "El proyecto no incluye evidencias suficientes de pruebas con "
            "usuarios reales. Revisar metricas de evaluacion del modelo y "
            "adjuntar al menos 2 sesiones de testing documentadas."
        ),
    },
    {
        "id": "old1",
        "title": "App para gestion de notas academicas",
        "type": "Proyecto",
        "date": "2023-05-20",
        "status": "publicado",
        "observations": "",
    },
]

# Novedades que muestra el dashboard del estudiante (RF-DSH-01).
STUDENT_ACTIVITY = [
    {
        "text": 'Tu proyecto "Sistema Blockchain para Titulos" esta en revision',
        "time": "Hace 2 dias",
        "icon": "⏳",
    },
    {
        "text": 'Ganaste la insignia "Primer Aporte" por tu contribucion',
        "time": "Hace 5 dias",
        "icon": "🏅",
    },
    {
        "text": 'Comentaste en "Plataforma de Gestion Academica con IA"',
        "time": "Hace 1 semana",
        "icon": "💬",
    },
    {
        "text": "Subiste al Nivel 4 - Sigue asi!",
        "time": "Hace 2 semanas",
        "icon": "🎯",
    },
]

# Puntos objetivo del siguiente nivel en el dashboard.
STUDENT_MAX_POINTS = 2000


# ==========================================================
# 10. BANDEJA DE VALIDACIÓN DEL ADMIN (RF-VAL-01)
# ==========================================================

VALIDATION_QUEUE = [
    {
        "id": "p1",
        "title": "Sistema Blockchain para Verificacion de Titulos Academicos",
        "type": "Proyecto",
        "author": "Juan Perez",
        "date": "2024-11-15",
        "image": "https://images.unsplash.com/photo-1639762681057-408e52192e55?w=600&h=400&fit=crop",
        "description": (
            "Sistema descentralizado para emision y verificacion de diplomas "
            "universitarios mediante smart contracts en Ethereum. El "
            "proyecto incluye un frontend React y contratos Solidity "
            "desplegados en testnet."
        ),
        "tags": ["Blockchain", "Solidity", "React"],
        "documents": [
            {"name": "Informe.pdf", "size": "2.1 MB"},
            {"name": "Codigo.zip", "size": "18 MB"},
        ],
    },
    {
        "id": "p2",
        "title": "Semillero NLP Lab - Analisis de Sentimientos en Redes Sociales",
        "type": "Investigacion",
        "author": "Dra. Ana Ramirez",
        "date": "2024-11-12",
        "image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop",
        "description": (
            "Avance de investigacion del semillero NLP Lab sobre clasificacion "
            "de sentimientos en Twitter usando transformers fine-tuned en "
            "espanol. F1-score de 91.2% en dataset colombiano."
        ),
        "tags": ["NLP", "Transformers", "Python"],
        "documents": [{"name": "Preprint.pdf", "size": "1.5 MB"}],
    },
    {
        "id": "p3",
        "title": "Hackathon FinTech 2024 - Primer Lugar",
        "type": "Premio",
        "author": "Equipo CodeBankers",
        "date": "2024-11-08",
        "image": "https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?w=600&h=400&fit=crop",
        "description": (
            "El equipo CodeBankers obtuvo el primer lugar en el Hackathon "
            "FinTech Colombia 2024 con una solucion de microcreditos basada "
            "en scoring alternativo."
        ),
        "tags": ["FinTech", "Hackathon", "ML"],
        "documents": [
            {"name": "Diploma.pdf", "size": "0.4 MB"},
            {"name": "Presentacion.pdf", "size": "5.2 MB"},
        ],
    },
    {
        "id": "p4",
        "title": "Congreso SISTEC 2024 - Convocatoria y Resultados",
        "type": "Evento",
        "author": "Comite SISTEC",
        "date": "2024-11-05",
        "image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&h=400&fit=crop",
        "description": (
            "El XVIII Congreso Nacional SISTEC reunio a 320 ponentes de 28 "
            "universidades. Se presentaron 64 ponencias en las lineas de IA, "
            "ciberseguridad, IoT y computacion en la nube."
        ),
        "tags": ["Congreso", "Evento", "SISTEC"],
        "documents": [{"name": "Memorias.pdf", "size": "9.8 MB"}],
    },
    {
        "id": "p5",
        "title": "Dr. Alejandro Ospina - Candidato Hall de la Fama",
        "type": "Hall de la Fama",
        "author": "Coordinacion Academica",
        "date": "2024-11-01",
        "image": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=600&h=400&fit=crop",
        "description": (
            "Candidatura del Dr. Alejandro Ospina, egresado 1998 y CEO de "
            "DataBridge, firma de analisis de datos con operaciones en 5 "
            "paises latinoamericanos."
        ),
        "tags": ["Hall de la Fama", "Egresado"],
        "documents": [{"name": "Hoja_de_vida.pdf", "size": "1.2 MB"}],
    },
]

# Acciones que se ejecutan al publicar (RF-VAL-04 / RF-DSH).
PUBLISH_CHECKLIST = [
    {"label": "Contenido visible para la comunidad", "done": True},
    {"label": "Actualizacion de linea del tiempo", "done": True},
    {"label": "Notificaciones enviadas a suscriptores", "done": True},
    {"label": "Indicadores de impacto actualizados", "done": True},
    {"label": "Contenido indexado para busqueda", "done": True},
    {"label": "Puntos de gamificacion asignados al autor", "done": True},
]


# ==========================================================
# 11. INDICADORES DEL DASHBOARD ADMIN (RF-DSH-03)
# ==========================================================

KPI_DATA = [
    {"label": "Premios registrados", "value": 47, "icon": "🏆", "color": "#C9A84C", "change": "+3 este mes"},
    {"label": "Proyectos publicados", "value": 134, "icon": "💡", "color": "#2563EB", "change": "+12 este mes"},
    {"label": "Eventos realizados", "value": 89, "icon": "📅", "color": "#059669", "change": "+4 este mes"},
    {"label": "Publicaciones cientificas", "value": 62, "icon": "🔬", "color": "#DC2626", "change": "+2 este mes"},
    {"label": "Hall de la Fama", "value": 24, "icon": "⭐", "color": "#C9A84C", "change": "+1 este mes"},
    {"label": "Usuarios activos", "value": 1842, "icon": "👥", "color": "#7C3AED", "change": "+234 este mes"},
]

MONTHLY_CONTENT = [
    32, 28, 45, 38, 52, 61, 49, 58, 70, 65, 80, 74,
]

MONTHS_LABELS = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]

IMPACT_METRICS = [
    {"label": "Egresados en empresas TOP 100", "value": "68%", "sub": "Colombia 2024"},
    {"label": "Tasa de empleabilidad", "value": "94.3%", "sub": "Dentro de 6 meses"},
    {"label": "Empresas aliadas activas", "value": 127, "sub": "Convenios vigentes"},
    {"label": "Satisfaccion egresados", "value": "4.6/5", "sub": "Encuesta 2024"},
]


# ==========================================================
# 12. GESTIÓN DE USUARIOS (RF-USR-05)
# ============================================================

SYSTEM_USERS = [
    {"id": "1", "name": "Valentina Moreno", "email": "v.moreno@unilibre.edu.co", "role": "Estudiante", "active": True, "joined": "2023-02-14", "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=60&h=60&fit=crop"},
    {"id": "2", "name": "Juan Perez", "email": "j.perez@unilibre.edu.co", "role": "Estudiante", "active": True, "joined": "2022-08-01", "avatar": "https://images.unsplash.com/photo-1527980965255-d3b416303d12?w=60&h=60&fit=crop"},
    {"id": "3", "name": "Dr. Carlos Patino", "email": "c.patino@unilibre.edu.co", "role": "Docente", "active": True, "joined": "2019-01-15", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=60&h=60&fit=crop"},
    {"id": "4", "name": "Dra. Ana Ramirez", "email": "a.ramirez@unilibre.edu.co", "role": "Docente", "active": True, "joined": "2020-03-10", "avatar": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=60&h=60&fit=crop"},
    {"id": "5", "name": "Ing. Laura Jimenez", "email": "l.jimenez@unilibre.edu.co", "role": "Administrador", "active": True, "joined": "2018-06-01", "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=60&h=60&fit=crop"},
    {"id": "6", "name": "Andres Felipe Rios", "email": "a.rios@correo.unilibre.edu.co", "role": "Egresado", "active": True, "joined": "2021-11-20", "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=60&h=60&fit=crop"},
    {"id": "7", "name": "Andrea Lopez", "email": "a.lopez@unilibre.edu.co", "role": "Estudiante", "active": False, "joined": "2023-07-05", "avatar": "https://images.unsplash.com/photo-1542596594-649edbc13630?w=60&h=60&fit=crop"},
]

USER_ROLES = ["Estudiante", "Egresado", "Docente", "Administrador"]

ROLE_COLORS = {
    "Estudiante": "tag-blue",
    "Egresado": "tag-purple",
    "Docente": "tag-orange",
    "Administrador": "tag-red",
}

ROLE_LABELS = {
    "student": "Estudiante",
    "teacher": "Docente",
    "admin": "Administrador",
}


# ==========================================================
# 13. CATÁLOGOS DE LOS FORMULARIOS
# ==========================================================

PROPOSAL_CATEGORIES = [
    "Proyecto de Grado",
    "Semillero de Investigacion",
    "Proyecto Extracurricular",
    "Tesis de Maestria",
]

PROPOSAL_TECHNOLOGIES = [
    "React",
    "Node.js",
    "Python",
    "Flutter",
    "Java",
    "TensorFlow",
    "Arduino",
    "Firebase",
    "PostgreSQL",
    "MongoDB",
]

# Tipos de contenido que el docente puede registrar (RF-COM-02).
TEACHER_CONTENT_TYPES = [
    {
        "id": "historia",
        "label": "Acontecimiento historico",
        "icon": "📜",
        "desc": "Hitos, fechas importantes, fundacion",
    },
    {
        "id": "premio",
        "label": "Premio",
        "icon": "🏆",
        "desc": "Reconocimientos nacionales e internacionales",
    },
    {
        "id": "proyecto",
        "label": "Proyecto",
        "icon": "💡",
        "desc": "Proyectos de investigacion o grado",
    },
    {
        "id": "evento",
        "label": "Evento",
        "icon": "📅",
        "desc": "Congresos, hackathons, simposios",
    },
    {
        "id": "investigacion",
        "label": "Avance de investigacion",
        "icon": "🔬",
        "desc": "Publicaciones, semilleros, resultados",
    },
    {
        "id": "hall",
        "label": "Persona para Hall de la Fama",
        "icon": "⭐",
        "desc": "Docentes, egresados destacados",
    },
]

# Campos dinámicos del formulario docente. El JS elige el
# formulario según el tipo de contenido seleccionado.
TEACHER_FORMS = {
    "premio": [
        {"label": "Nombre del premio *", "placeholder": "Ej: Premio Nacional ACIS 2022"},
        {"label": "Entidad otorgante *", "placeholder": "Ej: ACIS"},
        {"label": "Ano *", "type": "number", "placeholder": "2024"},
        {"label": "Categoria", "placeholder": "Ej: Innovacion en Software"},
        {"label": "Equipo / Persona galardonada *", "placeholder": "Nombre completo o del equipo"},
        {"label": "Descripcion *", "type": "textarea", "placeholder": "Describe el logro, el proceso de seleccion y su impacto..."},
    ],
    "hall": [
        {"label": "Nombre completo *", "placeholder": "Ej: Dr. Ricardo Montoya"},
        {"label": "Cargo / Rol en el programa *", "placeholder": "Ej: Docente investigador"},
        {"label": "Ano de ingreso al Hall *", "type": "number", "placeholder": "2024"},
        {"label": "Correo electronico", "type": "email", "placeholder": "correo@unilibre.edu.co"},
        {"label": "Principales logros *", "type": "textarea", "placeholder": "Logros, publicaciones, empresas fundadas..."},
        {"label": "Vinculo con la Universidad Libre *", "placeholder": "Egresado 2005, Docente desde 2010..."},
    ],
    "proyecto": [
        {"label": "Nombre del proyecto *", "placeholder": "Titulo descriptivo del proyecto"},
        {"label": "Ano *", "type": "number", "placeholder": "2024"},
        {"label": "Integrantes *", "placeholder": "Nombres separados por coma"},
        {"label": "Tecnologias utilizadas", "placeholder": "Python, React, Arduino..."},
        {"label": "Descripcion *", "type": "textarea", "placeholder": "Problema, metodologia, resultados..."},
    ],
    "default": [
        {"label": "Titulo *", "placeholder": "Titulo del contenido"},
        {"label": "Ano *", "type": "number", "placeholder": "2024"},
        {"label": "Responsable *", "placeholder": "Persona o equipo responsable"},
        {"label": "Descripcion *", "type": "textarea", "placeholder": "Descripcion detallada del contenido..."},
    ],
}


# ==========================================================
# 14. COMENTARIOS INICIALES (tabla COMENTARIO)
# ==========================================================

SEED_COMMENTS = [
    {
        "id": 1,
        "contentId": "1",
        "author": "Daniel Suarez",
        "text": "Excelente proyecto, muy bien documentado.",
        "time": "Hace 2 dias",
        "parentId": None,
    },
    {
        "id": 2,
        "contentId": "1",
        "author": "Lorena Castro",
        "text": "Inspirador para nuestro semillero. Comparten el codigo?",
        "time": "Hace 5 dias",
        "parentId": None,
    },
]

# Reacciones iniciales (tabla REACCION) por contenido.
SEED_REACTIONS = {
    "1": {"emoji": "👏", "count": 12, "reacted": False},
    "2": {"emoji": "🔥", "count": 8, "reacted": False},
    "3": {"emoji": "💡", "count": 5, "reacted": False},
    "4": {"emoji": "⭐", "count": 3, "reacted": False},
}

# Íconos por extensión de archivo en el gestor de evidencias.
FILE_ICONS = {
    "pdf": "📄",
    "zip": "📦",
    "png": "🖼️",
    "jpg": "🖼️",
    "jpeg": "🖼️",
    "mp4": "🎬",
    "doc": "📝",
    "docx": "📝",
    "ppt": "📊",
    "pptx": "📊",
}
