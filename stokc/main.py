"""
main.py — Ponto de entrada do Stokc.
Loop principal do assistente conversacional de inventário.
Execute com: python main.py
"""

import sys
import os

# Garante que o diretório do script está no path
sys.path.insert(0, os.path.dirname(__file__))

# Configura saída UTF-8 (necessário no Windows para emojis e acentos)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from colorama import init, Fore, Back, Style
import database as db
import nlp
import reports

# Inicializa colorama (Windows) — strip=False mantém cores em terminais modernos
init(autoreset=True, strip=False)



# ──────────────────────────── Banner ─────────────────────────────

BANNER = f"""
{Fore.CYAN}{Style.BRIGHT}
 ╔═══════════════════════════════════════════════════╗
 ║   {Fore.WHITE}  ███████╗████████╗ ██████╗ ██╗  ██╗ ██████╗{Fore.CYAN}   ║
 ║   {Fore.WHITE}  ██╔════╝╚══██╔══╝██╔═══██╗██║ ██╔╝██╔════╝{Fore.CYAN}   ║
 ║   {Fore.WHITE}  ███████╗   ██║   ██║   ██║█████╔╝ ██║     {Fore.CYAN}   ║
 ║   {Fore.WHITE}  ╚════██║   ██║   ██║   ██║██╔═██╗ ██║     {Fore.CYAN}   ║
 ║   {Fore.WHITE}  ███████║   ██║   ╚██████╔╝██║  ██╗╚██████╗{Fore.CYAN}   ║
 ║   {Fore.WHITE}  ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝{Fore.CYAN}  ║
 ║                                                   ║
 ║   {Fore.GREEN}  Gestão de Inventário Conversacional          {Fore.CYAN}  ║
 ║   {Fore.YELLOW}  MVP v1.0  •  Projeto Centelha 3 RO           {Fore.CYAN}  ║
 ╚═══════════════════════════════════════════════════╝
{Style.RESET_ALL}"""

