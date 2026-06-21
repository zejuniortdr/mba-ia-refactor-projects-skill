# Catálogo de Anti-Patterns — Auditoria Arquitetural

> 12 anti-patterns com sinais de detecção, severidade e exemplo de evidência.
> Classificação: CRITICAL > HIGH > MEDIUM > LOW

---

## AP-01: God Class / God File
**Severidade:** CRITICAL
**Categoria:** Arquitetura / Separação de Responsabilidades

**Descrição:**
Um único arquivo ou classe concentra responsabilidades de múltiplas camadas: acesso ao banco de dados,
lógica de negócio, validação de entrada, formatação de resposta e roteamento HTTP — tudo junto.

**Sinais de Detecção:**
- Arquivo único com >200 linhas contendo imports de `flask`, `sqlite3` e funções de negócio
- Funções que fazem `db.execute(SQL)` E retornam `jsonify()` na mesma função
- Um arquivo com >5 responsabilidades distintas identificáveis
- Nomes como `models.py` que contêm rotas, ou `app.py` que contém SQL

**Exemplo de Evidência:**
```python
# models.py — anti-pattern: SQL + lógica + formatação na mesma função
def criar_pedido(usuario_id, itens):
    db = sqlite3.connect('database.db')          # ← acesso direto ao DB
    total = sum(i['preco'] * i['qtd'] for i in itens)  # ← lógica de negócio
    cursor.execute("INSERT INTO pedidos...")      # ← SQL puro
    return {"pedido_id": id, "total": total}     # ← formatação de resposta
```

**Impacto:** Impossível testar unitariamente, mudanças em uma camada afetam todas as outras.

---

## AP-02: Hardcoded Credentials / Secrets
**Severidade:** CRITICAL
**Categoria:** Segurança

**Descrição:**
Credenciais, chaves secretas, senhas ou tokens de API escritos diretamente no código-fonte.

**Sinais de Detecção:**
- `SECRET_KEY = 'algum-valor-fixo'` em qualquer arquivo Python
- `app.secret_key = 'string_literal'`
- `password = 'admin123'` fora de testes
- Strings que parecem tokens/chaves (comprimento >20 chars, caracteres aleatórios)
- Connection strings com usuário/senha embutidos: `postgres://user:pass@host/db`

**Exemplo de Evidência:**
```python
app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'  # ← CRITICAL
DB_PASSWORD = 'admin@123'                                     # ← CRITICAL
```

**Impacto:** Exposição de dados em repositórios públicos, comprometimento de segurança total.

---

## AP-03: SQL Injection Vulnerability
**Severidade:** CRITICAL
**Categoria:** Segurança

**Descrição:**
Queries SQL construídas via concatenação de strings com dados vindos da requisição HTTP,
permitindo que atacantes manipulem a query executada.

**Sinais de Detecção:**
- `f"SELECT * FROM tabela WHERE id = {variavel}"` — f-string com variável em SQL
- `"SELECT ... WHERE id = " + str(request.args.get('id'))` — concatenação
- `.format()` em strings SQL com dados do usuário
- `%s` com `%` operator (em vez de parametrização segura)

**Exemplo de Evidência:**
```python
# CRÍTICO: variável da requisição diretamente na query
query = f"SELECT * FROM usuarios WHERE email = '{email}'"
cursor.execute(query)
```

**Impacto:** Atacante pode exfiltrar toda a base de dados, alterar dados ou deletar tabelas.

---

## AP-04: Business Logic in Controllers / Routes
**Severidade:** HIGH
**Categoria:** Violação de MVC

**Descrição:**
Lógica de negócio complexa (cálculos, validações de domínio, regras de negócio)
implementada diretamente nas funções de rota ou controller, em vez de ser delegada aos Models/Services.

**Sinais de Detecção:**
- Funções de rota com >30 linhas
- Loops `for` dentro de funções decoradas com `@app.route`
- Cálculos de totais, descontos, impostos dentro da função de rota
- Lógica de validação de negócio (ex: "produto em estoque?") dentro do controller

**Exemplo de Evidência:**
```python
@app.route('/checkout', methods=['POST'])
def checkout():
    itens = request.json['itens']
    total = 0
    for item in itens:                              # ← lógica de negócio na rota
        produto = db.execute(f"SELECT preco FROM produtos WHERE id = {item['id']}").fetchone()
        total += produto['preco'] * item['quantidade']
    desconto = total * 0.1 if len(itens) > 5 else 0  # ← regra de negócio
    total_final = total - desconto
    # ... 20 mais linhas de lógica
```

**Impacto:** Impossível reutilizar lógica, testar em isolamento ou mudar regra sem tocar nas rotas.

---

