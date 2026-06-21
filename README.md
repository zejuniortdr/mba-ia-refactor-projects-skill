# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---
---

# 📦 Documentação da Entrega

> Tudo acima é o enunciado original do desafio. A partir daqui está a documentação da solução
> entregue: skill `refactor-arch` (Claude Code) executada nos 3 projetos.

## A) Análise Manual

Análise manual dos três projetos antes da construção da skill. Os achados abaixo são os
problemas de maior impacto arquitetural/segurança identificados em cada codebase — os mesmos
que a skill precisou aprender a detectar.

### Projeto 1 — `code-smells-project` (Python/Flask — E-commerce API)

Monolito de 4 arquivos (~784 linhas), tudo misturado, sem qualquer separação de camadas.

| # | Problema | Severidade | Arquivo | Por que é relevante |
|---|---|---|---|---|
| 1 | SQL Injection generalizado (queries por concatenação de string) | **CRITICAL** | `models.py` (toda) | Permite burlar login (`' OR '1'='1`), exfiltrar e destruir a base via qualquer endpoint com parâmetro. |
| 2 | Endpoint `POST /admin/query` executa SQL arbitrário sem auth | **CRITICAL** | `app.py:59-78` | RCE sobre o banco exposto por HTTP a qualquer anônimo. |
| 3 | `SECRET_KEY` hardcoded + vazada no `/health` + senhas em texto puro | **CRITICAL** | `app.py:7`, `controllers.py:289`, `database.py:76-78` | Comprometimento de sessões e contas; segredo versionado no git. |
| 4 | God File / responsabilidades misturadas (dados + negócio + roteamento) | **CRITICAL** | `models.py:1-315`, `app.py:47-78` | Impossível testar regras isoladamente; qualquer mudança afeta tudo. |
| 5 | Lógica de negócio e efeitos colaterais (notificações) dentro de controllers | **HIGH** | `controllers.py:188-255` | Regras e notificações não reutilizáveis nem testáveis. |
| 6 | Conexão de banco como estado global mutável (`check_same_thread=False`) | **HIGH** | `database.py:4-12` | Race conditions e cursores compartilhados entre requests concorrentes. |
| 7 | `DEBUG=True` fixo + `str(e)` vazado ao cliente, sem error handler central | **HIGH** | `app.py:8,88`, `controllers.py` (todos os `except`) | Console Werkzeug (RCE) e vazamento de detalhes internos. |
| 8 | N+1 Query em listagem de pedidos/itens | **MEDIUM** | `models.py:171-233` | 1 + N + N×M queries; degradação exponencial sob volume. |
| 9 | Validação de entrada ausente/inconsistente | **MEDIUM** | `controllers.py:167-245` | Requisições malformadas viram 500 em vez de 400. |
| 10 | Duplicação (boilerplate de conexão e try/except em ~16 funções) | **MEDIUM** | `models.py`, `controllers.py` | Mudança de conexão/erro exige editar dezenas de pontos. |
| 11 | Magic numbers nas faixas de desconto | **LOW** | `models.py:256-262` | Significado dos valores oculto; regra difícil de alterar. |
| 12 | Nomenclatura ruim (`cursor2`, `cursor3`, `id` sombreando builtin) | **LOW** | `models.py`, `controllers.py` | Leitura/revisão mais lentas e propensas a erro. |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express — LMS API com checkout)

Monolito orientado a callbacks (~180 linhas) com uma única classe `AppManager` fazendo tudo.

