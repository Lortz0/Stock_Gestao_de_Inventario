# Projeto Stokc: Gestão de Inventário Conversacional

## 1. Identificação do Projeto
| Campo | Detalhe |
|---|---|
| **Nome** | Stokc |
| **Repositório** | [github.com/Lortz0/Stock_Gestao_de_Inventario](https://github.com/Lortz0/Stock_Gestao_de_Inventario) |
| **Autora** | Lorena (lortzfranciny@gmail.com) |
| **Área** | Desenvolvimento de Software / Inteligência Artificial Aplicada |
| **Tecnologia Principal** | Processamento de Linguagem Natural (NLP) com Python |
| **Setor Econômico** | Comércio e Serviços — Micro e Pequenas Empresas |
| **Status** | ✅ MVP Concluído |

---

## 2. Problema e Oportunidade

Microempreendedores e pequenos lojistas (feirantes, donos de mercearias, pequenos comércios) enfrentam uma barreira crítica na gestão de estoque: os sistemas de ERP tradicionais são complexos, caros e exigem digitação intensa, o que leva esses empreendedores a voltarem ao "caderno de papel" — gerando erros de contagem, perdas por validade vencida e falta de controle financeiro.

A oportunidade é preencher o vácuo entre o controle manual e os softwares burocráticos, oferecendo uma ferramenta **conversacional e intuitiva** que se adapta à rotina acelerada do balcão — sem curva de aprendizado.

---

## 3. Solução Implementada (MVP Entregue)

O **Stokc** é uma aplicação web local que funciona como um **assistente pessoal de inventário**. O lojista controla o estoque conversando em português natural, como se falasse com um funcionário:

> *"vendi 5 fardos de arroz"*
> *"chegaram 10 camisetas pretas"*
> *"quanto tem de feijão?"*
> *"relatório de hoje"*

O sistema interpreta o comando via NLP, atualiza o banco de dados em tempo real e exibe um painel visual com KPIs, alertas e histórico.

---

## 4. Arquitetura Técnica

### Stack Tecnológica

| Camada | Tecnologia | Versão |
|---|---|---|
| **Backend** | Python + Flask | Flask ≥ 3.0.0 |
| **NLP** | Regex + Palavras-chave em PT-BR | Nativo |
| **Banco de Dados** | SQLite (offline-first) | Nativo Python |
| **Frontend** | HTML5 + CSS3 + JavaScript Vanilla | — |
| **Utilitários** | Colorama (CLI) | 0.4.6 |

### Estrutura de Arquivos

```
Projeto_DevSistemas/
└── stokc/
    ├── app.py          # Servidor Flask — API REST e rotas web
    ├── database.py     # Camada de acesso ao SQLite
    ├── nlp.py          # Motor NLP — interpreta linguagem natural
    ├── reports.py      # Relatórios formatados (CLI e API)
    ├── main.py         # Entry point CLI alternativo
    ├── requirements.txt
    ├── stokc.db        # Banco de dados SQLite local
    ├── static/
    │   ├── css/style.css
    │   └── js/app.js
    └── templates/
        └── index.html  # Interface web principal
```

---

## 5. Módulos e Responsabilidades

### `nlp.py` — Motor de Linguagem Natural
Motor 100% local, sem dependência de APIs externas. Interpreta comandos em português usando **regex e palavras-chave** para identificar:

| Intenção | Exemplos de Comando |
|---|---|
| `venda` | "vendi 5 arroz", "saiu 2 feijão", "baixei 10 camisetas" |
| `entrada` | "chegaram 10 camisetas", "recebi 20 fardos", "comprei 5 unidades" |
| `saldo` | "quanto tem de arroz?", "estoque de feijão", "saldo" |
| `relatorio` | "relatório", "relatório de hoje", "resumo da semana", "histórico" |
| `cadastro` | "cadastrar arroz", "novo produto camiseta preço 35" |
| `preco` | "preço arroz 12,50", "atualizar preço feijão 8,00" |
| `listar` | "listar produtos", "mostrar todos os produtos" |
| `ajuda` | "ajuda", "como uso", "comandos" |

**Extração automática** de: quantidade (inteiro/decimal), preço (R$, vírgula ou ponto), nome do produto.

### `database.py` — Camada de Dados (SQLite)
Banco relacional local com duas tabelas:

**`produtos`**
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK | Auto-incremento |
| `nome` | TEXT UNIQUE | Case-insensitive |
| `quantidade` | REAL | Saldo atual em estoque |
| `preco_custo` | REAL | Preço de entrada |
| `preco_venda` | REAL | Preço de venda |
| `unidade` | TEXT | Unidade de medida |

**`movimentacoes`**
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK | Auto-incremento |
| `produto_id` | INTEGER FK | Referência ao produto |
| `tipo` | TEXT | `'entrada'` ou `'saida'` |
| `quantidade` | REAL | Qtd movimentada |
| `preco_unitario` | REAL | Preço no momento da mov. |
| `timestamp` | TEXT | Data/hora (YYYY-MM-DD HH:MM:SS) |

**Funcionalidades:** busca exata e parcial (LIKE), cadastro automático, atualização de estoque por delta, filtro de movimentações por período.

### `app.py` — Servidor Flask (API REST)
Serve a interface web e expõe os seguintes endpoints:

| Método | Endpoint | Função |
|---|---|---|
| `GET` | `/` | Serve o `index.html` |
| `POST` | `/api/chat` | Processa comando NLP e retorna resposta |
| `GET` | `/api/products` | Lista todos os produtos |
| `GET` | `/api/dashboard` | KPIs do dia (receita, lucro, alertas) |
| `GET` | `/api/history` | Histórico das últimas 50 movimentações |
| `GET` | `/api/profit/<periodo>` | Lucro por período: `hoje`, `semana`, `geral` |

### `reports.py` — Relatórios Visuais (CLI)
Relatórios formatados com cores (Colorama):
- **`relatorio_saldo()`** — Exibe estoque atual com alertas de estoque baixo (≤ 5 unidades)
- **`relatorio_lucro(periodo)`** — Receita, custo e lucro bruto por período
- **`relatorio_historico()`** — Últimas 50 movimentações com tipo e valor
- **`relatorio_geral()`** — Combinação de saldo + lucro do dia

---

## 6. Funcionalidades Implementadas

### Interface Web (Chat)
- ✅ Chat conversacional em português com NLP local
- ✅ Registro de vendas com validação de estoque
- ✅ Registro de entradas (com cadastro automático se produto inexistente)
- ✅ Consulta de saldo individual ou geral
- ✅ Cadastro de produtos com preço opcional
- ✅ Atualização de preço de venda
- ✅ Listagem de todos os produtos
- ✅ Relatório solicitado por chat (hoje / semana / geral / histórico)

### Dashboard / Painel
- ✅ KPIs em tempo real: receita do dia, lucro, valor em estoque, nº de vendas
- ✅ Alertas automáticos de estoque baixo (≤ 5 unidades) com destaque 🔴
- ✅ Histórico de movimentações
- ✅ Atualização automática após cada operação

### Lógica de Negócio
- ✅ Verificação de estoque antes de registrar venda (sem venda negativa)
- ✅ Suporte a preço customizado na venda (sobrepõe preço padrão)
- ✅ Cálculo de lucro bruto: receita (saídas) − custo (entradas)
- ✅ Busca de produto por nome exato e parcial (tolerância a erros de digitação)
- ✅ Normalização de texto (case-insensitive, remoção de pontuação extra)

---

## 7. Como Executar

### Pré-requisitos
- Python 3.11+

### Instalação e execução
```bash
# 1. Clonar o repositório
git clone https://github.com/Lortz0/Stock_Gestao_de_Inventario.git
cd Stock_Gestao_de_Inventario/stokc

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Iniciar o servidor
python app.py
```
Acesse: **http://localhost:5000**

---

## 8. Diferencial Inovador

| Característica | Stokc | ERP Tradicional | Planilha |
|---|---|---|---|
| Curva de aprendizado | **Zero** | Alta | Média |
| Velocidade de registro | **Segundos (chat)** | Minutos | Minutos |
| Custo | **Gratuito** | Alto | Baixo |
| Funciona offline | **Sim (SQLite)** | Não | Sim |
| Relatórios em tempo real | **Sim** | Sim | Manual |
| Cadastro automático | **Sim** | Não | Não |
| NLP em português | **Sim** | Não | Não |

---

## 9. Contexto do Programa Centelha 3 — RO

- **Submissão Fase 1:** Até 23/04/2026 (18:00, horário de Brasília)
- **Resultado Final Fase 1:** 02/07/2026
- **Submissão Fase 2 (Projeto de Fomento):** 03/07/2026 a 28/07/2026
- **Execução do Projeto Contratado:** Até 12 meses após a contratação

### Impacto Social
- Profissionalização de pequenos negócios locais em Rondônia
- Redução de desperdício por controle preciso de estoque
- Acessibilidade: interface simples, funciona em qualquer navegador
- Inclusão digital: sem instalação adicional além do Python

---

## 10. Roteiro de Pitch (3 minutos)

1. **Problema (45s):** O caos do caderno — lojista sem controle, produto vencendo, caixa no prejuízo
2. **Demo ao Vivo (1min):** Digite *"vendi 5 arroz"* e mostre o painel atualizando em tempo real
3. **Diferencial (30s):** NLP local, sem internet extra, sem mensalidade, sem treinamento
4. **Mercado e Impacto (30s):** Milhares de microempreendedores em RO sem acesso a ferramentas
5. **Encerramento (15s):** MVP funcional entregue por uma única desenvolvedora — escalável para mobile

---

*Documento atualizado em: Outubro de 2026 — Versão Final MVP*
