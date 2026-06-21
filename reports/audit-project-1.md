============================================
# ARCHITECTURE AUDIT REPORT
Project: code-smells-project
============================================

**Stack**:   Python 3 + Flask 3.1.1 (flask-cors 5.0.1)
**Files**:   4 analyzed (app.py, controllers.py, models.py, database.py) | ~784 lines of code
**Date**:    2026-06-20

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 2

Total findings: 12

## Findings

### [CRITICAL] SQL Injection (AP-03)
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151, 155-160, 163-166, 174, 188, 192, 220, 224, 280, 289-297
Description: Praticamente TODAS as queries de `models.py` são construídas por concatenação de strings com dados vindos da requisição. `get_produto_por_id`, `login_usuario`, `criar_produto`, `criar_usuario`, `buscar_produtos`, `criar_pedido`, `atualizar_status_pedido` etc. interpolam variáveis diretamente no SQL.
Evidence:
linha 28:  cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
linha 110: "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
linha 291: query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"
Impact: Atacante pode burlar o login (`' OR '1'='1`), exfiltrar toda a base, ou destruir tabelas via qualquer endpoint que aceite parâmetros. Comprometimento total da confidencialidade e integridade dos dados.
Recommendation: Reescrever 100% das queries com placeholders parametrizados (`?`) e tuplas de parâmetros. Aplicar Playbook SQL-01 durante a extração de Models (MODEL-01).

### [CRITICAL] Arbitrary SQL Execution Endpoint (AP-03)
File: app.py:59-78
Description: O endpoint `POST /admin/query` recebe uma string SQL arbitrária do corpo da requisição (`dados.get("sql")`) e a executa diretamente, sem autenticação, autorização ou whitelist. É um RCE sobre o banco de dados exposto via HTTP.
Evidence:
linha 61: query = dados.get("sql", "")
linha 69: cursor.execute(query)
Impact: Qualquer cliente anônimo pode ler, alterar ou apagar qualquer tabela (`DROP TABLE`, `DELETE`, dump de senhas). Falha de segurança de severidade máxima.
Recommendation: Remover o endpoint por completo na refatoração. Operações administrativas devem ser feitas via models parametrizados e protegidas por autenticação.

### [CRITICAL] Hardcoded Credentials / Secrets & Plaintext Passwords (AP-02)
File: app.py:7; controllers.py:289; database.py:76-78; models.py:83, 99, 118
Description: A `SECRET_KEY` está hardcoded no código (app.py:7) e ainda é vazada na resposta JSON do `/health` (controllers.py:289). Senhas são armazenadas em texto puro no banco (database.py seed) e retornadas em respostas (`get_todos_usuarios` inclui o campo `senha`).
Evidence:
linha 7:   app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
linha 289: "secret_key": "minha-chave-super-secreta-123"
linha 76:  ("Admin", "admin@loja.com", "admin123", "admin"),
Impact: Qualquer pessoa com acesso ao repositório ou ao endpoint `/health` obtém a chave de assinatura de sessões; senhas em texto puro permitem comprometimento total de contas em caso de vazamento do `loja.db`.
Recommendation: Extrair `SECRET_KEY` para variável de ambiente (Playbook ENV-01), remover o vazamento no `/health`, nunca retornar `senha` em respostas e aplicar hashing (bcrypt) — no mínimo remover o campo dos retornos durante a extração de Models.

### [CRITICAL] God File / Mixed Responsibilities (AP-01)
File: models.py:1-315; app.py:47-78
Description: `models.py` mistura acesso a dados, regras de negócio (cálculo de total e validação de estoque em `criar_pedido`, cálculo de descontos em `relatorio_vendas`) e mapeamento manual de linhas. `app.py` deixou de ser apenas composition root: contém rotas administrativas (`/admin/reset-db`, `/admin/query`) com SQL e lógica inline. Não há camada real de separação.
Evidence:
linha 137-146: total = 0 / for item in itens: ... total = total + (produto["preco"] * item["quantidade"])
linha 256-262: if faturamento > 10000: desconto = faturamento * 0.1 ...
linha 51-54:   cursor.execute("DELETE FROM itens_pedido") ... (SQL dentro de app.py)
Impact: Impossível testar regras de negócio isoladamente; qualquer mudança de regra exige tocar na camada de dados; o entry point acumula responsabilidades de roteamento, persistência e administração.
Recommendation: Separar em Models (apenas dados), Services/Models para regras de domínio e Controllers para orquestração, conforme MODEL-01 e CTRL-01. Mover rotas administrativas para um controller dedicado (ou removê-las).

### [HIGH] Business Logic & Side-Effects in Controllers (AP-04)
File: controllers.py:188-220, 237-255; models.py:235-273
Description: O controller `criar_pedido` dispara efeitos colaterais de domínio (envio simulado de e-mail/SMS/push via `print`) e `atualizar_status_pedido` contém regras de negócio sobre transições de status. A regra de negócio de descontos vive em `relatorio_vendas` (model), espalhando lógica de domínio entre camadas sem um service.
Evidence:
linha 208: print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + ...)
linha 247: if novo_status == "aprovado": print("NOTIFICAÇÃO: ...")
Impact: Notificações e regras de domínio não são reutilizáveis nem testáveis; o controller conhece detalhes de negócio que deveriam estar em um service/model.
Recommendation: Mover regras de domínio para Models/Services e isolar notificações em um módulo dedicado, chamado pelo controller. Aplicar CTRL-01 e MODEL-01.

