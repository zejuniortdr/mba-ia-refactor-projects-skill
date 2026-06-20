from src.models.database import get_connection


def _row_to_usuario_publico(row):
    """Mapeia o usuário sem expor o campo `senha`."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def listar_usuarios():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM usuarios").fetchall()
        return [_row_to_usuario_publico(row) for row in rows]


def buscar_por_id(usuario_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return _row_to_usuario_publico(row) if row else None


def criar(nome, email, senha, tipo="cliente"):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha, tipo),
        )
        return cursor.lastrowid


def autenticar(email, senha):
    """Retorna os dados públicos do usuário se as credenciais conferirem."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE email = ? AND senha = ?",
            (email, senha),
        ).fetchone()
        if row:
            return {
                "id": row["id"],
                "nome": row["nome"],
                "email": row["email"],
                "tipo": row["tipo"],
            }
        return None
