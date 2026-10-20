"""
app.py — Servidor Flask do Stokc.
Expõe a API REST e serve a interface web.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Carrega variáveis de ambiente do arquivo .env (se existir)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass  # python-dotenv não instalado — ok em produção com vars de sistema

from flask import Flask, request, jsonify, render_template
from datetime import date, timedelta
import database as db
import nlp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-insecure-key-change-in-production')

# ── Inicializa banco na primeira execução ──────────────────────────
db.criar_tabelas()


# ══════════════════════════════════════════════════════════════════
#  PÁGINA PRINCIPAL
# ══════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


# ══════════════════════════════════════════════════════════════════
#  API — CHAT (linguagem natural)
# ══════════════════════════════════════════════════════════════════

@app.route("/api/chat", methods=["POST"])
def chat():
    """Processa um comando em linguagem natural e retorna resposta."""
    data    = request.get_json(force=True)
    entrada = data.get("message", "").strip()

    if not entrada:
        return jsonify({"reply": "Por favor, diga algo! Ex: 'vendi 5 arroz'", "type": "error"})

    parsed   = nlp.interpretar(entrada)
    intencao = parsed["intencao"]

    handlers = {
        "venda":     _chat_venda,
        "entrada":   _chat_entrada,
        "saldo":     _chat_saldo,
        "relatorio": _chat_relatorio,
        "cadastro":  _chat_cadastro,
        "preco":     _chat_preco,
        "listar":    _chat_listar,
        "ajuda":     _chat_ajuda,
        "sair":      lambda p: {"reply": "Até logo! Boas vendas! 👋", "type": "bye"},
    }

    handler = handlers.get(intencao)
    if handler:
        result = handler(parsed)
    else:
        result = {
            "reply": (
                "Não entendi o comando. 🤔\n"
                "Tente algo como: 'vendi 5 arroz', 'chegaram 10 camisetas', "
                "'quanto tem de feijão?' ou 'relatório'."
            ),
            "type": "error",
        }

    return jsonify(result)


# ─────────────────── Handlers de chat ────────────────────────────

def _chat_venda(parsed):
    nome = parsed.get("produto")
    qtd  = parsed.get("quantidade")
    preco = parsed.get("preco")

    if not nome:
        return {"reply": "Não entendi o produto. Ex: 'vendi 5 arroz'", "type": "error"}

    produto = db.buscar_produto(nome)
    if not produto:
        return {"reply": f"❌ Produto '{nome}' não encontrado. Use 'cadastrar {nome}' primeiro.", "type": "error"}

    if qtd is None:
        return {"reply": "Quantidade não identificada. Ex: 'vendi 5 arroz'", "type": "error"}

    if produto["quantidade"] < qtd:
        return {
            "reply": (
                f"⚠️ Estoque insuficiente!\n"
                f"Disponível: **{produto['quantidade']:.0f}** {produto['unidade']}(s) de {produto['nome'].title()}"
            ),
            "type": "warning",
        }

    preco_unit = preco if preco else produto["preco_venda"]
    db.atualizar_estoque(produto["id"], -qtd)
    db.registrar_movimentacao(produto["id"], "saida", qtd, preco_unit)

    novo_saldo = produto["quantidade"] - qtd
    receita    = qtd * preco_unit

    return {
        "reply": (
            f"✅ Venda registrada!\n"
            f"**{qtd:.0f}x {produto['nome'].title()}** — Receita: **R$ {receita:.2f}**\n"
            f"Saldo restante: **{novo_saldo:.0f}** {produto['unidade']}(s)"
        ),
        "type": "success",
        "refresh": True,
    }


def _chat_entrada(parsed):
    nome  = parsed.get("produto")
    qtd   = parsed.get("quantidade")
    preco = parsed.get("preco")

    if not nome:
        return {"reply": "Não entendi o produto. Ex: 'chegaram 10 camisetas'", "type": "error"}

    produto = db.buscar_produto(nome)
    novo = False
    if not produto:
        produto = db.cadastrar_produto(nome)
        novo = True

    if qtd is None:
        return {"reply": "Quantidade não identificada. Ex: 'chegaram 10 camisetas'", "type": "error"}

    preco_unit = preco if preco else produto["preco_custo"]
    if preco and preco != produto["preco_custo"]:
        db.atualizar_preco(nome, preco_custo=preco)

    db.atualizar_estoque(produto["id"], qtd)
    db.registrar_movimentacao(produto["id"], "entrada", qtd, preco_unit)

    novo_saldo = produto["quantidade"] + qtd
    auto_msg   = f"\n_(Produto cadastrado automaticamente)_" if novo else ""

    return {
        "reply": (
            f"📦 Entrada registrada!{auto_msg}\n"
            f"**+{qtd:.0f}x {produto['nome'].title()}**\n"
            f"Saldo atualizado: **{novo_saldo:.0f}** {produto['unidade']}(s)"
        ),
        "type": "success",
        "refresh": True,
    }


def _chat_saldo(parsed):
    nome = parsed.get("produto")

    if not nome:
        produtos = db.listar_produtos()
        if not produtos:
            return {"reply": "Nenhum produto cadastrado ainda.", "type": "info"}
        linhas = [f"**📦 Saldo de Estoque:**"]
        for p in produtos:
            emoji = "🔴" if p["quantidade"] <= 5 else "🟢"
            linhas.append(f"{emoji} {p['nome'].title()}: **{p['quantidade']:.0f}** {p['unidade']}(s)")
        return {"reply": "\n".join(linhas), "type": "info"}

    produto = db.buscar_produto(nome)
    if not produto:
        return {"reply": f"❌ Produto '{nome}' não encontrado.", "type": "error"}

    emoji = "🔴" if produto["quantidade"] <= 5 else "🟢"
    return {
        "reply": (
            f"{emoji} **{produto['nome'].title()}**\n"
            f"Estoque: **{produto['quantidade']:.0f}** {produto['unidade']}(s)\n"
            f"Preço de venda: **R$ {produto['preco_venda']:.2f}**"
        ),
        "type": "info",
    }


def _chat_relatorio(parsed):
    sub = parsed.get("produto", "geral")
    return {
        "reply": f"📊 Relatório **{sub}** exibido no painel à direita!",
        "type":  "info",
        "action": f"report:{sub}",
    }


def _chat_cadastro(parsed):
    nome  = parsed.get("produto")
    preco = parsed.get("preco")

    if not nome:
        return {"reply": "Não entendi o nome. Ex: 'cadastrar arroz' ou 'cadastrar camiseta preço 35'", "type": "error"}

    existente = db.buscar_produto(nome)
    if existente:
        return {"reply": f"ℹ️ Produto '{existente['nome'].title()}' já está cadastrado.", "type": "info"}

    pv = preco if preco else 0.0
    db.cadastrar_produto(nome, preco_venda=pv)

    return {
        "reply": (
            f"✅ Produto **'{nome.title()}'** cadastrado!\n"
            + (f"Preço de venda: **R$ {pv:.2f}**" if pv else "💡 Use 'preço {nome} X,XX' para definir o valor.")
        ),
        "type": "success",
        "refresh": True,
    }


def _chat_preco(parsed):
    nome  = parsed.get("produto")
    preco = parsed.get("preco")

    if not nome or preco is None:
        return {"reply": "Ex: 'preço arroz 12,50'", "type": "error"}

    produto = db.buscar_produto(nome)
    if not produto:
        return {"reply": f"❌ Produto '{nome}' não encontrado.", "type": "error"}

    db.atualizar_preco(nome, preco_venda=preco)
    return {
        "reply": f"💰 Preço de **{produto['nome'].title()}** atualizado para **R$ {preco:.2f}**",
        "type": "success",
        "refresh": True,
    }


def _chat_listar(parsed):
    produtos = db.listar_produtos()
    if not produtos:
        return {"reply": "Nenhum produto cadastrado ainda.", "type": "info"}
    linhas = ["**📋 Produtos cadastrados:**"]
    for p in produtos:
        emoji = "🔴" if p["quantidade"] <= 5 else "🟢"
        linhas.append(
            f"{emoji} **{p['nome'].title()}** — {p['quantidade']:.0f} unid. | R$ {p['preco_venda']:.2f}"
        )
    return {"reply": "\n".join(linhas), "type": "info"}


def _chat_ajuda(parsed):
    return {
        "reply": (
            "🤖 **Comandos do Stokc:**\n\n"
            "📥 **Entrada:** 'chegaram 10 camisetas'\n"
            "📤 **Venda:** 'vendi 5 arroz'\n"
            "📦 **Saldo:** 'quanto tem de feijão?'\n"
            "📊 **Relatório:** 'relatório' ou 'relatório de hoje'\n"
            "🛍 **Cadastrar:** 'cadastrar refrigerante preço 5,50'\n"
            "💰 **Preço:** 'preço arroz 12,00'\n"
            "📋 **Listar:** 'listar produtos'"
        ),
        "type": "info",
    }


# ══════════════════════════════════════════════════════════════════
#  API — DASHBOARD
# ══════════════════════════════════════════════════════════════════

@app.route("/api/products")
def api_products():
    return jsonify(db.listar_produtos())


@app.route("/api/dashboard")
def api_dashboard():
    """Retorna KPIs para o painel principal."""
    hoje   = date.today().isoformat()
    movs   = db.listar_movimentacoes(hoje, hoje)
    todos  = db.listar_produtos()

    receita = sum(m["quantidade"] * m["preco_unitario"] for m in movs if m["tipo"] == "saida")
    custo   = sum(m["quantidade"] * m["preco_unitario"] for m in movs if m["tipo"] == "entrada")
    lucro   = receita - custo

    valor_estoque = sum(p["quantidade"] * p["preco_venda"] for p in todos)
    alertas = [p for p in todos if p["quantidade"] <= 5]
    vendas_hoje = sum(1 for m in movs if m["tipo"] == "saida")

    return jsonify({
        "receita_hoje":   round(receita, 2),
        "lucro_hoje":     round(lucro, 2),
        "valor_estoque":  round(valor_estoque, 2),
        "total_produtos": len(todos),
        "vendas_hoje":    vendas_hoje,
        "alertas":        len(alertas),
        "produtos":       todos,
        "alertas_nomes":  [p["nome"].title() for p in alertas],
    })


@app.route("/api/history")
def api_history():
    movs = db.listar_movimentacoes()
    return jsonify(movs)


@app.route("/api/profit/<periodo>")
def api_profit(periodo):
    hoje = date.today()
    if periodo == "hoje":
        inicio = hoje.isoformat()
        fim    = hoje.isoformat()
    elif periodo == "semana":
        inicio = (hoje - timedelta(days=7)).isoformat()
        fim    = hoje.isoformat()
    else:
        inicio = None
        fim    = None

    movs    = db.listar_movimentacoes(inicio, fim)
    receita = sum(m["quantidade"] * m["preco_unitario"] for m in movs if m["tipo"] == "saida")
    custo   = sum(m["quantidade"] * m["preco_unitario"] for m in movs if m["tipo"] == "entrada")

    return jsonify({
        "receita": round(receita, 2),
        "custo":   round(custo, 2),
        "lucro":   round(receita - custo, 2),
        "periodo": periodo,
    })


# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n  🚀  Stokc Web iniciado em http://localhost:5000\n")
    app.run(debug=True, port=5000, use_reloader=False)
