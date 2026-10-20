# Changelog — Stokc

Registro das decisões de projeto, correções e revisões feitas durante o desenvolvimento.

---

## [MVP Final] — Outubro/2026

### Decisões de Arquitetura

**Stack Python/Flask + SQLite (em vez de mobile)**
- A spec original previa um app mobile (Flutter/React Native) com APIs de IA externas (OpenAI, Google Speech-to-Text).
- **Decisão revisada:** Optamos por uma aplicação web local com Flask e NLP via regex próprio em português.
- **Justificativa:** Viabilidade para entrega no prazo por desenvolvedor solo; zero custo de API; funciona offline (relevante para Rondônia com conectividade variável).

**SQLite em vez de banco externo**
- Banco de dados SQLite embutido no Python, sem necessidade de instalação de MySQL/PostgreSQL.
- **Limitação reconhecida:** Dados são efêmeros no Render (redefinem a cada deploy). Anotado em "Problemas conhecidos" da spec.

**NLP por regex em vez de LLM**
- O agente (Antigravity) inicialmente sugeriu integração com a API OpenAI para interpretar comandos.
- **Revisão humana:** Descartamos essa opção por: custo de API, dependência de internet e complexidade de autenticação.
- **Decisão:** Motor NLP próprio com regex e palavras-chave em PT-BR. Cobre 100% dos casos de uso do MVP.

---

### Funcionalidades Implementadas

| # | Funcionalidade | Observação |
|---|---|---|
| 1 | Chat conversacional NLP (PT-BR) | Motor regex próprio, sem API externa |
| 2 | Registro de venda com validação de estoque | Impede venda negativa |
| 3 | Registro de entrada com autocadastro | Produto novo é criado automaticamente |
| 4 | Consulta de saldo individual e geral | Com indicador 🟢/🔴 por quantidade |
| 5 | Cadastro manual de produto com preço | Via chat natural |
| 6 | Atualização de preço de venda | Via comando "preço [produto] X,XX" |
| 7 | Listagem de todos os produtos | Via "listar produtos" |
| 8 | Dashboard com KPIs em tempo real | Receita, lucro, valor estoque, alertas |
| 9 | Alertas de estoque baixo (≤ 5 unid.) | Destaque vermelho automático |
| 10 | Relatório de lucro (hoje/semana/geral) | Via chat ou painel |
| 11 | Histórico das últimas 50 movimentações | Tabela com tipo, produto, qtd, preço |
| 12 | Interface web responsiva | HTML/CSS/JS Vanilla |

---

### Correções e Revisões do Agente

**`nlp.py` — Extração de produto**
- O agente gerou uma regex que capturava artigos ("de", "do", "da") como parte do nome do produto.
- **Correção humana:** Adicionada lista de palavras de exclusão (`_extrair_produto`) para remover conectores do português antes de salvar o nome.

**`database.py` — Busca parcial**
- O agente implementou apenas busca exata por nome.
- **Melhoria decidida pela desenvolvedora:** Adicionada busca parcial via `LIKE %nome%` como fallback para tolerar erros de digitação (ex: "arroz" encontra "arroz branco").

**`app.py` — Tratamento de estoque insuficiente**
- O agente não verificava estoque antes de registrar venda.
- **Correção:** Adicionada verificação `if produto["quantidade"] < qtd` com retorno de erro informativo.

**`reports.py` — Interface CLI separada**
- O agente mesclou relatórios CLI e web no mesmo módulo.
- **Decisão de refatoração:** Mantivemos relatórios CLI em `reports.py` e criamos handlers específicos no `app.py` para a API web.

**Segurança — variáveis de ambiente**
- O agente não havia configurado `SECRET_KEY` nem `python-dotenv`.
- **Adicionado pela revisão final:** Carregamento de `.env` via `python-dotenv`, `SECRET_KEY` via `os.environ`, e `.env.example` documentado.

**Deploy — Procfile e gunicorn**
- O agente não havia considerado o deploy em produção.
- **Adicionado:** `Procfile` para Render, `gunicorn` no `requirements.txt`.

---

### Checklist de Segurança (Anexo B da Apostila)

- [x] Nenhuma senha ou chave de API exposta no código-fonte
- [x] `SECRET_KEY` lida de variável de ambiente
- [x] `.env` no `.gitignore` (nunca commitado)
- [x] `.env.example` com valores fictícios no repositório
- [x] Consultas ao banco usando parâmetros `?` (sem SQL injection)
- [x] Dados de usuário (inputs do chat) tratados como string — não executados
- [x] `stokc.db` no `.gitignore` (banco local não vai para o GitHub)
- [ ] Autenticação com senha com hash — **não aplicável** (MVP single-user sem login)

---

### O que ficou de fora do MVP (escopo futuro)

- Reconhecimento de voz (Speech-to-Text) — previsto na spec original, não implementado no MVP por complexidade de integração no prazo
- App mobile (Flutter) — substituído por interface web responsiva
- Múltiplos usuários / autenticação — não implementado (single-user)
- Persistência de dados em nuvem — banco SQLite local; dados efêmeros no Render
- Exportação de relatório em PDF/Excel