AJUDA = f"""
{Fore.CYAN}╔══ COMANDOS DISPONÍVEIS ══════════════════════════════╗{Style.RESET_ALL}

  {Fore.GREEN}📥 ENTRADA DE ESTOQUE:{Style.RESET_ALL}
     "chegaram 10 camisetas pretas"
     "recebi 5 fardos de arroz"
     "comprei 20 refrigerantes"

  {Fore.RED}📤 VENDA / SAÍDA:{Style.RESET_ALL}
     "vendi 3 camisetas"
     "saíram 2 fardos de feijão"
     "baixei 1 garrafa de azeite"

  {Fore.YELLOW}📦 CONSULTA DE SALDO:{Style.RESET_ALL}
     "quanto tem de arroz?"
     "saldo de refrigerante"

  {Fore.MAGENTA}📋 RELATÓRIOS:{Style.RESET_ALL}
     "relatório"         → saldo + lucro do dia
     "relatório de hoje" → lucro de hoje
     "relatório semana"  → lucro dos últimos 7 dias
     "histórico"         → últimas movimentações

  {Fore.BLUE}🛍  CADASTRO DE PRODUTOS:{Style.RESET_ALL}
     "cadastrar arroz"
     "cadastrar refrigerante preço 5,50"
     "preço arroz 12,00"  → atualiza preço de venda

  {Fore.WHITE}📃 LISTAR PRODUTOS:{Style.RESET_ALL}
     "listar produtos"

  {Fore.WHITE}❓ OUTRAS:{Style.RESET_ALL}
     "ajuda" → mostra esta tela
     "sair"  → encerra o sistema

{Fore.CYAN}══════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""


# ──────────────────────── Helpers de saída ───────────────────────

def _ok(msg: str):
    print(f"\n  {Fore.GREEN}✔  {msg}{Style.RESET_ALL}\n")


def _erro(msg: str):
    print(f"\n  {Fore.RED}✘  {msg}{Style.RESET_ALL}\n")


def _info(msg: str):
    print(f"\n  {Fore.YELLOW}ℹ  {msg}{Style.RESET_ALL}\n")


def _stokc(msg: str):
    """Simula a 'fala' do assistente Stokc."""
    print(f"\n  {Fore.CYAN}{Style.BRIGHT}Stokc:{Style.RESET_ALL} {msg}\n")


# ──────────────────────── Handlers de intenção ───────────────────

def _handle_venda(parsed: dict):
    produto_nome = parsed.get("produto")
    qtd          = parsed.get("quantidade")
    preco        = parsed.get("preco")

    if not produto_nome:
        _erro("Não entendi o produto. Tente: 'vendi 5 [produto]'")
        return

    produto = db.buscar_produto(produto_nome)
    if not produto:
        _erro(f"Produto '{produto_nome}' não encontrado.")
        _info("Use 'cadastrar [produto]' para adicioná-lo primeiro.")
        return

    if qtd is None:
        _erro("Quantidade não identificada. Ex: 'vendi 5 unidades de arroz'")
        return

    if produto["quantidade"] < qtd:
        _erro(
            f"Estoque insuficiente! Disponível: {produto['quantidade']:.1f} "
            f"{produto['unidade']}(s) de {produto['nome'].title()}"
        )
        return

    # Usa preço de venda cadastrado se não informado na fala
    preco_unit = preco if preco else produto["preco_venda"]

    db.atualizar_estoque(produto["id"], -qtd)
    db.registrar_movimentacao(produto["id"], "saida", qtd, preco_unit)

    novo_saldo = produto["quantidade"] - qtd
    receita    = qtd * preco_unit

    _stokc(
        f"Venda registrada! {qtd:.0f}x {produto['nome'].title()} "
        f"— Receita: {Fore.GREEN}R$ {receita:.2f}{Style.RESET_ALL}. "
        f"Saldo restante: {Fore.YELLOW}{novo_saldo:.1f}{Style.RESET_ALL}"
    )


def _handle_entrada(parsed: dict):
    produto_nome = parsed.get("produto")
    qtd          = parsed.get("quantidade")
    preco        = parsed.get("preco")

    if not produto_nome:
        _erro("Não entendi o produto. Tente: 'chegaram 10 [produto]'")
        return

    produto = db.buscar_produto(produto_nome)
    if not produto:
        # Produto novo → cadastrar automaticamente
        produto = db.cadastrar_produto(produto_nome)
        _info(f"Produto '{produto_nome.title()}' cadastrado automaticamente.")

    if qtd is None:
        _erro("Quantidade não identificada. Ex: 'chegaram 10 camisetas'")
        return

    preco_unit = preco if preco else produto["preco_custo"]
    if preco and preco != produto["preco_custo"]:
        db.atualizar_preco(produto_nome, preco_custo=preco)

    db.atualizar_estoque(produto["id"], qtd)
    db.registrar_movimentacao(produto["id"], "entrada", qtd, preco_unit)

    novo_saldo = produto["quantidade"] + qtd

    _stokc(
        f"Entrada registrada! +{qtd:.0f}x {produto['nome'].title()}. "
        f"Saldo atualizado: {Fore.YELLOW}{novo_saldo:.1f}{Style.RESET_ALL} {produto['unidade']}(s)"
    )


def _handle_saldo(parsed: dict):
    produto_nome = parsed.get("produto")

    if not produto_nome:
        # Mostra saldo geral
        reports.relatorio_saldo()
        return

    produto = db.buscar_produto(produto_nome)
    if not produto:
        _erro(f"Produto '{produto_nome}' não encontrado.")
        return

    qtd = produto["quantidade"]
    cor = Fore.GREEN if qtd > reports.ESTOQUE_BAIXO_LIMITE else Fore.RED
    _stokc(
        f"{produto['nome'].title()}: "
        f"{cor}{qtd:.1f}{Style.RESET_ALL} {produto['unidade']}(s) em estoque  "
        f"| Preço de venda: {Fore.YELLOW}R$ {produto['preco_venda']:.2f}{Style.RESET_ALL}"
    )


def _handle_relatorio(parsed: dict):
    sub = parsed.get("produto", "geral")

    if sub == "hoje":
        reports.relatorio_lucro("hoje")
    elif sub == "semana":
        reports.relatorio_lucro("semana")
    elif sub == "historico":
        reports.relatorio_historico()
    else:
        reports.relatorio_geral()


def _handle_cadastro(parsed: dict):
    produto_nome = parsed.get("produto")
    preco        = parsed.get("preco")

    if not produto_nome:
        _erro("Não entendi o nome do produto. Ex: 'cadastrar arroz'")
        return

    existente = db.buscar_produto(produto_nome)
    if existente:
        _info(f"Produto '{existente['nome'].title()}' já está cadastrado.")
        return

    pv = preco if preco else 0.0
    db.cadastrar_produto(produto_nome, preco_venda=pv)

    _stokc(
        f"Produto '{produto_nome.title()}' cadastrado! "
        + (f"Preço de venda: R$ {pv:.2f}" if pv else "Preço não informado — use 'preço [produto] X,XX' para definir.")
    )


def _handle_preco(parsed: dict):
    produto_nome = parsed.get("produto")
    preco        = parsed.get("preco")

    if not produto_nome or preco is None:
        _erro("Ex: 'preço arroz 12,50'")
        return

    produto = db.buscar_produto(produto_nome)
    if not produto:
        _erro(f"Produto '{produto_nome}' não encontrado.")
        return

    db.atualizar_preco(produto_nome, preco_venda=preco)
    _stokc(f"Preço de venda de '{produto['nome'].title()}' atualizado para R$ {preco:.2f}")


def _handle_listar(_parsed: dict):
    products = db.listar_produtos()
    if not products:
        _info("Nenhum produto cadastrado. Use 'cadastrar [produto]'.")
        return

    print(f"\n{Fore.CYAN}{'─'*55}")
    print(f"  {'PRODUTO':<28} {'QTD':>8} {'P.CUSTO':>9} {'P.VENDA':>9}")
    print(f"{'─'*55}{Style.RESET_ALL}")

    for p in products:
        qtd_cor = Fore.RED if p["quantidade"] <= reports.ESTOQUE_BAIXO_LIMITE else Fore.GREEN
        print(
            f"  {p['nome'].title():<28} "
            f"{qtd_cor}{p['quantidade']:>8.1f}{Style.RESET_ALL} "
            f"{Fore.WHITE}{p['preco_custo']:>9.2f}{Style.RESET_ALL} "
            f"{Fore.YELLOW}{p['preco_venda']:>9.2f}{Style.RESET_ALL}"
        )
    print(f"{Fore.CYAN}{'─'*55}{Style.RESET_ALL}\n")


# ──────────────────────── Loop principal ─────────────────────────

HANDLERS = {
    "venda":     _handle_venda,
    "entrada":   _handle_entrada,
    "saldo":     _handle_saldo,
    "relatorio": _handle_relatorio,
    "cadastro":  _handle_cadastro,
    "preco":     _handle_preco,
    "listar":    _handle_listar,
}


def main():
    # Prepara banco de dados
    db.criar_tabelas()

    # Exibe banner
    print(BANNER)
    print(f"  {Fore.WHITE}Olá! Sou o {Fore.CYAN}{Style.BRIGHT}Stokc{Style.RESET_ALL}{Fore.WHITE}, seu assistente de inventário.")
    print(f"  Diga o que você vendeu, recebeu ou quer saber. Digite {Fore.YELLOW}'ajuda'{Style.RESET_ALL} para ver os comandos.\n")

    while True:
        try:
            entrada = input(f"  {Fore.GREEN}Você:{Style.RESET_ALL} ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            _stokc("Até logo! Boas vendas! 👋")
            break

        if not entrada:
            continue

        parsed = nlp.interpretar(entrada)
        intencao = parsed["intencao"]

        if intencao == "sair":
            _stokc("Até logo! Boas vendas! 👋")
            break

        elif intencao == "ajuda":
            print(AJUDA)

        elif intencao in HANDLERS:
            HANDLERS[intencao](parsed)

        else:
            _erro(
                "Não entendi o comando. "
                f"Tente '{Fore.WHITE}ajuda{Fore.RED}' para ver exemplos."
            )


if __name__ == "__main__":
    main()