## AP-05: N+1 Query Problem
**Severidade:** MEDIUM
**Categoria:** Performance

**Descrição:**
Execução de uma query para buscar uma lista de itens, seguida de N queries adicionais
(uma para cada item) para buscar dados relacionados, em vez de usar JOIN ou carregamento eager.

**Sinais de Detecção:**
- `db.execute(SELECT)` dentro de um loop `for` que já itera sobre resultados de outro SELECT
- Padrão: `for item in items: db.execute("SELECT ... WHERE id = " + item.id)`
- Qualquer query SQL dentro de um loop `for` / `.forEach()` / `.map()`

**Exemplo de Evidência:**
```python
pedidos = cursor.execute("SELECT * FROM pedidos").fetchall()
for pedido in pedidos:                                # ← loop sobre N pedidos
    itens = cursor.execute(                           # ← N queries adicionais!
        f"SELECT * FROM itens WHERE pedido_id = {pedido['id']}"
    ).fetchall()
```

**Impacto:** Performance exponencialmente pior com volume de dados, timeout em produção.

---

## AP-06: Missing Input Validation
**Severidade:** MEDIUM
**Categoria:** Segurança / Robustez

**Descrição:**
Dados recebidos da requisição HTTP usados diretamente sem validação de tipo, presença ou formato.

**Sinais de Detecção:**
- `request.json['campo']` sem verificar se `request.json` não é None
- `request.args.get('id')` usado diretamente em queries sem conversão/validação
- Ausência de qualquer bloco try/except ou verificação `if campo is None` antes do uso
- Funções de rota que não validam campos obrigatórios

**Exemplo de Evidência:**
```javascript
app.post('/users', (req, res) => {
    const { name, email, password } = req.body;  // ← sem validação
    db.query(`INSERT INTO users VALUES ('${name}', '${email}', '${password}')`);
});
```

**Impacto:** Crashes com dados malformados, dados inválidos no banco, vetores de ataque.

---

## AP-07: Duplicate Code / DRY Violation
**Severidade:** MEDIUM
**Categoria:** Manutenibilidade

**Descrição:**
O mesmo bloco de código (abertura de conexão com banco, tratamento de erro, validação)
repetido em múltiplas funções sem abstração.

**Sinais de Detecção:**
- `sqlite3.connect('database.db')` aparece em >2 funções diferentes
- Blocos try/except idênticos em múltiplas rotas
- A mesma query SQL (com variações mínimas) aparece em 3+ lugares
- Funções de formatação de resposta repetidas

**Exemplo de Evidência:**
```python
# Em criar_produto():
db = sqlite3.connect('database.db')
cursor = db.cursor()
# ... lógica

# Em listar_produtos():
db = sqlite3.connect('database.db')   # ← duplicado
cursor = db.cursor()                  # ← duplicado
```

**Impacto:** Mudança na conexão exige editar N arquivos, bugs introduzidos em cópias divergentes.

---

## AP-08: Deprecated API Usage
**Severidade:** MEDIUM
**Categoria:** Modernização / Compatibilidade

**Descrição:**
Uso de APIs, funções ou padrões que foram marcados como deprecated na versão atual do framework
ou que são considerados práticas ultrapassadas.

**Sinais de Detecção — Python/Flask:**
- `@app.before_first_request` → removido no Flask 2.3+
- `flask.ext.*` → removido no Flask 1.0
- `flask.json.JSONEncoder` customizado sem usar `app.json`
- `db.engine.execute()` → deprecated no SQLAlchemy 2.0

**Sinais de Detecção — Node.js/Express:**
- `req.param('name')` → removido no Express 5
- `app.configure()` → removido no Express 4
- `res.send(404)` → use `res.status(404).send()` no Express 4+
- Callbacks em vez de async/await em código novo (não é deprecated, mas é smelly)
- `new Buffer()` → use `Buffer.from()` no Node.js 10+

**Exemplo de Evidência:**
```python
@app.before_first_request  # ← deprecated Flask 2.3, removido Flask 3.0
def inicializar_banco():
    criar_tabelas()
```

**Impacto:** Quebra em upgrades de versão, warnings em produção, incompatibilidade futura.

---

## AP-09: Global Mutable State
**Severidade:** HIGH
**Categoria:** Concorrência / Testabilidade

**Descrição:**
Uso de variáveis globais mutáveis para armazenar estado da aplicação (conexões de banco,
sessões de usuário, contadores) que podem causar race conditions em ambientes multi-thread.

**Sinais de Detecção:**
- Variáveis definidas no nível do módulo que são modificadas dentro de funções
- `global db_connection` dentro de funções
- Objetos singleton mutáveis passados por referência entre handlers
- Estado de sessão armazenado em memória sem thread-safety

