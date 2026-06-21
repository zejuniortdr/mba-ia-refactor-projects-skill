============================================
# ARCHITECTURE AUDIT REPORT
Project: task-manager-api
============================================

**Stack**:   Python 3 + Flask v3.0.0 (Flask-SQLAlchemy v3.1.1, SQLite)
**Files**:   15 Python files analyzed | ~1.167 lines of code
**Date**:    2026-06-20

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 5 | LOW: 2

Total findings: 16

---

## Findings

### [CRITICAL] Hardcoded Secret Key (AP-02)
File: app.py:13
Description: A `SECRET_KEY` da aplicação Flask está hardcoded como string literal
`'super-secret-key-123'`, exposta diretamente no código-fonte e versionada no git.
Evidence:
```
linha 13: app.config['SECRET_KEY'] = 'super-secret-key-123'
linha 11: app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
```
Impact: Qualquer pessoa com acesso ao repositório pode forjar sessões/assinaturas
da aplicação, comprometendo a segurança. A URI do banco também está hardcoded,
impedindo configuração por ambiente.
Recommendation: Extrair para variáveis de ambiente via `python-dotenv` (já em
requirements.txt) e módulo `config/settings.py` (Playbook: ENV-01).

### [CRITICAL] Hardcoded Email Credentials (AP-02)
File: services/notification_service.py:7-10
Description: O `NotificationService` contém host, usuário e senha de SMTP escritos
diretamente no construtor, incluindo `email_password = 'senha123'`.
Evidence:
```
linha 8:  self.email_host = 'smtp.gmail.com'
linha 9:  self.email_user = 'taskmanager@gmail.com'
linha 10: self.email_password = 'senha123'
```
Impact: Vazamento de credenciais de e-mail no repositório; comprometimento da conta
SMTP e possibilidade de envio de e-mails fraudulentos em nome da aplicação.
Recommendation: Mover para variáveis de ambiente lidas em `config/settings.py`
(Playbook: ENV-01).

### [CRITICAL] God File — Route concentra todas as camadas (AP-01)
File: routes/task_routes.py:1-300
Description: O arquivo de rotas de tasks (300 linhas) concentra roteamento HTTP,
validação de entrada, regras de negócio (cálculo de overdue, completion_rate),
acesso a dados (queries) e montagem manual de dicionários de resposta — todas as
camadas no mesmo lugar. Ex.: `get_tasks` (linhas 11-63) faz query, monta dict campo a
campo, calcula overdue e dispara queries de User/Category na mesma função.
Evidence:
```
linha 14:  tasks = Task.query.all()
linha 30:  if t.due_date:            # regra de negócio dentro da rota
linha 42:  user = User.query.get(t.user_id)   # acesso a dados dentro da rota
```
Impact: Impossível testar a lógica isoladamente; qualquer mudança de regra exige
editar as rotas; alta probabilidade de regressão.
Recommendation: Separar em Model (acesso a dados), Controller (orquestração) e
Routes (apenas mapeamento) — Playbook MODEL-01, CTRL-01, ROUTE-01.

### [CRITICAL] God File — Relatórios + CRUD de Categorias no mesmo arquivo (AP-01)
File: routes/report_routes.py:1-224
Description: O arquivo mistura dois domínios distintos: geração de relatórios
(`summary_report`, `user_report`) e o CRUD completo de Categorias
(`get_categories`, `create_category`, `update_category`, `delete_category`),
com lógica de agregação, acesso a dados e formatação juntos.
Evidence:
```
linha 13:  def summary_report():     # ~90 linhas de agregação
linha 158: def get_categories():     # domínio Category misturado em report_routes
linha 168: def create_category():
```
Impact: Baixa coesão; o domínio Category fica "escondido" no arquivo de reports;
arquivo difícil de navegar e manter.
Recommendation: Separar `category` em seu próprio model/controller/routes e
extrair a lógica de agregação dos reports para um controller/service
(Playbook MODEL-01, CTRL-01, ROUTE-01).

---

### [HIGH] Business Logic in Routes — Relatório de agregação (AP-04)
File: routes/report_routes.py:12-101
Description: `summary_report` implementa ~90 linhas de lógica de negócio na rota:
contagens por status/prioridade, cálculo de overdue, atividade recente e produtividade
por usuário, montando o relatório inteiro dentro do handler HTTP.
Evidence:
```
linha 33:  for t in all_tasks:           # loop de regra de negócio na rota
linha 55:  for u in users:               # produtividade por usuário na rota
linha 67:  'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0
```
Impact: Lógica não reutilizável nem testável; duplicação com `task_stats` e
`user_report`; regra de "overdue" reescrita várias vezes.
Recommendation: Extrair para um `report_controller`/model que calcule as métricas;
a rota apenas chama e retorna (Playbook CTRL-01).

