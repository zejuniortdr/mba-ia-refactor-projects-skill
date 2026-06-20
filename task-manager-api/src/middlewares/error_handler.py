from flask import jsonify

from src.models.database import db


class AppError(Exception):
    """Erro de aplicação com status code e mensagem amigável."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_error_handlers(app):
    """Registra handlers de erro globais (remove try/except duplicado das rotas)."""

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({'error': 'Método HTTP não permitido'}), 405

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        # Garante rollback de qualquer transação pendente e não vaza stack trace.
        db.session.rollback()
        app.logger.exception('Erro não tratado')
        return jsonify({'error': 'Erro interno do servidor'}), 500
