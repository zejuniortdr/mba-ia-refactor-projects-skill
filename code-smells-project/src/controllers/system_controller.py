from flask import jsonify

from src.models import database, pedido_model


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def health_check():
    counts = pedido_model.contar_por_tabela()
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": counts,
        "versao": "1.0.0",
    }), 200


def reset_database():
    database.reset_database()
    print("!!! BANCO DE DADOS RESETADO !!!")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