| # | Problema | Severidade | Arquivo | Por que é relevante |
|---|---|---|---|---|
| 1 | God Class `AppManager` (schema + seeds + rotas + negócio + dados) | **CRITICAL** | `src/AppManager.js:4-141` | Acoplamento total; nada testável em isolamento. |
| 2 | Credenciais de produção e chave LIVE do gateway hardcoded | **CRITICAL** | `src/utils.js:1-7` | Fraude financeira e comprometimento total a partir do repositório. |
| 3 | Número de cartão + secret do gateway impressos em `console.log` | **CRITICAL** | `src/AppManager.js:45` | Violação de PCI-DSS; PAN e segredo vazam para logs. |
| 4 | "Hash" de senha com base64 truncado (`badCrypto`) + senha em texto nos seeds | **CRITICAL** | `src/utils.js:17-23` | Senhas reversíveis; vazamento do banco expõe contas. |
| 5 | Regra de negócio do checkout inline na rota (callbacks aninhados) | **HIGH** | `src/AppManager.js:28-78` | Fluxo de pagamento/matrícula não reutilizável nem testável. |
| 6 | Estado global mutável (`globalCache`, `totalRevenue`) | **HIGH** | `src/utils.js:9-15,25` | Race conditions, vazamento entre usuários e memory leak. |
| 7 | Erros de DB ignorados; `DELETE /users` sempre responde 200 | **HIGH** | `src/AppManager.js:104-137` | Falhas silenciosas e status enganoso em produção. |
| 8 | Deleção de usuário gera registros órfãos (sem integridade referencial) | **HIGH** | `src/AppManager.js:131-137` | Corrompe `enrollments`/`payments` e o relatório financeiro. |
| 9 | N+1 Query no relatório financeiro (cursos→matrículas→usuário→pagamento) | **MEDIUM** | `src/AppManager.js:83-128` | Queries crescem multiplicativamente; risco de timeout. |
| 10 | Validação de entrada ausente (só checa presença) | **MEDIUM** | `src/AppManager.js:29-35` | Dados malformados entram no fluxo de pagamento. |
| 11 | Duplicação do tratamento de erro de DB espalhado em callbacks | **MEDIUM** | `src/AppManager.js` (vários) | Mudança de estratégia exige editar vários pontos. |
| 12 | Magic values (`cc.startsWith("4")`, loop de 10000 no "hash") | **LOW** | `src/AppManager.js:47`, `src/utils.js:19-22` | Regra de aprovação oculta em literais. |
| 13 | Nomenclatura ruim (`u`, `e`, `cc`, `usr`, `eml`) | **LOW** | `src/AppManager.js:29-33` | Leitura mais lenta no fluxo crítico de pagamento. |

### Projeto 3 — `task-manager-api` (Python/Flask — Task Manager API)

Projeto **parcialmente organizado** (models, routes, services, utils com Flask-SQLAlchemy,
~1.167 linhas), mas com separação apenas superficial — as rotas concentram todas as camadas.

| # | Problema | Severidade | Arquivo | Por que é relevante |
|---|---|---|---|---|
| 1 | `SECRET_KEY` e URI do banco hardcoded | **CRITICAL** | `app.py:11,13` | Permite forjar sessões; impede config por ambiente. |
| 2 | Credenciais de SMTP hardcoded (`email_password='senha123'`) | **CRITICAL** | `services/notification_service.py:7-10` | Comprometimento da conta de e-mail a partir do repositório. |
| 3 | God File: rotas de tasks concentram todas as camadas (300 linhas) | **CRITICAL** | `routes/task_routes.py:1-300` | Lógica não testável; alto risco de regressão. |
| 4 | God File: relatórios + CRUD de categorias no mesmo arquivo | **CRITICAL** | `routes/report_routes.py:1-224` | Baixa coesão; domínio Category escondido em reports. |
| 5 | ~90 linhas de regra de negócio dentro do handler de relatório | **HIGH** | `routes/report_routes.py:12-101` | Lógica não reutilizável, duplicada com outros endpoints. |
| 6 | Cálculos de stats/overdue/completion_rate replicados nas rotas | **HIGH** | `task_routes.py:273-299`, `report_routes.py:103-155` | Mesma regra em 3 endpoints; mudança exige editar vários. |
| 7 | `debug=True` em produção + `except:` pelados + rotas sem tratamento | **HIGH** | `app.py:34`, rotas (várias) | RCE via console Werkzeug; bugs mascarados. |
| 8 | Hash de senha com MD5 sem salt + hash exposto no `to_dict()` | **HIGH** | `models/user.py:23-32` | MD5 quebrado; expor hash facilita ataque offline. |
| 9 | Estado mutável em memória no `NotificationService` | **HIGH** | `services/notification_service.py:5-6` | Não thread-safe; perde dados a cada restart. |
| 10 | N+1 Query na listagem de tasks (User/Category por item) | **MEDIUM** | `routes/task_routes.py:41-57` | Performance degrada linearmente com o volume. |
| 11 | N+1 Query em relatórios e contagem de categorias | **MEDIUM** | `routes/report_routes.py:55-68,161-164` | Relatório fica caro com mais usuários/categorias. |
| 12 | Duplicação da lógica de "overdue" em ~6 lugares (model `is_overdue()` ignorado) | **MEDIUM** | rotas (várias), `models/task.py:50-60` | Risco de divergência; método pronto não é usado. |
| 13 | Casts inseguros (`int(...)`) sem validação → 500 | **MEDIUM** | `routes/task_routes.py:113,261,264` | Query params inválidos derrubam o endpoint. |
| 14 | **Deprecated API**: `Model.query.get()` (SQLAlchemy 2.0) e `datetime.utcnow()` (Python 3.12) | **MEDIUM** | rotas e models (vários) | Warnings de depreciação e quebra futura em upgrades. |
| 15 | Magic numbers de validação (constantes em `helpers.py` ignoradas) | **LOW** | rotas (várias), `utils/helpers.py:110-116` | Regras espalhadas; constantes prontas não reaproveitadas. |
| 16 | Nomenclatura ruim (`p1..p5`, `d`, `td`, `pwd`) | **LOW** | `report_routes.py`, `models/category.py` | Intenção não explícita; manutenção mais lenta. |