**Exemplo de Evidência:**
```python
db_connection = None  # ← estado global

def get_connection():
    global db_connection          # ← modificação de global
    if db_connection is None:
        db_connection = sqlite3.connect('db.sqlite')
    return db_connection
```

**Impacto:** Race conditions em produção, vazamento de dados entre requests, testes não-determinísticos.

---

## AP-10: Missing Error Handling / Exposed Stack Traces
**Severidade:** HIGH
**Categoria:** Segurança / UX

**Descrição:**
Ausência de tratamento de erros nas rotas HTTP, expondo stack traces completos para o cliente
ou deixando a aplicação crashar com exceções não capturadas.

**Sinais de Detecção:**
- Rotas sem nenhum bloco try/except (Python) ou try/catch (JS)
- `app.run(debug=True)` em configuração de produção
- Ausência de middleware de error handling global (`@app.errorhandler` ou `app.use((err, req, res, next)`)
- Retorno direto de objetos de exceção para o cliente

**Exemplo de Evidência:**
```javascript
app.get('/products/:id', (req, res) => {
    // ← sem try/catch: qualquer erro crasha o servidor
    const product = GodManager.getProduct(req.params.id);
    res.json(product);
});
```

**Impacto:** Vazamento de informações de infraestrutura, crashes em produção, má experiência do usuário.

---

## AP-11: Magic Numbers
**Severidade:** LOW
**Categoria:** Legibilidade / Manutenibilidade

**Descrição:**
Números literais ("mágicos") embutidos diretamente em cálculos, condicionais ou
configurações, sem nome ou constante que explique seu significado. O leitor precisa
adivinhar o que `0.1`, `5` ou `2` representam.

**Sinais de Detecção:**
- Literais numéricos em cálculos de negócio: `total * 0.1`, `preco * 1.18`
- Limiares soltos em condicionais: `if len(itens) > 5`, `if idade >= 18`
- Códigos de status/tipo como inteiros crus: `if status == 2`, `tipo = 3`
- Timeouts, tamanhos de página, limites sem constante nomeada: `[:20]`, `timeout=30`

**Exemplo de Evidência:**
```python
desconto = total * 0.1 if len(itens) > 5 else 0   # ← 0.1 e 5 são magic numbers
if pedido['status'] == 2:                          # ← o que significa 2?
    enviar_email()
```

**Impacto:** Código difícil de entender e manter; mudança de regra exige caçar o número
em vários lugares; risco de inconsistência quando o mesmo valor é replicado.

---

## AP-12: Poor Naming / Readability
**Severidade:** LOW
**Categoria:** Legibilidade / Manutenibilidade

**Descrição:**
Identificadores não descritivos que não revelam intenção — variáveis de uma letra fora
de loops triviais, abreviações ambíguas, nomes genéricos e sufixos numéricos que não
explicam a diferença entre si.

**Sinais de Detecção:**
- Variáveis de 1–2 caracteres fora de loops curtos: `d`, `x`, `tmp`, `val`
- Nomes genéricos que não dizem nada: `data`, `data2`, `info`, `result2`, `obj`
- Funções vagas: `processar()`, `fazer()`, `handle()`, `do_stuff()`
- Booleanos sem prefixo de intenção: `flag`, `check` (em vez de `is_ativo`, `tem_estoque`)

**Exemplo de Evidência:**
```python
def processar(d):                  # ← 'processar' e 'd' não revelam intenção
    tmp = d['p'] * d['q']          # ← 'tmp', 'p', 'q' ambíguos
    data2 = calcular(tmp)          # ← 'data2' não diz o que contém
    return data2
```

**Impacto:** Leitura e revisão mais lentas, maior chance de erro ao alterar o código,
onboarding de novos desenvolvedores prejudicado.

---

## Resumo de Severidades

| Código | Anti-Pattern                   | Severidade |
|--------|-------------------------------|------------|
| AP-01  | God Class / God File          | CRITICAL   |
| AP-02  | Hardcoded Credentials         | CRITICAL   |
| AP-03  | SQL Injection                 | CRITICAL   |
| AP-04  | Business Logic in Routes      | HIGH       |
| AP-05  | N+1 Query Problem             | MEDIUM     |
| AP-06  | Missing Input Validation      | MEDIUM     |
| AP-07  | Duplicate Code / DRY          | MEDIUM     |
| AP-08  | Deprecated API Usage          | MEDIUM     |
| AP-09  | Global Mutable State          | HIGH       |
| AP-10  | Missing Error Handling        | HIGH       |
| AP-11  | Magic Numbers                 | LOW        |
| AP-12  | Poor Naming / Readability     | LOW        |