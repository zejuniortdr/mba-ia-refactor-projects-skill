from flask import request, jsonify

from src.models import produto_model
from src.middlewares.error_handler import AppError

CATEGORIAS_VALIDAS = [
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
]
NOME_TAMANHO_MIN = 2
NOME_TAMANHO_MAX = 200


def _validar_produto(dados):
    if not dados:
        raise AppError("Dados inválidos", 400)
    for campo, label in (("nome", "Nome"), ("preco", "Preço"), ("estoque", "Estoque")):
        if campo not in dados:
            raise AppError(f"{label} é obrigatório", 400)

    nome = dados["nome"]
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        raise AppError("Preço não pode ser negativo", 400)
    if estoque < 0:
        raise AppError("Estoque não pode ser negativo", 400)
    if len(nome) < NOME_TAMANHO_MIN:
        raise AppError("Nome muito curto", 400)
    if len(nome) > NOME_TAMANHO_MAX:
        raise AppError("Nome muito longo", 400)
    if categoria not in CATEGORIAS_VALIDAS:
        raise AppError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS), 400)

    return {
        "nome": nome,
        "descricao": dados.get("descricao", ""),
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def listar_produtos():
    produtos = produto_model.listar_produtos()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(id):
    produto = produto_model.buscar_por_id(id)
    if not produto:
        raise AppError("Produto não encontrado", 404)
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar_produto():
    dados = _validar_produto(request.get_json(silent=True))
    novo_id = produto_model.criar(**dados)
    return jsonify(
        {"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}
    ), 201


def atualizar_produto(id):
    if not produto_model.buscar_por_id(id):
        raise AppError("Produto não encontrado", 404)
    dados = _validar_produto(request.get_json(silent=True))
    produto_model.atualizar(id, **dados)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    if not produto_model.buscar_por_id(id):
        raise AppError("Produto não encontrado", 404)
    produto_model.deletar(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)

    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)

    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify(
        {"dados": resultados, "total": len(resultados), "sucesso": True}
    ), 200