### [HIGH] Business Logic in Routes — Stats e relatório de usuário (AP-04)
File: routes/task_routes.py:273-299 ; routes/report_routes.py:103-155
Description: `task_stats` e `user_report` calculam contagens, overdue e
`completion_rate` diretamente nas rotas, com loops sobre todas as tasks.
Evidence:
```
task_routes.py:283  for t in all_tasks:
task_routes.py:296  'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
report_routes.py:119 for t in tasks:    # contagem por status na rota
```
Impact: Mesma regra replicada em 3 endpoints; mudança de definição de "overdue" ou
de "completion_rate" exige editar vários lugares.
Recommendation: Centralizar cálculos no model `Task` / controller de reports
(Playbook CTRL-01, MODEL-01).

### [HIGH] Missing / Poor Error Handling (AP-10)
File: app.py:34 ; routes/task_routes.py:62,137,236 ; routes/user_routes.py:130,149 ; routes/report_routes.py:187,207,221
Description: `app.run(debug=True, host='0.0.0.0')` expõe o debugger Werkzeug em
produção. Há múltiplos `except:` "pelados" que engolem qualquer exceção retornando
mensagem genérica, e vários endpoints (`get_task`, `search_tasks`, `task_stats`,
`summary_report`, `get_users`) sem nenhum tratamento. Não existe handler de erro
centralizado.
Evidence:
```
app.py:34            app.run(debug=True, host='0.0.0.0', port=5000)
task_routes.py:62    except:
                         return jsonify({'error': 'Erro interno'}), 500
```
Impact: `debug=True` permite execução remota de código via console do Werkzeug;
`except:` mascara bugs reais e dificulta diagnóstico; rotas sem try/except podem
crashar o request.
Recommendation: Desativar debug por env; criar middleware `error_handler` com
`@app.errorhandler` e classe `AppError`; remover try/except duplicados das rotas
(Playbook ERR-01).

### [HIGH] Weak Password Hashing & Hash Exposure (AP-02 / Segurança)
File: models/user.py:23-32
Description: Senhas são hasheadas com MD5 (sem salt) em `set_password`/`check_password`,
e `to_dict()` inclui o campo `password` (o hash) na resposta, que é retornado por
endpoints como `GET /users/<id>`, `POST /users` e `/login`.
Evidence:
```
linha 24:  'password': self.password,        # hash exposto na API
linha 29:  self.password = hashlib.md5(pwd.encode()).hexdigest()
linha 32:  return self.password == hashlib.md5(pwd.encode()).hexdigest()
```
Impact: MD5 é criptograficamente quebrado e sem salt é vulnerável a rainbow tables;
expor o hash na resposta facilita ataques offline.
Recommendation: Usar `werkzeug.security.generate_password_hash`/`check_password_hash`
(ou bcrypt) e remover `password` do `to_dict()` (serializer no model).

### [HIGH] Global Mutable State em serviço (AP-09)
File: services/notification_service.py:5-6,31-36,43-48
Description: `NotificationService` mantém estado mutável em memória
(`self.notifications = []`) usado como armazenamento de notificações. Concebido como
serviço compartilhado, não é thread-safe e perde dados a cada restart.
Evidence:
```
linha 6:   self.notifications = []
linha 31:  self.notifications.append({...})   # mutação de estado em memória
```
Impact: Em ambiente multi-thread/multi-worker gera race conditions e resultados
inconsistentes; notificações somem entre processos/reinícios.
Recommendation: Persistir notificações no banco (model dedicado) ou usar store
externo; evitar estado mutável compartilhado no processo.

---

### [MEDIUM] N+1 Query Problem — listagem de tasks (AP-05)
File: routes/task_routes.py:41-57
Description: `get_tasks` itera sobre todas as tasks e, para cada uma, dispara
`User.query.get` e `Category.query.get`, gerando N+1 queries.
Evidence:
```
linha 16:  for t in tasks:
linha 42:  user = User.query.get(t.user_id)
linha 51:  cat = Category.query.get(t.category_id)
```
Impact: Performance degrada linearmente com o número de tasks; lento sob volume.
Recommendation: Usar eager loading (`joinedload`) ou JOIN único e acessar
`t.user`/`t.category` via relationship já definida (Playbook PERF-01).

