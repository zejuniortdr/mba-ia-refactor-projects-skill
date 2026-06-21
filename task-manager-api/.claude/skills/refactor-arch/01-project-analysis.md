# Referência: Análise de Projeto

## Objetivo
Detectar com precisão a stack tecnológica e mapear a arquitetura atual de qualquer projeto.

---

## 1. Detecção de Linguagem

### Heurísticas por arquivo manifesto:
| Arquivo encontrado       | Linguagem detectada         |
|--------------------------|-----------------------------|
| `requirements.txt`       | Python                      |
| `Pipfile` / `Pipfile.lock` | Python                    |
| `pyproject.toml`         | Python                      |
| `package.json`           | JavaScript / TypeScript     |
| `tsconfig.json`          | TypeScript                  |
| `go.mod`                 | Go                          |
| `Cargo.toml`             | Rust                        |
| `pom.xml`                | Java                        |

### Heurísticas por extensão de arquivo:
- `.py` → Python
- `.js` / `.mjs` → JavaScript
- `.ts` → TypeScript
- `.go` → Go

---

## 2. Detecção de Framework

### Python:
| Sinal no código                       | Framework         |
|---------------------------------------|-------------------|
| `from flask import Flask`             | Flask             |
| `from django.db import models`        | Django            |
| `from fastapi import FastAPI`         | FastAPI           |
| `app = Flask(__name__)`               | Flask (confirma)  |

### Node.js / JavaScript:
| Sinal no código / package.json        | Framework         |
|---------------------------------------|-------------------|
| `"express"` em dependencies           | Express           |
| `require('express')`                  | Express           |
| `import express from 'express'`       | Express (ESM)     |
| `"fastify"` em dependencies           | Fastify           |
| `"@nestjs/core"` em dependencies      | NestJS            |

### Como detectar versão:
- Python: ler `requirements.txt` — ex: `Flask==3.1.1` → versão 3.1.1
- Node.js: ler `package.json` campo `dependencies` — ex: `"express": "^4.18.0"`

---

## 3. Detecção de Banco de Dados

| Sinal detectado                                      | Banco             |
|------------------------------------------------------|-------------------|
| `sqlite3` em imports, `sqlite3.connect()`            | SQLite            |
| `psycopg2`, `asyncpg`, `pg` em package.json          | PostgreSQL        |
| `pymysql`, `mysql2` em package.json                  | MySQL             |
| `mongoose`, `from mongoose import`                   | MongoDB           |
| `SQLAlchemy` + URL `sqlite:///`                      | SQLite via ORM    |
| `sequelize` em package.json                          | SQL via ORM       |
| `database.db` ou `*.sqlite` presente                 | SQLite (arquivo)  |

---

## 4. Mapeamento de Arquitetura

### 4.1 Classificação de arquitetura:

**Monolítica (Tudo em 1-2 arquivos)**
- Sinais: único arquivo `app.py` / `app.js` com rotas, lógica e SQL
- Grau de risco: CRÍTICO

**Semi-organizada (Arquivos separados, mas sem camadas)**
- Sinais: pastas `models/`, `routes/` existem mas controllers contêm SQL
- Grau de risco: ALTO

**MVC Parcial (Camadas presentes, mas com vazamentos)**
- Sinais: controllers existem mas há lógica de negócio nas rotas
- Grau de risco: MÉDIO

**MVC Completo (Referência)**
- Sinais: Models → Controllers → Routes claramente separados, config em módulo separado
- Grau de risco: BAIXO

### 4.2 Como mapear entidades de domínio:
1. Leia as definições de tabelas SQL (`CREATE TABLE`, `db.execute`, `mongoose.Schema`)
2. Leia os nomes de classes e funções em arquivos de modelo
3. Infira domínios pelos nomes dos endpoints (ex: `/produtos/` → domínio Produto)

### 4.3 Como mapear endpoints:
Busque pelos seguintes padrões:

**Flask:**
```python
@app.route('/path', methods=['GET', 'POST'])
```

**Express:**
```javascript
app.get('/path', handler)
router.post('/path', handler)
```

Liste cada endpoint com método HTTP + path + handler associado.

---

## 5. Resumo de Saída Esperada

Ao final da Fase 1, você deve ser capaz de responder:
1. Qual linguagem e framework (com versão)?
2. Qual banco de dados?
3. Quantos arquivos e linhas de código?
4. Qual arquitetura atual (com classificação)?
5. Quais são os domínios/entidades?
6. Quais são os endpoints disponíveis?