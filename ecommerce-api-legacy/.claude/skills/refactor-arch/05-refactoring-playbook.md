# Playbook de Refatoração — Padrões de Transformação

> 8 padrões de transformação com exemplos ANTES/DEPOIS.
> Referência obrigatória durante a Fase 3.

---

## PLAYBOOK-01: Extração de Configuração (ENV-01)

**Problema:** Credenciais e configurações hardcoded no código.
**Solução:** Extrair para variáveis de ambiente + arquivo `.env.example`.

### ANTES:
```python
# app.py
app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'
DATABASE = 'database.db'
```

### DEPOIS:
```python
# src/config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-only-insecure-key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
```

```bash
# .env.example (commitado no repo — sem valores reais)
SECRET_KEY=troque-por-chave-segura-em-producao
DATABASE_URL=sqlite:///app.db
DEBUG=False
```

**Passos:**
1. Instalar `python-dotenv` (Python) ou `dotenv` (Node.js)
2. Criar `.env.example` com todas as variáveis necessárias
3. Criar `.env` local (adicionado ao `.gitignore`)
4. Criar `src/config/settings.py` ou `src/config/settings.js`
5. Substituir todas as ocorrências de valores hardcoded

---

## PLAYBOOK-02: Extração de Model (MODEL-01)

**Problema:** SQL executado diretamente em funções de rota ou "God Class".
**Solução:** Criar model por entidade com funções de acesso ao banco.

### ANTES:
```python
# models.py (God Class)
def criar_produto(nome, preco, estoque):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)",
        (nome, preco, estoque)
    )
    db.commit()
    produto_id = cursor.lastrowid
    db.close()
    return produto_id
```

### DEPOIS:
```python
# src/models/database.py
import sqlite3
from src.config.settings import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_URL.replace('sqlite:///', ''))
    conn.row_factory = sqlite3.Row
    return conn

# src/models/produto_model.py
from src.models.database import get_db_connection

def criar_produto(nome: str, preco: float, estoque: int) -> int:
    """Insere um produto e retorna o ID gerado."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)",
            (nome, preco, estoque)
        )
        conn.commit()
        return cursor.lastrowid

def buscar_produto_por_id(produto_id: int) -> dict | None:
    """Busca produto por ID. Retorna dict ou None."""
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return dict(row) if row else None

def listar_produtos() -> list[dict]:
    """Retorna lista de todos os produtos."""
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM produtos").fetchall()
        return [dict(row) for row in rows]
```

---

## PLAYBOOK-03: Extração de Controller (CTRL-01)

**Problema:** Lógica de negócio e acesso a dados dentro das funções de rota.
**Solução:** Criar controller que orquestra a request → model → response.

### ANTES:
```python
@app.route('/produtos', methods=['POST'])
def criar_produto():
    data = request.json
    nome = data['nome']
    preco = data['preco']
    estoque = data['estoque']
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("INSERT INTO produtos VALUES (?, ?, ?)", (nome, preco, estoque))
    db.commit()
    return jsonify({"id": cursor.lastrowid, "message": "Produto criado"}), 201
```

### DEPOIS:
```python
# src/controllers/produto_controller.py
from flask import request, jsonify
from src.models import produto_model

def get_produtos():
    """Lista todos os produtos."""
    try:
        produtos = produto_model.listar_produtos()
        return jsonify(produtos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_produto():
    """Cria um novo produto."""
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['nome', 'preco', 'estoque']):
            return jsonify({"error": "Campos obrigatórios: nome, preco, estoque"}), 400

        produto_id = produto_model.criar_produto(
            nome=data['nome'],
            preco=float(data['preco']),
            estoque=int(data['estoque'])
        )
        return jsonify({"id": produto_id, "message": "Produto criado"}), 201
    except ValueError as e:
        return jsonify({"error": f"Dado inválido: {e}"}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno"}), 500
```

---

## PLAYBOOK-04: Separação de Rotas (ROUTE-01)

**Problema:** Rotas definidas diretamente no `app.py` com lógica misturada.
**Solução:** Criar arquivo de routes que apenas mapeia URLs para controllers.

### ANTES:
```python
# app.py
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    # 30 linhas de lógica...

@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    # 40 linhas de lógica...
```

### DEPOIS:
```python
# src/views/routes.py
from flask import Blueprint
from src.controllers import produto_controller, usuario_controller

produtos_bp = Blueprint('produtos', __name__)
usuarios_bp = Blueprint('usuarios', __name__)

# Produto routes
produtos_bp.route('/produtos', methods=['GET'])(produto_controller.get_produtos)
produtos_bp.route('/produtos/<int:id>', methods=['GET'])(produto_controller.get_produto)
produtos_bp.route('/produtos', methods=['POST'])(produto_controller.create_produto)
produtos_bp.route('/produtos/<int:id>', methods=['PUT'])(produto_controller.update_produto)
produtos_bp.route('/produtos/<int:id>', methods=['DELETE'])(produto_controller.delete_produto)

# Usuario routes
usuarios_bp.route('/usuarios', methods=['GET'])(usuario_controller.get_usuarios)
usuarios_bp.route('/usuarios', methods=['POST'])(usuario_controller.create_usuario)

# src/app.py
from flask import Flask
from src.views.routes import produtos_bp, usuarios_bp
from src.middlewares.error_handler import register_error_handlers
from src.config.settings import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.register_blueprint(produtos_bp)
    app.register_blueprint(usuarios_bp)
    register_error_handlers(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG)
```

