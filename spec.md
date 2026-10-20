# spec.md — Stokc: Gestão de Inventário Conversacional

> **Repositório:** https://github.com/Lortz0/Stock_Gestao_de_Inventario  
> **Sistema publicado:** *(preencher com URL do Render após o deploy)*  
> **Autora:** Lorena — lortzfranciny@gmail.com  
> **Versão:** Final MVP — Outubro/2026

---

## 1. Objetivo

O **Stokc** é um assistente web de gestão de estoque que permite ao lojista registrar vendas, entradas e consultar saldo conversando em português natural — sem menus complexos, sem curva de aprendizado.

**Público-alvo:** Microempreendedores e pequenos lojistas (feirantes, merceeiros, donos de pequeno comércio) com baixa familiaridade com sistemas de gestão.

---

## 2. Usuários e Casos de Uso

| Caso de Uso | Comando de exemplo |
|---|---|
| Registrar venda | "vendi 5 arroz" |
| Registrar entrada de estoque | "chegaram 10 camisetas" |
| Consultar saldo de produto | "quanto tem de feijão?" |
| Consultar saldo geral | "saldo" |
| Cadastrar produto | "cadastrar refrigerante preço 5,50" |
| Atualizar preço de venda | "preço arroz 12,00" |
| Listar todos os produtos | "listar produtos" |
| Ver relatório do dia | "relatório de hoje" |
| Ver relatório da semana | "relatório semana" |
| Ver histórico de movimentações | "histórico" |

---

## 3. Requisitos

### Funcionais
- RF01 — Registrar venda (saída de estoque) via linguagem natural
- RF02 — Registrar entrada de estoque via linguagem natural
- RF03 — Impedir venda quando estoque insuficiente
- RF04 — Cadastrar produto automaticamente quando não existe (entrada)
- RF05 — Exibir saldo de produto individual e saldo geral
- RF06 — Gerar relatório de lucro bruto (hoje / semana / geral)
- RF07 — Exibir histórico das últimas 50 movimentações
- RF08 — Alertar produtos com estoque ≤ 5 unidades (destaque vermelho)
- RF09 — Dashboard com KPIs: receita do dia, lucro, valor em estoque, nº de vendas

### Não-funcionais
- RNF01 — Funciona offline (SQLite local)
- RNF02 — Interface responsiva, acessível por navegador
- RNF03 — NLP local sem chamada a API externa
- RNF04 — Tempo de resposta < 1 segundo por comando
- RNF05 — Nenhuma credencial exposta no código-fonte

---

## 4. Modelo de Dados

**SGBD:** SQLite 3 (nativo no Python, sem instalação separada)  
**Arquivo do banco:** `stokc/stokc.db` (criado automaticamente ao iniciar)  
**Script SQL:** `database/schema.sql`

### Tabelas

| Tabela | Campos principais | Chave primária | Relacionamentos |
|---|---|---|---|
| `produtos` | id, nome, quantidade, preco_custo, preco_venda, unidade | id | — |
| `movimentacoes` | id, produto_id, tipo, quantidade, preco_unitario, timestamp | id | produto_id → produtos.id |

#### Detalhamento dos campos

**`produtos`**
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | Identificador único |
| `nome` | TEXT UNIQUE COLLATE NOCASE | Nome do produto (case-insensitive) |
| `quantidade` | REAL DEFAULT 0 | Saldo atual em estoque |
| `preco_custo` | REAL DEFAULT 0 | Preço de compra/entrada |
| `preco_venda` | REAL DEFAULT 0 | Preço de venda ao cliente |
| `unidade` | TEXT DEFAULT 'unidade' | Unidade de medida |

**`movimentacoes`**
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | Identificador único |
| `produto_id` | INTEGER FK | Referência ao produto |
| `tipo` | TEXT CHECK IN ('entrada','saida') | Tipo da movimentação |
| `quantidade` | REAL | Quantidade movimentada |
| `preco_unitario` | REAL DEFAULT 0 | Preço unitário no momento |
| `timestamp` | TEXT | Data/hora no formato YYYY-MM-DD HH:MM:SS |

**Dados iniciais:** Não há dados obrigatórios pré-inseridos. O banco começa vazio. Use os comandos do chat para cadastrar produtos.

---

## 5. Decisão de Stack

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Backend | Python 3.11 + Flask 3.x | Linguagem dominada pela equipe; Flask é leve e rápido para MVPs |
| NLP | Regex + palavras-chave PT-BR | Sem custo de API; funciona offline; adequado ao vocabulário fixo do domínio |
| Banco de dados | SQLite 3 | Zero configuração; nativo no Python; offline-first |
| Frontend | HTML5 + CSS3 + JavaScript Vanilla | Sem dependências de framework; carregamento rápido |
| Servidor produção | Gunicorn 21.x | WSGI server padrão para Flask no Render/Heroku |
| Deploy | Render (free tier) | Suporta Python nativamente; deploy por push no GitHub |

---

