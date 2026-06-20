from src.models.database import get_connection


def _row_to_produto(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def listar_produtos():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM produtos").fetchall()
        return [_row_to_produto(row) for row in rows]


def buscar_por_id(produto_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return _row_to_produto(row) if row else None


def criar(nome, descricao, preco, estoque, categoria):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    with get_connection() as conn:
        conn.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, "
            "estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
        return True


def deletar(produto_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        return True


def buscar(termo, categoria=None, preco_min=None, preco_max=None):
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    with get_connection() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
        return [_row_to_produto(row) for row in rows]
