from src.models.database import get_connection
from src.middlewares.error_handler import AppError

# Faixas de desconto sobre o faturamento (resolve Magic Numbers).
FAIXA_DESCONTO_ALTO = 10000
FAIXA_DESCONTO_MEDIO = 5000
FAIXA_DESCONTO_BAIXO = 1000
DESCONTO_ALTO = 0.10
DESCONTO_MEDIO = 0.05
DESCONTO_BAIXO = 0.02

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def criar(usuario_id, itens):
    """Cria um pedido validando estoque e calculando o total.

    Levanta AppError (400) quando um produto não existe ou não há estoque.
    Retorna {"pedido_id": id, "total": total}.
    """
    with get_connection() as conn:
        total = 0
        for item in itens:
            produto = conn.execute(
                "SELECT * FROM produtos WHERE id = ?", (item["produto_id"],)
            ).fetchone()
            if produto is None:
                raise AppError(
                    f"Produto {item['produto_id']} não encontrado", 400
                )
            if produto["estoque"] < item["quantidade"]:
                raise AppError(
                    f"Estoque insuficiente para {produto['nome']}", 400
                )
            total += produto["preco"] * item["quantidade"]

        cursor = conn.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            produto = conn.execute(
                "SELECT preco FROM produtos WHERE id = ?", (item["produto_id"],)
            ).fetchone()
            conn.execute(
                "INSERT INTO itens_pedido "
                "(pedido_id, produto_id, quantidade, preco_unitario) "
                "VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            conn.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        return {"pedido_id": pedido_id, "total": total}


def _carregar_pedidos(where_clause="", params=()):
    """Carrega pedidos e seus itens em UMA query com JOIN (resolve N+1)."""
    query = f"""
        SELECT
            p.id, p.usuario_id, p.status, p.total, p.criado_em,
            i.produto_id, i.quantidade, i.preco_unitario,
            pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = i.produto_id
        {where_clause}
        ORDER BY p.id
    """
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    pedidos = {}
    ordem = []
    for row in rows:
        pedido_id = row["id"]
        if pedido_id not in pedidos:
            pedidos[pedido_id] = {
                "id": pedido_id,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            ordem.append(pedido_id)
        if row["produto_id"] is not None:
            pedidos[pedido_id]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] or "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return [pedidos[pid] for pid in ordem]


def listar_por_usuario(usuario_id):
    return _carregar_pedidos("WHERE p.usuario_id = ?", (usuario_id,))


def listar_todos():
    return _carregar_pedidos()


def atualizar_status(pedido_id, novo_status):
    with get_connection() as conn:
        conn.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            (novo_status, pedido_id),
        )
        return True


def _calcular_desconto(faturamento):
    if faturamento > FAIXA_DESCONTO_ALTO:
        return faturamento * DESCONTO_ALTO
    if faturamento > FAIXA_DESCONTO_MEDIO:
        return faturamento * DESCONTO_MEDIO
    if faturamento > FAIXA_DESCONTO_BAIXO:
        return faturamento * DESCONTO_BAIXO
    return 0


def relatorio_vendas():
    with get_connection() as conn:
        total_pedidos = conn.execute(
            "SELECT COUNT(*) FROM pedidos"
        ).fetchone()[0]
        faturamento = conn.execute(
            "SELECT SUM(total) FROM pedidos"
        ).fetchone()[0] or 0
        pendentes = conn.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'"
        ).fetchone()[0]
        aprovados = conn.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'"
        ).fetchone()[0]
        cancelados = conn.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'"
        ).fetchone()[0]

    desconto = _calcular_desconto(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }


def contar_por_tabela():
    """Contagens usadas pelo health check."""
    with get_connection() as conn:
        produtos = conn.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
        usuarios = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        pedidos = conn.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    return {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos}
