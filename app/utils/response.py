def success(
    data=None,
    message="OK",
    status=200
):

    """
    Genera una respuesta exitosa.
    """

    return {
        "success": True,
        "message": message,
        "data": data
    }, status


def error(
    message,
    status=400,
    details=None
):

    """
    Genera una respuesta de error.
    """

    response = {
        "success": False,
        "message": message
    }


    # details se utiliza principalmente
    # para errores de validación.

    if details:

        response["details"] = details


    return response, status