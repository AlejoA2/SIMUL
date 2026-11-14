"""
Pruebas del backend SIMUL (FastAPI + SQLAlchemy + SQLite).

Cubren los criterios del tercer corte:
- documentación OpenAPI (/docs, /redoc),
- API REST con CRUD y códigos HTTP correctos,
- validaciones (422) y seguridad (401/403, roles),
- flujo de validación con gamificación.

Se ejecutan sin MySQL: ver tests/conftest.py.
"""

from tests.conftest import cabeceras


# ============================================================
# 1. DOCUMENTACIÓN / ARQUITECTURA
# ============================================================

def test_documentacion_openapi(client):

    assert client.get("/docs").status_code == 200

    assert client.get("/redoc").status_code == 200

    esquema = client.get("/openapi.json").json()

    rutas = esquema["paths"]

    for ruta in (
        "/api/museo/auth/login",
        "/api/museo/auth/register",
        "/api/museo/contenido/",
        "/api/museo/validacion/bandeja",
        "/api/museo/gamificacion/ranking",
        "/api/museo/admin/usuarios",
    ):

        assert ruta in rutas, f"Falta {ruta} en OpenAPI"


def test_paginas_html(client):

    assert client.get("/").status_code == 200

    assert client.get("/login").status_code == 200

    assert client.get("/explorar").status_code == 200


# ============================================================
# 2. AUTENTICACIÓN (RF-USR-01)
# ============================================================

def test_registro_login_y_perfil(client):

    correo = "nuevo.estudiante@unilibre.edu.co"

    respuesta = client.post(
        "/api/museo/auth/register",
        json={
            "nombre": "Nuevo Estudiante",
            "correo": correo,
            "password": "clave12345",
        },
    )

    assert respuesta.status_code == 201, respuesta.text

    assert respuesta.json()["success"] is True

    # La contraseña NUNCA viaja ni se expone.
    assert "password" not in respuesta.text

    respuesta = client.post(
        "/api/museo/auth/login",
        json={"correo": correo, "password": "clave12345"},
    )

    assert respuesta.status_code == 200

    token = respuesta.json()["data"]["access_token"]

    respuesta = client.get(
        "/api/museo/auth/me",
        headers=cabeceras(token),
    )

    assert respuesta.status_code == 200

    perfil = respuesta.json()["data"]

    assert perfil["correo"] == correo

    assert perfil["rol"] == "estudiante"

    assert "password_hash" not in respuesta.text


def test_registro_correo_duplicado(client):

    payload = {
        "nombre": "Duplicado Uno",
        "correo": "duplicado@unilibre.edu.co",
        "password": "clave12345",
    }

    assert client.post(
        "/api/museo/auth/register", json=payload
    ).status_code == 201

    respuesta = client.post(
        "/api/museo/auth/register", json=payload
    )

    assert respuesta.status_code == 409


def test_registro_password_corta(client):

    respuesta = client.post(
        "/api/museo/auth/register",
        json={
            "nombre": "Corto Clave",
            "correo": "corta@unilibre.edu.co",
            "password": "123",
        },
    )

    assert respuesta.status_code == 422

    cuerpo = respuesta.json()

    assert cuerpo["success"] is False

    assert "password" in cuerpo["details"]


def test_login_credenciales_invalidas(client):

    respuesta = client.post(
        "/api/museo/auth/login",
        json={
            "correo": "nadie@unilibre.edu.co",
            "password": "clave12345",
        },
    )

    assert respuesta.status_code == 401


def test_endpoint_protegido_sin_token(client):

    assert client.get(
        "/api/museo/auth/me"
    ).status_code == 401

    assert client.post(
        "/api/museo/contenido/",
        json={},
    ).status_code == 401


# ============================================================
# 3. CRUD DE CONTENIDO (RF-CON)
# ============================================================

def _crear_contenido(client, headers, titulo):

    respuesta = client.post(
        "/api/museo/contenido/",
        headers=headers,
        json={
            "titulo": titulo,
            "tipo": "proyecto",
            "categoria": "Proyectos",
            "anio": 2024,
            "descripcion": "Descripción de prueba del proyecto.",
        },
    )

    assert respuesta.status_code == 201, respuesta.text

    return respuesta.json()["data"]["id_contenido"]


