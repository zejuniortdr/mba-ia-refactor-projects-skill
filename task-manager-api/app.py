from src.app import create_app
from src.config.settings import Config

app = create_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
