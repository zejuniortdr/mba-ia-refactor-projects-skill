from flask import Flask
from flask_cors import CORS

from src.config.settings import Config
from src.models.database import init_db
from src.views.routes import register_routes
from src.middlewares.error_handler import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    register_routes(app)
    register_error_handlers(app)
    return app


app = create_app()

if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{Config.PORT}")
    print("=" * 50)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