---

## PLAYBOOK-05: Error Handling Centralizado (ERR-01)

**Problema:** Try/catch duplicado em cada rota, ou ausência de tratamento de erros.
**Solução:** Middleware de error handling global.

### ANTES:
```python
@app.route('/produtos/<int:id>')
def get_produto(id):
    # sem try/except — qualquer erro crasha
    produto = buscar_produto(id)
    return jsonify(produto)
```

### DEPOIS:
```python
# src/middlewares/error_handler.py

class AppError(Exception):
    """Erro customizado da aplicação com status code."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def register_error_handlers(app):
    """Registra handlers de erro globais no app Flask."""
    
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"error": error.message}), error.status_code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Recurso não encontrado"}), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"error": "Método HTTP não permitido"}), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({"error": "Erro interno do servidor"}), 500
```

```javascript
// Node.js — src/middlewares/errorHandler.js
class AppError extends Error {
    constructor(message, statusCode = 400) {
        super(message);
        this.statusCode = statusCode;
    }
}

const errorHandler = (err, req, res, next) => {
    if (err instanceof AppError) {
        return res.status(err.statusCode).json({ error: err.message });
    }
    console.error(err.stack);
    return res.status(500).json({ error: 'Erro interno do servidor' });
};

module.exports = { AppError, errorHandler };
```

---

## PLAYBOOK-06: Correção de SQL Injection (SQL-01)

**Problema:** Queries construídas via f-string/concatenação com dados do usuário.
**Solução:** Queries parametrizadas com placeholders.

### ANTES:
```python
# VULNERÁVEL A SQL INJECTION
email = request.args.get('email')
query = f"SELECT * FROM usuarios WHERE email = '{email}'"
cursor.execute(query)
```

### DEPOIS:
```python
# SEGURO — parametrizado
email = request.args.get('email')
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
```

```javascript
// ANTES — vulnerável
const query = `SELECT * FROM users WHERE email = '${email}'`;
db.query(query, callback);

// DEPOIS — seguro
db.query("SELECT * FROM users WHERE email = ?", [email], callback);
// Ou com async/await:
const result = await db.query("SELECT * FROM users WHERE email = $1", [email]);
```

---

## PLAYBOOK-07: Eliminação do N+1 Problem (PERF-01)

**Problema:** Query dentro de loop gera N queries para N itens.
**Solução:** Usar JOIN ou carregar dados relacionados em uma única query.

### ANTES:
```python
pedidos = cursor.execute("SELECT * FROM pedidos").fetchall()
for pedido in pedidos:                                # N iterações
    itens = cursor.execute(                           # N queries!
        f"SELECT * FROM itens WHERE pedido_id = {pedido['id']}"
    ).fetchall()
    pedido['itens'] = itens
```

### DEPOIS:
```python
# Uma única query com JOIN
def listar_pedidos_com_itens() -> list[dict]:
    query = """
        SELECT 
            p.id as pedido_id, p.status, p.total,
            i.produto_id, i.quantidade, i.preco_unitario
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        ORDER BY p.id
    """
    rows = conn.execute(query).fetchall()
    
    # Agrupa itens por pedido em Python (1 query total)
    pedidos = {}
    for row in rows:
        pid = row['pedido_id']
        if pid not in pedidos:
            pedidos[pid] = {"id": pid, "status": row['status'], "itens": []}
        if row['produto_id']:
            pedidos[pid]['itens'].append({
                "produto_id": row['produto_id'],
                "quantidade": row['quantidade']
            })
    return list(pedidos.values())
```

---

## PLAYBOOK-08: Validação de Entrada (VAL-01)

**Problema:** Dados do usuário usados sem validação de presença, tipo e formato.
**Solução:** Validação explícita antes de qualquer operação.

### ANTES:
```javascript
app.post('/checkout', (req, res) => {
    const { usuario_id, itens } = req.body;  // sem validação
    GodManager.processCheckout(usuario_id, itens);
});
```

### DEPOIS:
```javascript
// src/controllers/OrderController.js
const createOrder = async (req, res, next) => {
    try {
        const { usuario_id, itens } = req.body;
        
        // Validação explícita
        if (!usuario_id || typeof usuario_id !== 'number') {
            return res.status(400).json({ error: 'usuario_id deve ser um número válido' });
        }
        if (!Array.isArray(itens) || itens.length === 0) {
            return res.status(400).json({ error: 'itens deve ser um array não vazio' });
        }
        for (const item of itens) {
            if (!item.produto_id || !item.quantidade || item.quantidade <= 0) {
                return res.status(400).json({ 
                    error: 'Cada item deve ter produto_id e quantidade > 0' 
                });
            }
        }
        
        const order = await OrderModel.create({ usuario_id, itens });
        return res.status(201).json(order);
    } catch (error) {
        next(error);  // passa para o error handler global
    }
};
```