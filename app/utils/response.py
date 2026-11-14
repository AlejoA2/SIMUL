"""
Sobre de respuestas de la API.

Se conserva el formato {success, message, data} / {success,
message, details} que usan el frontend y las capas de
servicio; aquí se emite como JSONResponse con el código
HTTP correspondiente (FastAPI no usa tuplas como Flask).
"""

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success(
    data=None,
    message="OK",
    status=200
):

    """
    Genera una respuesta exitosa.
    """

    return JSONResponse(
        status_code=status,
        content=jsonable_encoder({
            "success": True,
            "message": message,
            "data": data
        })
    )


def error(
    message,
    status=400,
    details=None
):

    """
    Genera una respuesta de error.

    details se utiliza principalmente para errores de
    validación de campos.
    """

    cuerpo = {
        "success": False,
        "message": message
    }

    if details:

        cuerpo["details"] = details

    return JSONResponse(
        status_code=status,
        content=jsonable_encoder(cuerpo)
    )
