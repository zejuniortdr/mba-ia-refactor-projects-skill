from flask import jsonify


class AppError(Exception):
    """Erro de domínio/validação com status HTTP associado."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_error_handlers(app):
    """Centraliza o tratamento de erros (resolve try/except duplicado e
    vazamento de stack trace). Mantém o formato de resposta da API:
    {"erro": <mensagem>, "sucesso": False}.
    """

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"erro": error.message, "sucesso": False}), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"erro": "Método HTTP não permitido", "sucesso": False}), 405

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        # Não vaza detalhes internos (str(e)/stack trace) ao cliente.
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