---

## B) Construção da Skill

### Estrutura do `SKILL.md` e dos arquivos de referência

O `SKILL.md` foi escrito como um **prompt orquestrador**: define o papel (arquiteto sênior),
as regras de comportamento e as **3 fases sequenciais** (Análise → Auditoria → Refatoração),
mas delega todo o conhecimento de domínio a 5 arquivos de referência em Markdown. Isso mantém
o `SKILL.md` enxuto e focado em *o que fazer*, enquanto os arquivos de referência fornecem
*como reconhecer e corrigir*:

| Arquivo | Área de conhecimento | Conteúdo |
|---|---|---|
| `01-project-analysis.md` | Análise de projeto | Heurísticas para detectar linguagem, framework, versão, banco e mapear arquitetura/domínio. |
| `02-antipatterns-catalog.md` | Catálogo de anti-patterns | 12 anti-patterns (AP-01..AP-12) com sinais de detecção e severidade. |
| `03-report-template.md` | Template de relatório | Formato padronizado do relatório de auditoria da Fase 2. |
| `04-mvc-guidelines.md` | Guidelines de arquitetura | Regras do MVC alvo (Models/Views-Routes/Controllers) por stack. |
| `05-refactoring-playbook.md` | Playbook de refatoração | 8 padrões de transformação com exemplos antes/depois. |

### Anti-patterns incluídos no catálogo e por quê

Foram catalogados **12 anti-patterns** com severidade distribuída, escolhidos a partir da
análise manual para cobrir os três eixos do desafio — **segurança, arquitetura e qualidade**:

- **CRITICAL** — `AP-01` God Class/File, `AP-02` Hardcoded Credentials, `AP-03` SQL Injection.
- **HIGH** — `AP-04` Business Logic in Controllers, `AP-09` Global Mutable State, `AP-10` Missing Error Handling / Stack Traces expostos.
- **MEDIUM** — `AP-05` N+1 Query, `AP-06` Missing Input Validation, `AP-07` Duplicate Code / DRY, `AP-08` **Deprecated API Usage**.
- **LOW** — `AP-11` Magic Numbers, `AP-12` Poor Naming / Readability.

O `AP-08` atende especificamente o requisito de **detecção de APIs deprecated** (ex.:
`Model.query.get()` do SQLAlchemy legado, `datetime.utcnow()`, `req.param()`/callbacks no
Express), recomendando sempre o equivalente moderno.

### Como a skill garante ser agnóstica de tecnologia