def test_crud_contenido(
    client,
    estudiante_headers,
    admin_headers,
):

    contenido_id = _crear_contenido(
        client,
        estudiante_headers,
        "Proyecto CRUD de prueba",
    )

    # Todo contenido nace pendiente.
    listado = client.get("/api/museo/contenido/")

    assert listado.status_code == 200

    ids_publicos = [
        item["id_contenido"]
        for item in listado.json()["data"]["items"]
    ]

    assert contenido_id not in ids_publicos

    # PUT (actualización completa) por el autor.
    respuesta = client.put(
        f"/api/museo/contenido/{contenido_id}",
        headers=estudiante_headers,
        json={
            "titulo": "Proyecto CRUD editado",
            "categoria": "Investigación",
            "descripcion": "Descripción actualizada del proyecto.",
            "anio": 2025,
        },
    )

    assert respuesta.status_code == 200, respuesta.text

    # PATCH (actualización parcial) por el autor.
    respuesta = client.patch(
        f"/api/museo/contenido/{contenido_id}",
        headers=estudiante_headers,
        json={"titulo": "Proyecto CRUD parcheado"},
    )

    assert respuesta.status_code == 200, respuesta.text

    # El admin aprueba → pasa a publicado.
    respuesta = client.post(
        f"/api/museo/validacion/{contenido_id}/aprobar",
        headers=admin_headers,
        json={"observaciones": "Cumple los criterios"},
    )

    assert respuesta.status_code == 200, respuesta.text

    # Ahora sí es visible públicamente.
    respuesta = client.get(
        f"/api/museo/contenido/{contenido_id}"
    )

    assert respuesta.status_code == 200

    assert respuesta.json()["data"]["estado"] == "publicado"

    # El estudiante NO puede eliminar (solo admin).
    respuesta = client.delete(
        f"/api/museo/contenido/{contenido_id}",
        headers=estudiante_headers,
    )

    assert respuesta.status_code == 403

    # El admin sí elimina.
    respuesta = client.delete(
        f"/api/museo/contenido/{contenido_id}",
        headers=admin_headers,
    )

    assert respuesta.status_code == 200, respuesta.text

    assert client.get(
        f"/api/museo/contenido/{contenido_id}"
    ).status_code == 404


def test_contenido_no_encontrado(client):

    assert client.get(
        "/api/museo/contenido/999999"
    ).status_code == 404


def test_contenido_validacion_de_campos(
    client,
    estudiante_headers,
):

    respuesta = client.post(
        "/api/museo/contenido/",
        headers=estudiante_headers,
        json={
            "titulo": "ab",
            "tipo": "inexistente",
            "categoria": "x",
            "anio": 1800,
            "descripcion": "corta",
        },
    )

    assert respuesta.status_code == 422

    detalles = respuesta.json()["details"]

    for campo in ("titulo", "tipo", "categoria", "anio", "descripcion"):

        assert campo in detalles


# ============================================================
# 4. VALIDACIÓN Y ROLES (RF-VAL / RNF-SEG)
# ============================================================

def test_bandeja_solo_admin(client, estudiante_headers, admin_headers):

    assert client.get(
        "/api/museo/validacion/bandeja",
        headers=estudiante_headers,
    ).status_code == 403

    assert client.get(
        "/api/museo/validacion/bandeja",
        headers=admin_headers,
    ).status_code == 200


def test_rechazo_exige_motivo(client, estudiante_headers, admin_headers):

    contenido_id = _crear_contenido(
        client,
        estudiante_headers,
        "Proyecto para rechazo",
    )

    # Sin cuerpo → 422 (campo obligatorio).
    respuesta = client.post(
        f"/api/museo/validacion/{contenido_id}/rechazar",
        headers=admin_headers,
        json={},
    )

    assert respuesta.status_code == 422, respuesta.text

    # Motivo demasiado corto → 422.
    respuesta = client.post(
        f"/api/museo/validacion/{contenido_id}/rechazar",
        headers=admin_headers,
        json={"observaciones": "no"},
    )

    assert respuesta.status_code == 422

    # Motivo válido → 200 y queda rechazado.
    respuesta = client.post(
        f"/api/museo/validacion/{contenido_id}/rechazar",
        headers=admin_headers,
        json={"observaciones": "Falta la evidencia fotográfica"},
    )

    assert respuesta.status_code == 200, respuesta.text

    assert respuesta.json()["data"]["estado"] == "rechazado"


