"""
Configuración común de las pruebas del backend SIMUL.

La cadena de conexión se fija ANTES de importar la app,
porque el motor SQLAlchemy se crea al importar
`app.extensions` (ver app/extensions.py). Se usa SQLite en
un directorio temporal: las pruebas no tocan MySQL.

Ejecutar:

    pytest -q
"""

import os
import tempfile
from pathlib import Path

import pytest

# ------------------------------------------------------------
# Base de datos temporal (aislada del repo y de MySQL)
# ------------------------------------------------------------

_DIRECTORIO = Path(tempfile.mkdtemp(prefix="simul_tests_"))

os.environ["DATABASE_URL"] = (
    f"sqlite:///{(_DIRECTORIO / 'simul_test.db').as_posix()}"
)

os.environ["JWT_SECRET_KEY"] = (
    "simul-test-secret-key-con-mas-de-32-caracteres"
)

# Las importaciones van después de fijar el entorno (flake8:
# noqa E402).
from fastapi.testclient import TestClient  # noqa: E402

from app import create_app  # noqa: E402
from app.extensions import db, sesion_bd  # noqa: E402
from app.models.nivel import Nivel  # noqa: E402
from app.models.rol import Rol  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402


# ------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------

PASSWORD = "clave12345"


def crear_usuario(nombre, correo, rol, password=PASSWORD):
    """Inserta un usuario directamente en la BD (bypass del
    registro para preparar escenarios)."""

    with sesion_bd():

        existente = (
            db.session.query(Usuario)
            .filter_by(correo=correo)
            .first()
        )

        if existente:

            return existente.id_usuario

        rol_bd = (
            db.session.query(Rol)
            .filter_by(nombre=rol)
            .first()
        )

        usuario = Usuario(
            nombre=nombre,
            correo=correo,
            id_rol=rol_bd.id_rol,
            id_nivel=1,
            estado=True,
        )

        usuario.set_password(password)

        db.session.add(usuario)

        db.session.flush()

        return usuario.id_usuario


def iniciar_sesion(client, correo, password=PASSWORD):
    """Devuelve el access token de un usuario existente."""

    respuesta = client.post(
        "/api/museo/auth/login",
        json={"correo": correo, "password": password},
    )

    assert respuesta.status_code == 200, respuesta.text

    return respuesta.json()["data"]["access_token"]


def cabeceras(token):
    return {"Authorization": f"Bearer {token}"}


# ------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------

@pytest.fixture(scope="session")
def app():
    """App FastAPI con la BD temporal y los catálogos mínimos
    (roles y niveles) sembrados."""

    aplicacion = create_app()

    with sesion_bd():

        for nombre in (
            "estudiante",
            "docente",
            "admin",
            "egresado",
        ):

            if not db.session.query(Rol).filter_by(
                nombre=nombre
            ).first():

                db.session.add(
                    Rol(nombre=nombre, descripcion=nombre)
                )

        for numero in range(1, 11):

            if not db.session.query(Nivel).filter_by(
                numero=numero
            ).first():

                db.session.add(
                    Nivel(
                        numero=numero,
                        nombre=f"Nivel {numero}",
                        puntos_min=(numero - 1) * 100,
                        puntos_max=numero * 100 - 1,
                    )
                )

    return aplicacion


@pytest.fixture(scope="session")
def client(app):

    with TestClient(app) as cliente:

        yield cliente


@pytest.fixture(scope="session")
def admin_id(client):

    return crear_usuario(
        "Administrador Pruebas",
        "admin@unilibre.edu.co",
        "admin",
    )


@pytest.fixture(scope="session")
def admin_headers(client, admin_id):

    return cabeceras(
        iniciar_sesion(client, "admin@unilibre.edu.co")
    )


@pytest.fixture(scope="session")
def estudiante_id(client):

    return crear_usuario(
        "Estudiante Pruebas",
        "estudiante@unilibre.edu.co",
        "estudiante",
    )


@pytest.fixture(scope="session")
def estudiante_headers(client, estudiante_id):

    return cabeceras(
        iniciar_sesion(client, "estudiante@unilibre.edu.co")
    )
