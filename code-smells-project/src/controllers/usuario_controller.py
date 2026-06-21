from flask import request, jsonify

from src.models import usuario_model
from src.middlewares.error_handler import AppError


def listar_usuarios():
    usuarios = usuario_model.listar_usuarios()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_usuario(id):
    usuario = usuario_model.buscar_por_id(id)
    if not usuario:
        raise AppError("Usuário não encontrado", 404)
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar_usuario():
    dados = request.get_json(silent=True)
    if not dados:
        raise AppError("Dados inválidos", 400)

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise AppError("Nome, email e senha são obrigatórios", 400)

    novo_id = usuario_model.criar(nome, email, senha)
    return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201


def login():
    dados = request.get_json(silent=True)
    if not dados:
        raise AppError("Email e senha são obrigatórios", 400)

    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        raise AppError("Email e senha são obrigatórios", 400)

    usuario = usuario_model.autenticar(email, senha)
    if not usuario:
        raise AppError("Email ou senha inválidos", 401)

    return jsonify(
        {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}
    ), 200