### [MEDIUM] N+1 Query Problem — relatórios e categorias (AP-05)
File: routes/report_routes.py:55-68 ; routes/report_routes.py:161-164
Description: `summary_report` faz uma query de tasks por usuário dentro do loop de
usuários; `get_categories` faz um `count()` por categoria dentro do loop.
Evidence:
```
report_routes.py:56  user_tasks = Task.query.filter_by(user_id=u.id).all()
report_routes.py:163 cat_data['task_count'] = Task.query.filter_by(category_id=c.id).count()
```
Impact: Número de queries cresce com usuários/categorias; relatório fica caro.
Recommendation: Agregar com `GROUP BY` em uma única query por métrica (Playbook PERF-01).

### [MEDIUM] Duplicate Code / DRY Violation — lógica de "overdue" (AP-07)
File: routes/task_routes.py:30-39,71-80,283-287 ; routes/user_routes.py:171-180 ; routes/report_routes.py:33-37,132-135
Description: O bloco aninhado que decide se uma task está atrasada
(`if due_date < now and status not in done/cancelled`) é reescrito em ~6 lugares.
O model `Task.is_overdue()` (models/task.py:50-60) já implementa exatamente isso,
mas não é usado por nenhuma rota.
Evidence:
```
task_routes.py:31  if t.due_date < datetime.utcnow():
task_routes.py:32      if t.status != 'done' and t.status != 'cancelled':
models/task.py:50  def is_overdue(self):   # já existe, ignorado
```
Impact: Mudança na definição de "atrasada" exige editar 6 trechos; risco de
divergência. Também há montagem manual de dict duplicando `to_dict()`.
Recommendation: Usar `Task.is_overdue()` no model e expor via `to_dict()`; remover
as cópias (Playbook MODEL-01).

### [MEDIUM] Missing Input Validation — casts inseguros (AP-06)
File: routes/task_routes.py:261,264 ; routes/task_routes.py:113
Description: `search_tasks` converte `priority` e `user_id` com `int(...)` sem
validação, lançando `ValueError` (e 500) em entrada não numérica. Em `create_task`,
`priority` é comparado com `< 1`/`> 5` sem garantir que seja inteiro.
Evidence:
```
linha 261: tasks = tasks.filter(Task.priority == int(priority))
linha 264: tasks = tasks.filter(Task.user_id == int(user_id))
linha 113: if priority < 1 or priority > 5:   # priority pode vir como string
```
Impact: Requisições com query params inválidos derrubam o endpoint com erro 500
não tratado.
Recommendation: Validar/coagir tipos com tratamento de erro no controller e
retornar 400 (Playbook VAL-01).

### [MEDIUM] Deprecated API Usage (AP-08)
File: routes/task_routes.py (vários) ; routes/user_routes.py (vários) ; models/*.py
Description: Uso pervasivo de `Model.query.get(id)` (Legacy Query API, deprecada no
SQLAlchemy 2.0 — usar `db.session.get(Model, id)`) e de `datetime.utcnow()`
(deprecada no Python 3.12 — usar `datetime.now(timezone.utc)`).
Evidence:
```
task_routes.py:67   task = Task.query.get(task_id)
task_routes.py:31   if t.due_date < datetime.utcnow():
```
Impact: Warnings de depreciação e quebra futura em upgrades de SQLAlchemy/Python.
Recommendation: Migrar para `db.session.get(...)` e `datetime.now(timezone.utc)`
durante a extração de models.

---

### [LOW] Magic Numbers (AP-11)
File: routes/task_routes.py:96-114,182-183 ; routes/user_routes.py:64,116 ; routes/report_routes.py:45,129
Description: Limiares e fatores numéricos soltos: tamanho de título (3/200),
faixa de prioridade (1..5), tamanho mínimo de senha (4), `priority <= 2` para
"high_priority", `timedelta(days=7)`, `* 100` no completion_rate. O arquivo
`utils/helpers.py:110-116` já define `MAX_TITLE_LENGTH`, `MIN_PASSWORD_LENGTH`,
etc., mas as rotas não os utilizam.
Impact: Mudança de regra exige caçar números repetidos; risco de inconsistência.
Recommendation: Reaproveitar as constantes de `helpers.py` (ou config) em todos os
pontos de validação.

### [LOW] Poor Naming / Readability (AP-12)
File: routes/report_routes.py:24-28 ; models/category.py:14 ; seed.py:78
Description: Identificadores pouco descritivos: `p1..p5` para contagens por
prioridade, `d` como retorno de `to_dict`, `td`/`t`/`u`/`c` em loops não triviais,
`pwd` em `User`.
Impact: Leitura e manutenção mais lentas; intenção não explícita.
Recommendation: Renomear para nomes intencionais (ex.: `priority_1_count`,
`category_dict`); aplicar durante a extração de models/controllers.

================================

Total: 16 findings

CRITICAL: 4 | HIGH: 5 | MEDIUM: 5 | LOW: 2
