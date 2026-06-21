from flask import Flask
from flask_cors import CORS

from src.config.settings import Config
from src.middlewares.error_handler import register_error_handlers
from src.models.database import db
from src.views.routes import register_routes


def create_app(config_object=Config):
    """Composition root: cria o app, registra extensões, rotas e error handlers."""
    app = Flask(__name__)
    app.config.from_object(config_object)

    CORS(app)
    db.init_app(app)

    register_routes(app)
    register_error_handlers(app)

    with app.app_context():
        import src.models  # noqa: F401  (garante o registro dos models)
        db.create_all()

    return app
