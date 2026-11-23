"""
Vistas HTML (Jinja2) para FastAPI.

- renderizar(): envuelve TemplateResponse y siempre inyecta
  `url_for` para los templates Jinja:
  url_for('web.<pagina>', ...) y url_for('static', ...).
- El mapa endpoint → ruta se alimenta desde el propio
  web_router (los nombres de ruta son la fuente de verdad,
  sin duplicar el mapa de URLs).
"""

import re
from urllib.parse import urlencode

from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="app/templates")

_mapa_rutas: dict = {}


def registrar_rutas_web(web_router):

    """Registra las rutas web para resolver url_for()."""

    for ruta in web_router.routes:

        _mapa_rutas[ruta.name] = ruta


def url_for(endpoint, **params):

    """
    Construye una URL para los templates Jinja.

    - url_for('static', filename='css/app.css') → /static/...
    - url_for('web.detalle_contenido', contenido_id=3)
        → /contenido/3
    - url_for('web.buscar', cat='eventos')
        → /buscar?cat=eventos  (los extras van en query)
    """

    if endpoint == "static":

        return f"/static/{params.get('filename', '')}"

    ruta = _mapa_rutas.get(endpoint)

    if ruta is None:

        raise RuntimeError(
            f"url_for: endpoint desconocido '{endpoint}'"
        )

    plantilla = ruta.path

    nombres_path = set(
        re.findall(r"\{(\w+)[^}]*\}", plantilla)
    )

    path_params = {
        k: v for k, v in params.items()
        if k in nombres_path
    }

    query_params = {
        k: v for k, v in params.items()
        if k not in nombres_path
    }

    url = str(ruta.url_path_for(endpoint, **path_params))

    if query_params:

        return f"{url}?{urlencode(query_params)}"

    return url


def renderizar(request, plantilla, status_code=200, **contexto):

    """render_template() equivalent: Jinja2 + url_for."""

    contexto.setdefault("url_for", url_for)

    return templates.TemplateResponse(
        request,
        plantilla,
        contexto,
        status_code=status_code
    )
