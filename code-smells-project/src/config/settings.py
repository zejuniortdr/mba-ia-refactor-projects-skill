import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configurações da aplicação lidas de variáveis de ambiente.

    Nenhum segredo deve ser hardcoded aqui — apenas defaults seguros de
    desenvolvimento. Em produção, defina as variáveis via .env / ambiente.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
