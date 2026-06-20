from flask import request, jsonify

from src.models import pedido_model
from src.services import notification_service
from src.middlewares.error_handler import AppError


def criar_pedido():
    dados = request.get_json(silent=True)
    if not dados:
        raise AppError("Dados inválidos", 400)

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise AppError("Usuario ID é obrigatório", 400)
    if not itens or len(itens) == 0:
        raise AppError("Pedido deve ter pelo menos 1 item", 400)
    for item in itens:
        if not isinstance(item, dict) or "produto_id" not in item or "quantidade" not in item:
            raise AppError("Cada item deve ter produto_id e quantidade", 400)

    resultado = pedido_model.criar(usuario_id, itens)
    notification_service.notificar_pedido_criado(resultado["pedido_id"], usuario_id)

    return jsonify(
        {"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}
    ), 201


def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_model.listar_por_usuario(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_todos_pedidos():
    pedidos = pedido_model.listar_todos()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json(silent=True) or {}
    novo_status = dados.get("status", "")

    if novo_status not in pedido_model.STATUS_VALIDOS:
        raise AppError("Status inválido", 400)

    pedido_model.atualizar_status(pedido_id, novo_status)
    notification_service.notificar_mudanca_status(pedido_id, novo_status)

    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


def relatorio_vendas():
    relatorio = pedido_model.relatorio_vendas()
    return jsonify({"dados": relatorio, "sucesso": True}), 200