1. **Sinais de detecção, não nomes de arquivo**: o catálogo descreve *padrões* ("query SQL
   montada por concatenação", "estado global mutável no nível de módulo"), que existem tanto
   em Python quanto em JS.
2. **Heurísticas de stack na Fase 1**: a skill lê `requirements.txt`/`package.json` e infere
   linguagem, framework e banco antes de auditar — não assume nada.
3. **Guidelines e playbook com variantes por stack**: `04-mvc-guidelines.md` e o playbook
   trazem a estrutura-alvo tanto para Python/Flask (`views/routes.py`) quanto para
   Node/Express (`routes/*Routes.js`).
4. **Adaptação ao nível de organização**: a skill trata tanto monolito puro (projetos 1 e 2)
   quanto projeto já parcialmente em camadas (projeto 3), propondo só as transformações
   necessárias em cada caso.
5. **Cópia idêntica nos 3 projetos**: a mesma skill (sem ajustes por projeto) roda nas três
   stacks — provando o desacoplamento. A sincronização das cópias é automatizada via
   `make update-skills`, que apenas automatiza a cópia da skill para os projetos, vindas do path `~/.claude/skills` para reutilização.

### Desafios encontrados e como foram resolvidos

- **Caminho do relatório**: a skill precisava salvar em `../reports/` (uma pasta acima do
  projeto) e não dentro dele. Resolvido com instrução explícita no Passo 2.4 (incl.
  `mkdir -p ../reports`) e mapeamento fixo projeto→arquivo.
- **Preservar funcionalidade ao remover monolitos**: os arquivos originais não foram apagados,
  mas **arquivados em `legacy/`** em cada projeto, permitindo comparação antes/depois e rollback.
- **Projeto já organizado (task-manager)**: o risco era a skill "não achar nada". O catálogo
  foi calibrado para detectar problemas mesmo com camadas presentes (God File em rotas, regra
  de negócio nos handlers, deprecated APIs) — resultando em 16 findings.
- **Confirmação obrigatória da Fase 2**: garantida via parada explícita com `[y/n]` antes de
  qualquer escrita, atendendo o requisito de revisão humana.

---

## C) Resultados

### Resumo dos relatórios de auditoria

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | **Total** | Relatório |
|---|---|:---:|:---:|:---:|:---:|:---:|---|
| 1 — code-smells-project | Python/Flask 3.1.1 | 4 | 3 | 3 | 2 | **12** | [audit-project-1.md](reports/audit-project-1.md) |
| 2 — ecommerce-api-legacy | Node.js/Express 4.18 | 4 | 4 | 3 | 2 | **13** | [audit-project-2.md](reports/audit-project-2.md) |
| 3 — task-manager-api | Python/Flask 3.0 (SQLAlchemy) | 4 | 5 | 5 | 2 | **16** | [audit-project-3.md](reports/audit-project-3.md) |

### Comparação antes/depois da estrutura

**Projeto 1 — code-smells-project**
```
ANTES (monolito, 4 arquivos)          DEPOIS (MVC)
app.py        (rotas + admin + SQL)   src/config/settings.py
controllers.py (negócio + try/except) src/models/{database,produto,usuario,pedido}_model.py
models.py     (dados + negócio)       src/controllers/{produto,pedido,usuario,system}_controller.py
database.py   (conexão global)        src/views/routes.py
                                      src/services/notification_service.py
                                      src/middlewares/error_handler.py
                                      app.py (composition root)
                                      legacy/ (originais arquivados)
```

**Projeto 2 — ecommerce-api-legacy**
```
ANTES (callbacks)                     DEPOIS (MVC)
src/app.js                            src/config/settings.js
src/AppManager.js (God Class)         src/models/{database,User,Course,Enrollment,Payment,Report,AuditLog}Model.js
src/utils.js (config + estado global) src/controllers/{Checkout,Report,User}Controller.js
                                      src/routes/{checkout,report,user}Routes.js + index.js
                                      src/services/paymentService.js
                                      src/middlewares/{errorHandler,asyncHandler}.js
                                      src/app.js (composition root)
                                      legacy/ (AppManager.js, utils.js)
```

**Projeto 3 — task-manager-api**
```
ANTES (parcialmente organizado)       DEPOIS (MVC consolidado)
app.py (config hardcoded)             src/config/settings.py
models/ (com is_overdue ignorado)     src/models/{database,task,user,category}_model.py
routes/ (God Files com negócio)       src/controllers/{task,user,category,report,auth}_controller.py
services/ (estado mutável)            src/views/routes.py
utils/ (constantes ignoradas)         src/services/notification_service.py
                                      src/middlewares/error_handler.py
                                      src/utils/{validators,time}.py
                                      src/app.py + app.py (entry point)
                                      legacy/ (estrutura original arquivada)
```

### Checklist de validação preenchido

> Boot validado executando cada aplicação após a refatoração. Endpoints verificados com
> **smoke tests reais via `curl`** contra o servidor rodando (resultados completos abaixo).

#### Projeto 1 — code-smells-project
```
Fase 1 — Análise
[x] Linguagem detectada corretamente (Python)
[x] Framework detectado corretamente (Flask 3.1.1)
[x] Domínio descrito corretamente (E-commerce: produtos, usuários, pedidos)
[x] Número de arquivos analisados condiz (4 arquivos / ~784 linhas)
Fase 2 — Auditoria
[x] Relatório segue o template definido
[x] Cada finding tem arquivo e linhas exatos
[x] Findings ordenados por severidade (CRITICAL → LOW)
[x] Mínimo de 5 findings (12 encontrados)
[x] Detecção de APIs deprecated incluída (catálogo AP-08)
[x] Skill pausa e pede confirmação antes da Fase 3
Fase 3 — Refatoração
[x] Estrutura de diretórios segue padrão MVC
[x] Configuração extraída para módulo config (sem hardcoded) + .env.example
[x] Models criados para abstrair dados
[x] Views/Routes separadas
[x] Controllers concentram o fluxo
[x] Error handling centralizado (middleware)
[x] Entry point claro (composition root)
[x] Aplicação inicia sem erros  ← verificado: BOOT OK
[x] Endpoints originais respondem corretamente
```

#### Projeto 2 — ecommerce-api-legacy
```
Fase 1 — Análise
[x] Linguagem detectada corretamente (JavaScript/Node.js)
[x] Framework detectado corretamente (Express 4.18.2)
[x] Domínio descrito corretamente (LMS API com checkout)
[x] Número de arquivos analisados condiz (3 arquivos / ~180 linhas)
Fase 2 — Auditoria
[x] Relatório segue o template definido
[x] Cada finding tem arquivo e linhas exatos
[x] Findings ordenados por severidade (CRITICAL → LOW)
[x] Mínimo de 5 findings (13 encontrados)
[x] Detecção de APIs deprecated incluída (catálogo AP-08)
[x] Skill pausa e pede confirmação antes da Fase 3
Fase 3 — Refatoração
[x] Estrutura de diretórios segue padrão MVC
[x] Configuração extraída para módulo config (sem hardcoded) + .env.example
[x] Models criados para abstrair dados
[x] Routes separadas
[x] Controllers concentram o fluxo
[x] Error handling centralizado (errorHandler middleware)
[x] Entry point claro (src/app.js)
[x] Aplicação inicia sem erros  ← verificado: BOOT OK (respeita PORT)
[x] Endpoints originais respondem corretamente
```

#### Projeto 3 — task-manager-api
```
Fase 1 — Análise
[x] Linguagem detectada corretamente (Python)
[x] Framework detectado corretamente (Flask 3.0 + SQLAlchemy)
[x] Domínio descrito corretamente (Task Manager)
[x] Número de arquivos analisados condiz (15 arquivos / ~1.167 linhas)
Fase 2 — Auditoria
[x] Relatório segue o template definido
[x] Cada finding tem arquivo e linhas exatos
[x] Findings ordenados por severidade (CRITICAL → LOW)
[x] Mínimo de 5 findings (16 encontrados)
[x] Detecção de APIs deprecated incluída (AP-08: query.get / datetime.utcnow)
[x] Skill pausa e pede confirmação antes da Fase 3
Fase 3 — Refatoração
[x] Estrutura de diretórios segue padrão MVC
[x] Configuração extraída para módulo config (sem hardcoded) + .env.example
[x] Models criados para abstrair dados
[x] Views/Routes separadas
[x] Controllers concentram o fluxo
[x] Error handling centralizado (middleware)
[x] Entry point claro (app.py + src/app.py)
[x] Aplicação inicia sem erros  ← verificado: BOOT OK
[x] Endpoints originais respondem corretamente
```

### Logs de validação (smoke tests reais pós-refatoração)

Cada aplicação foi iniciada e os endpoints foram chamados com `curl`. Todas as respostas
retornaram o status esperado.

**Projeto 1 — code-smells-project (Python/Flask)**
```text
GET  /                     → 200  {"endpoints":{...},"mensagem":"Bem-vindo à API da Loja"}
GET  /produtos             → 200  lista de produtos
GET  /produtos/1           → 200  {"dados":{...},"sucesso":true}
GET  /usuarios             → 200  lista de usuários  (sem campo "senha" — vazamento corrigido)
POST /login                → 200  {"mensagem":"Login OK","sucesso":true}
GET  /pedidos              → 200  {"dados":[],"sucesso":true}
GET  /relatorios/vendas    → 200  relatório de vendas agregado
```

**Projeto 2 — ecommerce-api-legacy (Node.js/Express)**
```text
POST   /api/checkout (cartão 4xxx)       → 200  {"msg":"Sucesso","enrollment_id":2}
POST   /api/checkout (cartão 5xxx)       → 400  "Pagamento recusado"
POST   /api/checkout (payload vazio)     → 400  "Bad Request"
GET    /api/admin/financial-report       → 200  relatório por curso (sem N+1, via JOIN)
DELETE /api/users/1                      → 200  "Usuário deletado" (sem registros órfãos)
```

**Projeto 3 — task-manager-api (Python/Flask + SQLAlchemy)**
```text
GET /health                → 200  {"status":"ok",...}
GET /tasks                 → 200  lista de tasks (overdue calculado via model)
GET /tasks/stats           → 200  {"total":10,"completion_rate":10.0,...}
GET /tasks/search?priority=1 → 200  busca filtrada (cast validado)
GET /users                 → 200  lista de usuários (sem hash de senha exposto)
GET /categories            → 200  lista de categorias com task_count
GET /reports/summary       → 200  relatório agregado de overdue/produtividade
```

### Observações sobre o comportamento em stacks diferentes

- A **mesma skill, copiada sem alteração**, funcionou nas 3 stacks — confirmando o
  agnosticismo. A detecção por *sinais de padrão* (e não por nomes de arquivo) foi decisiva.
- Em **Python** a skill identificou bem injeção de SQL por concatenação e estado global de
  conexão; em **Node** soube reconhecer o anti-pattern equivalente em código orientado a
  callbacks (God Class + estado de módulo + erros silenciosos).
- No **projeto já organizado** (task-manager) a skill não se contentou com a separação
  superficial: detectou God Files nas rotas, regra de negócio nos handlers e **deprecated
  APIs** — gerando o maior número de findings (16).
- A consolidação para MVC variou conforme o ponto de partida: monolitos (1 e 2) exigiram
  criação completa de camadas; o projeto 3 exigiu **redistribuição** das responsabilidades já
  parcialmente separadas.

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e autenticado.
- **Python 3** (projetos 1 e 3) e **Node.js** (projeto 2).
- Dependências de cada projeto (`pip install -r requirements.txt` / `npm install`).

### Executar a skill em cada projeto

A skill já está copiada em `.claude/skills/refactor-arch/` dentro dos 3 projetos. Para
(re)sincronizar as cópias a partir da skill global, use `make update-skills`.

```bash
# Projeto 1 — code-smells-project (Python/Flask)
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 — ecommerce-api-legacy (Node.js/Express)
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — task-manager-api (Python/Flask)
cd ../task-manager-api
claude "/refactor-arch"
```

A skill executa as 3 fases em sequência e **pausa após a Fase 2** pedindo confirmação
(`[y/n]`) antes de modificar qualquer arquivo. O relatório de cada execução é salvo em
`reports/audit-project-{1,2,3}.md`.

### Como validar que a refatoração funcionou

```bash
# Projeto 1
cd code-smells-project && pip install -r requirements.txt && python app.py
# espere "SERVIDOR INICIADO" e teste os endpoints (ex.: curl http://localhost:5000/produtos)

# Projeto 2
cd ../ecommerce-api-legacy && npm install && node src/app.js
# servidor sobe na porta configurada (PORT, default 3000); teste via api.http

# Projeto 3
cd ../task-manager-api && pip install -r requirements.txt && python app.py
# espere o boot sem erros e teste os endpoints de tasks/users/reports
```

Critério de sucesso (igual ao do desafio): a aplicação **inicia sem erros** e **todos os
endpoints originais continuam respondendo** após a refatoração.