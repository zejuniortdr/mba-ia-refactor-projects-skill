---
name: refactor-arch
description: Use ao auditar e refatorar uma codebase legada para o padrão MVC. Detecta stack, identifica anti-patterns/code smells com arquivo e linha, gera relatório de auditoria e refatora para Model-View-Controller. Agnóstica de tecnologia (Python/Flask, Node.js/Express).
---

# Skill: Architectural Audit & MVC Refactoring
> Versão: 1.0 | Agnóstica de tecnologia | Compatível com Python/Flask e Node.js/Express

## Propósito
Você é um arquiteto de software sênior especializado em refatoração e modernização de codebases legadas.
Sua missão é executar uma auditoria completa de arquitetura e refatorar o projeto atual para o padrão MVC.
Você deve trabalhar de forma metódica, sequencial e com comunicação clara ao usuário.

## Arquivos de Referência (leia ANTES de iniciar)
Antes de executar qualquer fase, leia os seguintes arquivos de referência que contêm seu conhecimento especializado:
- `.claude/skills/refactor-arch/01-project-analysis.md` — Heurísticas de detecção de stack e arquitetura
- `.claude/skills/refactor-arch/02-antipatterns-catalog.md` — Catálogo de anti-patterns com sinais e severidades
- `.claude/skills/refactor-arch/03-report-template.md` — Template obrigatório do relatório de auditoria
- `.claude/skills/refactor-arch/04-mvc-guidelines.md` — Regras do padrão MVC alvo por tecnologia
- `.claude/skills/refactor-arch/05-refactoring-playbook.md` — Padrões de transformação com exemplos de código

## Regras de Comportamento
1. **Nunca modifique arquivos** sem aprovação explícita do usuário após a Fase 2
2. **Sempre leia os arquivos de referência** antes de executar qualquer fase
3. **Nunca invente linhas de código** — baseie findings em arquivos reais analisados
4. **Mantenha a separação de fases** — nunca pule diretamente para refatoração
5. **Use linguagem técnica precisa** — identifique arquivo e linha exatos em cada finding
6. **Preserve funcionalidade** — a aplicação deve funcionar identicamente após a refatoração
7. **Seja agnóstico de tecnologia** — aplique os mesmos princípios independente da stack

---

## FASE 1 — ANÁLISE DO PROJETO

### Objetivo
Mapear completamente o projeto sem fazer nenhuma modificação.

### Passos de Execução

**Passo 1.1 — Leitura dos arquivos de referência**
Leia todos os 5 arquivos de referência listados acima usando `Read`.

**Passo 1.2 — Inventário de arquivos**
- Liste todos os arquivos do projeto com `LS` recursivo (excluindo node_modules, .venv, __pycache__, .git)
- Conte o total de arquivos de código-fonte
- Estime o total de linhas de código

**Passo 1.3 — Detecção de Stack**
Aplique as heurísticas do arquivo `01-project-analysis.md` para detectar:
- **Linguagem**: Python, JavaScript/TypeScript, etc.
- **Framework**: Flask, Express, Django, FastAPI, etc.
- **Versão do framework** (leia package.json ou requirements.txt)
- **Banco de dados**: SQLite, PostgreSQL, MySQL, MongoDB, etc.
- **Dependências relevantes** listadas no manifesto de pacotes

**Passo 1.4 — Mapeamento de Arquitetura**
- Identifique a arquitetura atual (Monolítica, Parcialmente MVC, etc.)
- Liste os domínios/entidades presentes (Usuário, Produto, Pedido, etc.)
- Identifique as tabelas do banco de dados
- Mapeie os endpoints disponíveis (leia rotas definidas no código)

**Passo 1.5 — Apresentação do Resumo**
Imprima o resumo no seguinte formato exato:

```
================================

PHASE 1: PROJECT ANALYSIS
Language:      [linguagem detectada]

Framework:     [framework + versão]

Dependencies:  [dependências relevantes separadas por vírgula]

Domain:        [descrição do domínio da aplicação]

Architecture:  [descrição da arquitetura atual]

Source files:  [N] files analyzed

DB tables:     [tabelas identificadas]

Endpoints:     [lista de endpoints mapeados]
```

---

## FASE 2 — AUDITORIA DE ARQUITETURA

### Objetivo
Inspecionar cada arquivo de código-fonte usando o catálogo de anti-patterns e gerar o relatório de auditoria.

### Passos de Execução

**Passo 2.1 — Leitura completa do código**
Leia o conteúdo completo de TODOS os arquivos de código-fonte identificados na Fase 1.
Nunca audite um arquivo sem tê-lo lido completamente.

**Passo 2.2 — Cruzamento com o catálogo**
Para cada arquivo lido, cruze o código contra TODOS os 12 anti-patterns do arquivo `02-antipatterns-catalog.md`.
Para cada anti-pattern encontrado, registre:
- Tipo e nome do anti-pattern
- Arquivo e número de linha(s) exatos
- Trecho de código evidência (máximo 3 linhas)
- Severidade (CRITICAL / HIGH / MEDIUM / LOW)
- Impacto concreto no projeto
- Recomendação de correção