### [HIGH] Global Mutable State (AP-09)
File: database.py:4-12
Description: A conexão com o banco é uma variável global mutável (`db_connection`), inicializada sob demanda com `global` e `check_same_thread=False`, compartilhada entre todas as threads do Flask.
Evidence:
linha 4:  db_connection = None
linha 9:  global db_connection
linha 10: db_connection = sqlite3.connect(db_path, check_same_thread=False)
Impact: Race conditions e cursores compartilhados entre requests concorrentes; comportamento não-determinístico e vazamento de estado entre requisições em produção.
Recommendation: Encapsular a conexão em um módulo `models/database.py` com função `get_db_connection()` que abre/fecha conexão por uso (context manager), conforme MODEL-01.

### [HIGH] Missing Error Handling / Exposed Stack Traces (AP-10)
File: app.py:8, 88; controllers.py:12, 22, 62, 78 (e todos os `except`); app.py:77
Description: `DEBUG=True` está fixo em produção e a aplicação roda com `debug=True`. Todos os handlers capturam exceções e retornam `str(e)` diretamente ao cliente, vazando detalhes internos. Não há middleware de error handling centralizado — cada rota repete o mesmo `try/except`.
Evidence:
linha 8:   app.config["DEBUG"] = True
linha 12:  return jsonify({"erro": str(e)}), 500
linha 88:  app.run(host="0.0.0.0", port=5000, debug=True)
Impact: Vazamento de mensagens internas (SQL, paths) ao cliente; `debug=True` expõe o console interativo Werkzeug (RCE) se acessível; tratamento de erro duplicado e inconsistente.
Recommendation: Centralizar tratamento via `@app.errorhandler` (Playbook ERR-01), controlar `DEBUG` por variável de ambiente (ENV-01) e remover `str(e)` das respostas ao cliente.

### [MEDIUM] N+1 Query Problem (AP-05)
File: models.py:171-201, 203-233
Description: `get_pedidos_usuario` e `get_todos_pedidos` executam, para cada pedido, uma query de itens e, para cada item, mais uma query de nome de produto — gerando 1 + N + (N*M) queries.
Evidence:
linha 188: cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
linha 192: cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
Impact: Degradação exponencial de performance com o volume de pedidos/itens; risco de timeout em produção.
Recommendation: Substituir por uma única query com `JOIN` entre `pedidos`, `itens_pedido` e `produtos`, agrupando em Python (Playbook PERF-01).

### [MEDIUM] Missing Input Validation (AP-06)
File: controllers.py:167-176, 188-203, 237-245
Description: Validações inconsistentes e incompletas. `login` e `criar_pedido` assumem que `request.get_json()` não é None e não validam tipos; a estrutura de cada item de pedido (`produto_id`, `quantidade`) não é validada antes de chegar ao model; `preco`/`estoque` não têm verificação de tipo.
Evidence:
linha 170: email = dados.get("email", "")  (sem checar se dados é None)
linha 196: itens = dados.get("itens", [])  (itens não validados estruturalmente)
Impact: Requisições malformadas causam 500 (TypeError) em vez de 400; dados inválidos podem chegar ao banco.
Recommendation: Validação explícita de presença e tipo nos controllers antes de chamar o model (Playbook VAL-01).

### [MEDIUM] Duplicate Code / DRY Violation (AP-07)
File: models.py (todas as funções: `db = get_db(); cursor = db.cursor()`); controllers.py (try/except idêntico em ~16 funções); models.py:171-201 ≈ 203-233
Description: O par `db = get_db(); cursor = db.cursor()` repete-se em todas as ~16 funções de model; o bloco `try/except Exception as e: return jsonify({"erro": str(e)}), 500` repete-se em quase todos os controllers; `get_pedidos_usuario` e `get_todos_pedidos` são praticamente idênticas; o mapeamento manual linha→dict de produto repete-se 3x.
Evidence:
linha 5-6:   db = get_db() / cursor = db.cursor()
linha 10-12: except Exception as e: ... return jsonify({"erro": str(e)}), 500
Impact: Mudança na obtenção de conexão ou no tratamento de erro exige editar dezenas de pontos; risco de divergência entre cópias.
Recommendation: Centralizar conexão em `models/database.py`, error handling em middleware (ERR-01) e extrair um mapeador de linha (helper) reutilizável.

### [LOW] Magic Numbers (AP-11)
File: models.py:256-262; controllers.py:47-50
Description: Limiares e percentuais de desconto soltos em `relatorio_vendas` (10000/5000/1000 e 0.1/0.05/0.02) e limites de tamanho de nome (2/200) sem constantes nomeadas.
Evidence:
linha 257: if faturamento > 10000: desconto = faturamento * 0.1
linha 259: elif faturamento > 5000: desconto = faturamento * 0.05
Impact: Significado dos valores não é evidente; mudança de regra exige caçar números espalhados.
Recommendation: Extrair para constantes nomeadas no model/service (ex: `DESCONTO_FAIXA_ALTA = 0.1`).

### [LOW] Poor Naming / Readability (AP-12)
File: models.py:187-193, 219-225; controllers.py (uso de `id` como parâmetro); múltiplos arquivos
Description: Identificadores não descritivos: `cursor2`, `cursor3`, `prod`, `row`, e o parâmetro `id` que sombreia o builtin do Python; variável genérica `dados` em todos os controllers.
Evidence:
linha 187: cursor2 = db.cursor()
linha 191: cursor3 = db.cursor()
Impact: Leitura e revisão mais lentas; maior chance de erro ao alterar; sombreamento de builtin.
Recommendation: Renomear para nomes que revelam intenção (`cursor_itens`, `cursor_produto`, `produto`, `produto_id`) durante a refatoração.

================================

Total: 12 findings

CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 2
