from flask import jsonify, request

from src.middlewares.error_handler import AppError
from src.models import user_model


def login():
    data = request.get_json()
    if not data:
        raise AppError('Dados inválidos', 400)

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise AppError('Email e senha são obrigatórios', 400)

    user = user_model.find_by_email(email)
    if not user or not user.check_password(password):
        raise AppError('Credenciais inválidas', 401)
    if not user.active:
        raise AppError('Usuário inativo', 403)

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': 'fake-jwt-token-' + str(user.id),
    }), 200