def test_historial_validacion_solo_admin(
    client,
    estudiante_headers,
    admin_headers,
):

    assert client.get(
        "/api/museo/validacion/1/historial",
        headers=estudiante_headers,
    ).status_code == 403

    assert client.get(
        "/api/museo/validacion/1/historial",
        headers=admin_headers,
    ).status_code == 200


def test_admin_usuarios_solo_admin(
    client,
    estudiante_headers,
    admin_headers,
):

    assert client.get(
        "/api/museo/admin/usuarios",
        headers=estudiante_headers,
    ).status_code == 403

    respuesta = client.get(
        "/api/museo/admin/usuarios",
        headers=admin_headers,
    )

    assert respuesta.status_code == 200

    assert isinstance(respuesta.json()["data"], list)

    assert client.get(
        "/api/museo/admin/kpis",
        headers=admin_headers,
    ).status_code == 200


def test_historial_gamificacion_privado(
    client,
    estudiante_headers,
    estudiante_id,
    admin_id,
):

    # Sin token → 401.
    assert client.get(
        f"/api/museo/gamificacion/historial/{estudiante_id}"
    ).status_code == 401

    # Otro usuario → 403.
    assert client.get(
        f"/api/museo/gamificacion/historial/{admin_id}",
        headers=estudiante_headers,
    ).status_code == 403

    # El propio usuario → 200.
    assert client.get(
        f"/api/museo/gamificacion/historial/{estudiante_id}",
        headers=estudiante_headers,
    ).status_code == 200


# ============================================================
# 5. GAMIFICACIÓN Y SOCIAL
# ============================================================

def test_aprobar_suma_puntos_y_publica(
    client,
    estudiante_headers,
    admin_headers,
):

    contenido_id = _crear_contenido(
        client,
        estudiante_headers,
        "Proyecto con puntos",
    )

    antes = client.get(
        "/api/museo/auth/me",
        headers=estudiante_headers,
    ).json()["data"]["puntos_total"]

    assert client.post(
        f"/api/museo/validacion/{contenido_id}/aprobar",
        headers=admin_headers,
        json={"observaciones": "Aprobado"},
    ).status_code == 200

    despues = client.get(
        "/api/museo/auth/me",
        headers=estudiante_headers,
    ).json()["data"]["puntos_total"]

    assert despues == antes + 100


def test_comentario_reaccion_favorito(
    client,
    estudiante_headers,
    admin_headers,
):

    contenido_id = _crear_contenido(
        client,
        estudiante_headers,
        "Proyecto social",
    )

    assert client.post(
        f"/api/museo/validacion/{contenido_id}/aprobar",
        headers=admin_headers,
        json={"observaciones": "Aprobado"},
    ).status_code == 200

    respuesta = client.post(
        f"/api/museo/contenido/{contenido_id}/comentarios",
        headers=estudiante_headers,
        json={"texto": "Excelente proyecto"},
    )

    assert respuesta.status_code == 201, respuesta.text

    assert client.get(
        f"/api/museo/contenido/{contenido_id}/comentarios"
    ).status_code == 200

    assert client.post(
        f"/api/museo/contenido/{contenido_id}/reaccion",
        headers=estudiante_headers,
        json={"tipo_reaccion": "like"},
    ).status_code in (200, 201)

    assert client.post(
        f"/api/museo/contenido/{contenido_id}/favorito",
        headers=estudiante_headers,
    ).status_code in (200, 201)

    assert client.get(
        "/api/museo/contenido/favoritos",
        headers=estudiante_headers,
    ).status_code == 200


def test_ranking_y_catalogos(client):

    assert client.get(
        "/api/museo/gamificacion/ranking"
    ).status_code == 200

    assert client.get(
        "/api/museo/gamificacion/niveles"
    ).status_code == 200

    assert client.get(
        "/api/museo/gamificacion/insignias"
    ).status_code == 200


def test_home_del_museo(client):

    respuesta = client.get("/api/museo/home")

    assert respuesta.status_code == 200

    assert respuesta.json()["success"] is True