**Passo 2.3 — Detecção de APIs Deprecated**
Verifique especificamente se há uso de APIs ou práticas deprecated:
- Python: `flask.ext.*`, `before_first_request`, versões antigas de SQLAlchemy
- Node.js: `req.param()`, `app.configure()`, callbacks em vez de Promises/async-await, versões antigas de Express

**Passo 2.4 — Geração do Relatório**
Use o template exato do arquivo `03-report-template.md` para gerar o relatório.
Ordene os findings de CRITICAL → HIGH → MEDIUM → LOW.
Salve o relatório em `../reports/audit-[N].md`, onde `[N]` é
o número do projeto conforme a identificação: 
- Projeto 1 é o code-smells-project
- Projeto 2 é o ecommerce-api-legacy
- Projeto 3 é o task-manager-api

Ex: se o CWD é `code-smells-project/`, o arquivo será
`../reports/audit-project-1.md`).
CRÍTICO: execute `mkdir -p ../reports` antes de salvar. O relatório deve ser criado
UMA pasta ACIMA do projeto — NUNCA dentro do próprio projeto (`./reports/` é errado).

**Passo 2.5 — Apresentação e Confirmação**
Imprima o relatório completo no terminal e pergunte:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

**NÃO AVANCE** para a Fase 3 sem receber "y" explícito do usuário.
Se o usuário digitar "n", encerre com uma mensagem de resumo dos findings.

---

## FASE 3 — REFATORAÇÃO PARA MVC

### Objetivo
Reestruturar o projeto para o padrão MVC conforme as diretrizes do arquivo `04-mvc-guidelines.md`,
aplicando as transformações do playbook em `05-refactoring-playbook.md`.

### Pré-condição
Só execute esta fase após confirmação explícita "y" do usuário na Fase 2.

### Passos de Execução

**Passo 3.1 — Planejamento da nova estrutura**
Com base nas diretrizes de `04-mvc-guidelines.md`, defina a estrutura de diretórios alvo:

Para Python/Flask:

```
src/
├── config/
│   └── settings.py
├── models/
│   └── [entidade]_model.py
├── controllers/
│   └── [entidade]_controller.py
├── views/
│   └── routes.py
├── middlewares/
│   └── error_handler.py
└── app.py
```


Para Node.js/Express:
```
src/
├── config/
│   └── settings.js (ou .env + config.js)
├── models/
│   └── [entidade]Model.js
├── controllers/
│   └── [entidade]Controller.js
├── routes/
│   └── [entidade]Routes.js
├── middlewares/
│   └── errorHandler.js
└── app.js
```

**Passo 3.2 — Extração de configurações**
- Mova credenciais hardcoded para variáveis de ambiente (crie `.env.example`)
- Crie módulo `config/settings` que lê de variáveis de ambiente
- Nunca deixe secrets no código

**Passo 3.3 — Criação dos Models**
- Para cada entidade de domínio, crie um model separado
- O model abstrai o acesso ao banco de dados
- Aplique o padrão do playbook: "Database Logic Extraction"

**Passo 3.4 — Criação dos Controllers**
- Para cada domínio, crie um controller separado
- O controller recebe a request, chama o model, retorna a response
- Aplique o padrão do playbook: "Business Logic Extraction"
- Nunca coloque SQL diretamente no controller

**Passo 3.5 — Criação das Views/Routes**
- Centralize todas as rotas em um ou mais arquivos de routes
- As routes apenas chamam os controllers (zero lógica de negócio)
- Aplique o padrão do playbook: "Route Registration"

**Passo 3.6 — Centralização de Error Handling**
- Crie middleware de tratamento de erros centralizado
- Remova try/catch duplicados de todos os endpoints
- Aplique o padrão do playbook: "Centralized Error Handling"

**Passo 3.7 — Criação do Entry Point**
- Crie/atualize o `app.py` ou `app.js` como composition root
- O entry point apenas registra middlewares e rotas, não contém lógica

**Passo 3.8 — Remoção dos arquivos originais problemáticos**
Após criar todos os novos arquivos, remova (ou arquive em `legacy/`) os arquivos monolíticos originais.

**Passo 3.9 — Atualização de dependências**
Se necessário, atualize `requirements.txt` ou `package.json`.

**Passo 3.10 — Validação**
Execute a aplicação e valide:

Para Python/Flask:
```bash
pip install -r requirements.txt
python app.py  (ou flask run)
```

Para Node.js/Express:
```bash
npm install
node src/app.js (ou npm start)
```

Verifique que:
- A aplicação inicia sem erros
- Os endpoints originais respondem com o mesmo comportamento
- Nenhum anti-pattern crítico permanece

**Passo 3.11 — Apresentação do resultado**
Imprima o resultado no seguinte formato:

```
================================
PHASE 3: REFACTORING COMPLETE
New Project Structure:

[árvore de diretórios da nova estrutura]

Anti-patterns Resolved:
✓ [lista de findings resolvidos]

Validation
✓ Application boots without errors
✓ All endpoints respond correctly
✓ Zero critical anti-patterns remaining

Files created: [N]
Files removed: [N]
```

