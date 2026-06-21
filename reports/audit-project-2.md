============================================
# ARCHITECTURE AUDIT REPORT
Project: ecommerce-api-legacy
============================================

**Stack**:   JavaScript (Node.js) + Express v4.18.2
**Files**:   3 analyzed | ~180 lines of code
**Date**:    2026-06-20

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 3 | LOW: 2

Total findings: 13

## Findings

### [CRITICAL] God Class / God File
File: src/AppManager.js:4-141
Description: A classe `AppManager` concentra responsabilidades de todas as camadas:
criação de schema (`initDb`), seeds, registro de rotas HTTP (`setupRoutes`), regras de
negócio (decisão de pagamento, criação de usuário) e acesso direto ao SQLite — tudo em
um único arquivo de 141 linhas.
Evidence:
linha 25: setupRoutes(app) {
linha 37: this.db.get("SELECT * FROM courses WHERE id = ? AND active = 1", ...)
linha 47: let status = cc.startsWith("4") ? "PAID" : "DENIED";
Impact: Impossível testar qualquer regra de negócio em isolamento; qualquer mudança em
rota, schema ou regra de pagamento toca o mesmo arquivo, gerando alto acoplamento e risco
de regressão.
Recommendation: Quebrar em Models (acesso a dados), Controllers (orquestração) e Routes
(roteamento). Aplicar Playbook MODEL-01, CTRL-01 e ROUTE-01.

### [CRITICAL] Hardcoded Credentials / Secrets
File: src/utils.js:1-7
Description: O objeto `config` contém credenciais de banco de produção, chave de gateway
de pagamento e usuário SMTP hardcoded como string literais no código-fonte.
Evidence:
linha 3: dbPass: "senha_super_secreta_prod_123",
linha 4: paymentGatewayKey: "pk_live_1234567890abcdef",
Impact: Qualquer pessoa com acesso ao repositório obtém credenciais de produção e a chave
LIVE do gateway de pagamento, permitindo fraude financeira e comprometimento total.
Recommendation: Extrair para variáveis de ambiente via `dotenv` + `.env.example`, criando
`src/config/settings.js` que lê de `process.env` (Playbook ENV-01).

### [CRITICAL] Sensitive Data Exposure in Logs
File: src/AppManager.js:45
Description: O número completo do cartão de crédito (`cc`) e a chave do gateway de pagamento
são impressos em `console.log` durante o checkout.
Evidence:
linha 45: console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
Impact: Dados de cartão (PCI-DSS) e secret de pagamento vazam para logs/stdout, violando
compliance e expondo dados sensíveis a qualquer um com acesso aos logs.
Recommendation: Remover o log de dados sensíveis; nunca logar PAN de cartão nem secrets.
Mover a lógica de pagamento para um Model/Service dedicado (Playbook MODEL-01).

### [CRITICAL] Broken / Insecure Password Hashing
File: src/utils.js:17-23, src/AppManager.js:68
Description: A função `badCrypto` "hasheia" senhas com base64 truncado em 10 caracteres —
não é criptografia, é reversível e colidível. Além disso há senha em texto plano nos seeds
(`'123'`).
Evidence:
linha 17: function badCrypto(pwd) {
linha 21: hash += Buffer.from(pwd).toString('base64').substring(0, 2);
Impact: Senhas dos usuários ficam efetivamente desprotegidas; um vazamento do banco expõe
contas imediatamente. base64 não é hash.
Recommendation: Substituir por `bcrypt`/`argon2` com salt. Isolar em `UserModel`
(Playbook MODEL-01).

### [HIGH] Business Logic in Routes / Controllers
File: src/AppManager.js:28-78
Description: A rota `POST /api/checkout` contém toda a regra de negócio inline: validação,
busca de curso, criação condicional de usuário, decisão de aprovação de pagamento, inserção
de matrícula, pagamento e log — aninhados em callbacks dentro do handler de rota.
Evidence:
linha 47: let status = cc.startsWith("4") ? "PAID" : "DENIED";
linha 50: this.db.run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", ...)
Impact: Regra de aprovação de pagamento e fluxo de matrícula não podem ser reutilizados nem
testados; mudanças exigem editar o handler HTTP.
Recommendation: Extrair para `CheckoutController` + `EnrollmentModel`/`PaymentModel`
(Playbook CTRL-01 e MODEL-01).

### [HIGH] Global Mutable State
File: src/utils.js:9-15, 25
Description: `globalCache` e `totalRevenue` são variáveis globais mutáveis no nível do
módulo, modificadas por `logAndCache` e compartilhadas entre todas as requisições.
Evidence:
linha 9: let globalCache = {};
linha 13: globalCache[key] = data;
Impact: Estado compartilhado entre requests gera race conditions, vazamento de dados entre
usuários e testes não-determinísticos; em memória, cresce indefinidamente (memory leak).
Recommendation: Eliminar estado global; usar cache injetável/escopo de request ou remover.
Encapsular dependências (Playbook MODEL-01 / injeção de dependência).

### [HIGH] Missing Error Handling / Inconsistent Responses
File: src/AppManager.js:104-137
Description: Vários callbacks ignoram o parâmetro `err` (ex: `this.db.get(... (err, user)`
sem checar `err`), e o `DELETE /api/users/:id` ignora completamente erros, sempre
respondendo 200. Não há middleware de erro global.
Evidence:
linha 104: this.db.get("SELECT name, email FROM users WHERE id = ?", [enr.user_id], (err, user) => {
linha 133: this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => {
Impact: Erros de banco passam silenciosamente, retornando dados parciais ou status 200
enganoso; falhas ficam invisíveis em produção.
Recommendation: Centralizar tratamento via middleware `errorHandler` (err, req, res, next)
e usar `next(err)` nos controllers (Playbook ERR-01).

### [HIGH] Orphaned Records / Missing Referential Integrity
File: src/AppManager.js:131-137
Description: A rota `DELETE /api/users/:id` remove o usuário sem remover (ou bloquear)
matrículas e pagamentos relacionados — o próprio código admite isso na mensagem de resposta.
Evidence:
linha 133: this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => {
linha 135: res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.");
Impact: Gera dados órfãos em `enrollments` e `payments`, corrompendo a integridade
referencial e o relatório financeiro.
Recommendation: Tratar deleção em cascata/transação no `UserModel`, ou impedir deleção com
dependências (Playbook MODEL-01).

### [MEDIUM] N+1 Query Problem
File: src/AppManager.js:83-128
Description: O relatório financeiro faz uma query de cursos e, para cada curso, uma query de
matrículas; para cada matrícula, uma query de usuário e outra de pagamento — produzindo
N×M queries aninhadas em callbacks com contadores manuais (`coursesPending`/`enrPending`).
Evidence:
linha 89: courses.forEach(c => {
linha 92: this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], ...)
linha 106: this.db.get("SELECT amount, status FROM payments WHERE enrollment_id = ?", ...)
Impact: Número de queries cresce multiplicativamente com o volume de dados, causando lentidão
e risco de timeout; lógica de agregação por callbacks é frágil e difícil de manter.
Recommendation: Substituir por uma única query com JOIN agregando em memória (Playbook
PERF-01), encapsulada em `ReportModel`.

### [MEDIUM] Missing Input Validation
File: src/AppManager.js:29-35
Description: Os campos do checkout são lidos de `req.body` e usados diretamente; só há
checagem de presença (`!u || !e || !cid || !cc`). Não há validação de tipo/formato de
e-mail, de `c_id` numérico nem do número do cartão.
Evidence:
linha 29: let u = req.body.usr;
linha 35: if (!u || !e || !cid || !cc) return res.status(400).send("Bad Request");
Impact: Dados malformados entram no fluxo de pagamento e no banco; ausência de validação
de tipo abre espaço para comportamento inesperado.
Recommendation: Validação explícita de presença, tipo e formato no controller antes de
chamar o model (Playbook VAL-01).

### [MEDIUM] Duplicate Code / DRY Violation
File: src/AppManager.js:38, 54, 84, 92, 104, 106
Description: O padrão de tratamento de erro de DB (`if (err) return res.status(500)...`) e os
acessos repetidos a `this.db`/`self.db` aparecem espalhados em múltiplos callbacks, sem uma
camada de acesso a dados reutilizável.
Evidence:
linha 39: if (err || !course) return res.status(404).send("Curso não encontrado");
linha 54: self.db.run("INSERT INTO payments ...", function(err) {
Impact: Mudança na estratégia de acesso/erro de banco exige editar vários pontos; o
workaround `self`/`this` indica acoplamento ao escopo de callback.
Recommendation: Centralizar acesso a dados em Models com conexão compartilhada e promisify
(Playbook MODEL-01).

### [LOW] Magic Numbers / Magic Values
File: src/AppManager.js:47, src/utils.js:19-22
Description: Valores literais sem nome explicam a regra: aprovação de pagamento por cartão
iniciado em "4", e o loop de 10000 iterações com truncamento em 2/10 caracteres no hashing.
Evidence:
linha 47: let status = cc.startsWith("4") ? "PAID" : "DENIED";
linha 19: for(let i = 0; i < 10000; i++) {
Impact: A regra de negócio (aprovação) e os parâmetros do "hash" ficam ocultos em literais,
dificultando entendimento e manutenção.
Recommendation: Extrair para constantes nomeadas e substituir o hashing por biblioteca
padrão (parte do Playbook MODEL-01 / refatoração de domínio).

### [LOW] Poor Naming / Readability
File: src/AppManager.js:29-33
Description: Variáveis de uma letra e abreviações ambíguas no checkout (`u`, `e`, `p`,
`cid`, `cc`) e nomes de campos não descritivos no payload (`usr`, `eml`, `pwd`, `c_id`,
`card`).
Evidence:
linha 29: let u = req.body.usr;
linha 33: let cc = req.body.card;
Impact: Leitura e revisão mais lentas, maior chance de erro ao alterar o fluxo de pagamento.
Recommendation: Renomear para nomes que revelam intenção (`name`, `email`, `password`,
`courseId`, `cardNumber`) ao mover a lógica para o controller (Playbook CTRL-01).

================================

Total: 13 findings

CRITICAL: 4 | HIGH: 4 | MEDIUM: 3 | LOW: 2
