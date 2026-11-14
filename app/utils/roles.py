from flask import g

from flask_jwt_extended import (
    get_jwt_identity,
    verify_jwt_in_request,
)

from app.repositories.usuario_repository import (
    UsuarioRepository
)


repository = UsuarioRepository()


def usuario_actual():

    """
    Devuelve el Usuario del JWT vigente o None.

    Funciona tanto en rutas decoradas con @jwt_required()
    como en rutas PÚBLICAS: si aún no se verificó el JWT
    en la petición, lo verifica de forma opcional (sin
    token → None; token inválido/expirado → 401).
    Un usuario inactivo no pasa.
    """

    if g.get("_jwt_extended_jwt") is None:

        verify_jwt_in_request(optional=True)

    identidad = get_jwt_identity()

    if identidad is None:

        return None

    try:

        usuario_id = int(identidad)

    except (TypeError, ValueError):

        return None

    usuario = repository.get_by_id(usuario_id)

    if usuario is None or not usuario.estado:

        return None

    return usuario


def es_admin(usuario):

    return (
        usuario is not None
        and usuario.rol is not None
        and usuario.rol.nombre == "admin"
    )


def es_docente(usuario):

    return (
        usuario is not None
        and usuario.rol is not None
        and usuario.rol.nombre == "docente"
    )
