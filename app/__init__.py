from flask import Flask
from flask_jwt_extended import JWTManager

from app.config import Config
from app.extensions import db

from app.routes.auth_routes import auth_bp
from app.routes.product_routes import product_bp
from app.routes.web_routes import web_bp


def create_app():

    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )

    app.config.from_object(Config)

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

    with app.app_context():

        from app.models.user import User
        from app.models.product import Product

        db.create_all()

    return app