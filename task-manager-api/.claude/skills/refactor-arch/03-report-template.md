# Template de Relatório de Auditoria

> Use este template EXATAMENTE para gerar o relatório da Fase 2.
> Substitua os valores entre [ ] pelos dados reais do projeto auditado.
> Ordene os findings de CRITICAL → HIGH → MEDIUM → LOW.

---

## Template do Relatório


============================================
# ARCHITECTURE AUDIT REPORT
Project: [nome do diretório do projeto]
============================================

**Stack**:   [Linguagem] + [Framework v.X.X]
**Files**:   [N] analyzed | ~[N] lines of code
**Date**:    [data de execução]

## Summary
CRITICAL: [N] | HIGH: [N] | MEDIUM: [N] | LOW: [N]

Total findings: [N]

## Findings
### [CRITICAL] [Nome do Anti-Pattern — ex: God Class / God File]
File: [arquivo.py]:[linha_inicio]-[linha_fim]
Description: [Descrição objetiva do que foi encontrado, referenciando o código real]
Evidence:
[linha N]: [trecho do código evidência — máximo 3 linhas]
Impact: [Impacto concreto no projeto — seja específico]
Recommendation: [Ação de correção — mencione o padrão do playbook a aplicar]

### [CRITICAL] [Nome do Anti-Pattern]
File: [arquivo]:[linha]
Description: [...]
Evidence:
[linha N]: [...]
Impact: [...]
Recommendation: [...]

### [HIGH] [Nome do Anti-Pattern]
File: [arquivo]:[linha_inicio]-[linha_fim]
Description: [...]
Evidence:
[linha N]: [...]
Impact: [...]
Recommendation: [...]

### [MEDIUM] [Nome do Anti-Pattern]
File: [arquivo]:[linha_inicio]-[linha_fim]
Description: [...]
Evidence:
[linha N]: [...]
Impact: [...]
Recommendation: [...]

### [LOW] [Nome do Anti-Pattern]
File: [arquivo]:[linha]
Description: [...]
Impact: [...]
Recommendation: [...]
================================

Total: [N] findings

CRITICAL: [N] | HIGH: [N] | MEDIUM: [N] | LOW: [N]


---

## Regras de Preenchimento

1. **Arquivo e linha são OBRIGATÓRIOS** — nunca deixe genérico como "models.py (várias linhas)"
2. **Evidence deve ser código real** — copie exatamente do arquivo analisado
3. **Description deve ser específica** — mencione nomes de funções e variáveis reais
4. **Impact deve ser concreto** — evite "pode causar problemas"; diga "permite SQL Injection"
5. **Recommendation deve referenciar** o padrão do playbook a ser aplicado na Fase 3
6. **Ordenação obrigatória**: CRITICAL primeiro, depois HIGH, MEDIUM, LOW
7. **Mínimo de 5 findings** por projeto para auditoria completa

---

## Exemplo de Finding Preenchido Corretamente
```
### [CRITICAL] Hardcoded Secret Key
File: app.py:8
Description: A SECRET_KEY da aplicação Flask está hardcoded como string literal
'minha-chave-super-secreta-123', exposta diretamente no código-fonte.

Evidence:
linha 8: app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'
Impact: Qualquer pessoa com acesso ao repositório pode forjar sessões de usuário,
comprometendo completamente a autenticação da aplicação.
Recommendation: Extrair para variável de ambiente via python-dotenv (Playbook: ENV-01).
```