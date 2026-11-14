from flask import Flask
from flask_jwt_extended import JWTManager

from app.config import Config
from app.extensions import db

from app.routes.auth_routes import auth_bp
from app.routes.product_routes import product_bp
from app.routes.web_routes import web_bp

# Blueprints del museo SIMUL (arquitectura por capas
# idéntica a la del profesor: routes → controllers →
# services → repositories → models).
from app.routes.simul_auth_routes import simul_auth_bp
from app.routes.contenido_routes import contenido_bp
from app.routes.validacion_routes import validacion_bp
from app.routes.gamificacion_routes import (
    gamificacion_bp
)
from app.routes.admin_routes import admin_bp
from app.routes.museo_routes import museo_bp


def create_app(test_config=None):

    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )

    app.config.from_object(Config)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)

    JWTManager(app)

    app.register_blueprint(web_bp)

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
        product_bp,
        url_prefix="/api/products"
    )

    # --------------------------------------------------------
    # MUSEO SIMUL
    # --------------------------------------------------------

    app.register_blueprint(
        simul_auth_bp,
        url_prefix="/api/museo/auth"
    )

    app.register_blueprint(
        contenido_bp,
        url_prefix="/api/museo/contenido"
    )

    app.register_blueprint(
        validacion_bp,
        url_prefix="/api/museo/validacion"
    )

    app.register_blueprint(
        gamificacion_bp,
        url_prefix="/api/museo/gamificacion"
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/api/museo/admin"
    )

    app.register_blueprint(
        museo_bp,
        url_prefix="/api/museo"
    )

    with app.app_context():

        # Modelos del profesor + 25 tablas del museo.
        # Ojo: "import app.models" (sin "as") rebindaría la
        # variable local "app" y create_app devolvería el
        # módulo en vez de la instancia de Flask.
        import app.models as _modelos  # noqa: F401

        db.create_all()

    return app