## 6. API REST

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/` | Serve a interface web (index.html) |
| POST | `/api/chat` | Processa comando em linguagem natural |
| GET | `/api/products` | Lista todos os produtos |
| GET | `/api/dashboard` | KPIs do dia (receita, lucro, estoque, alertas) |
| GET | `/api/history` | Últimas 50 movimentações |
| GET | `/api/profit/<periodo>` | Lucro por período: `hoje`, `semana`, `geral` |

---

## 7. Critérios de Aceite

- [ ] Usuário digita "vendi 5 arroz" e o estoque é atualizado imediatamente
- [ ] Sistema recusa venda quando estoque < quantidade pedida
- [ ] Dashboard exibe receita e lucro do dia em tempo real
- [ ] Produto com quantidade ≤ 5 aparece em vermelho no painel
- [ ] Comando "relatório" exibe saldo e lucro corretamente
- [ ] Sistema abre sem erro em aba anônima do navegador pelo link publicado
- [ ] Professor consegue instalar e rodar seguindo apenas esta spec

---

## 8. Variáveis de Ambiente

Copie `.env.example` para `.env` e preencha:

```env
SECRET_KEY=troque-por-uma-chave-secreta-forte
FLASK_ENV=development
PORT=5000
```

| Variável | Finalidade | Como preencher |
|---|---|---|
| `SECRET_KEY` | Segurança de sessões Flask | Gere com: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_ENV` | Modo de execução | `development` local / `production` no servidor |
| `PORT` | Porta do servidor | `5000` localmente; o Render define automaticamente |

> ⚠️ O arquivo `.env` está no `.gitignore` e **nunca deve ser commitado**.

---

## 9. Instalação e Execução

### 9.1 Ambiente

| Item | Versão testada |
|---|---|
| Sistema operacional | Windows 11 / Ubuntu 22.04 |
| Python | 3.11 ou superior |
| Pip | Incluído no Python 3.11+ |
| SQLite | Nativo no Python (sem instalação) |
| Navegador | Chrome, Firefox, Edge (qualquer moderno) |

### 9.2 Passo a passo completo

```
1. Clonar o repositório
   git clone https://github.com/Lortz0/Stock_Gestao_de_Inventario.git
   cd Stock_Gestao_de_Inventario

2. Criar e ativar ambiente virtual (recomendado)
   # Windows:
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac:
   python3 -m venv venv
   source venv/bin/activate

3. Instalar as dependências
   pip install -r requirements.txt

4. Configurar variáveis de ambiente
   # Windows:
   copy .env.example .env

   # Linux/Mac:
   cp .env.example .env

   # Abra o arquivo .env e edite o valor de SECRET_KEY

5. Iniciar o servidor
   cd stokc
   python app.py

6. Abrir no navegador
   http://localhost:5000
```

> O banco de dados `stokc/stokc.db` é criado **automaticamente** ao iniciar o servidor pela primeira vez. Não é necessário executar o script SQL manualmente para rodar localmente.

### 9.3 Banco de dados (opcional — execução manual do script)

Caso queira criar o banco manualmente ou inspecioná-lo:

```bash
# Com SQLite instalado separadamente:
sqlite3 stokc/stokc.db < database/schema.sql

# OU via Python (já feito automaticamente pelo app.py):
cd stokc
python -c "import database; database.criar_tabelas(); print('Banco criado!')"
```

### 9.4 Como testar o sistema

**Usuário de teste:** não há autenticação (sistema single-user por design do MVP).

**Roteiro do fluxo principal:**

1. Abra `http://localhost:5000` no navegador
2. No chat, digite: `cadastrar arroz preço 7,00`
3. Digite: `chegaram 50 arroz`
4. Digite: `vendi 3 arroz`
5. Digite: `quanto tem de arroz?` — deve mostrar 47 unidades
6. Digite: `relatório de hoje` — deve mostrar receita e lucro
7. O painel à direita atualiza automaticamente com os KPIs

### 9.5 Problemas conhecidos e limitações

| Problema | Descrição | Impacto |
|---|---|---|
| Dados efêmeros no Render | O SQLite é salvo em disco temporário; dados são apagados a cada novo deploy | Baixo — aceitável para MVP/demonstração |
| NLP por regex | Comandos fora do padrão esperado podem não ser reconhecidos | Baixo — guia de comandos disponível no chat (digite "ajuda") |
| Sem autenticação | Qualquer pessoa com acesso à URL pode usar o sistema | Baixo — MVP single-user por decisão de escopo |
| Render "dorme" | O serviço gratuito fica inativo após ~15min sem uso; primeiro acesso pode demorar ~1min para "acordar" | Aguarde carregar antes de apresentar |

---

## 10. Contexto — Programa Centelha 3 (RO)

- **Submissão Fase 1:** Até 23/04/2026
- **Resultado Fase 1:** 02/07/2026
- **Fase 2:** 03/07/2026 a 28/07/2026

**Impacto social:** Profissionalização de microempreendedores em Rondônia com ferramenta gratuita, offline-first e sem curva de aprendizado.
