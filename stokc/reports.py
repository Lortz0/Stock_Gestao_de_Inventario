"""
reports.py — Módulo de relatórios do Stokc.
Gera e exibe relatórios de saldo, lucro, histórico de movimentações
e alertas de estoque baixo diretamente no terminal.
"""

from datetime import date, timedelta
from colorama import Fore, Style
import database as db


ESTOQUE_BAIXO_LIMITE = 5  # Quantidade mínima antes do alerta


def _linha(char="─", largura=55):
    return char * largura


def _titulo(texto: str):
    print(f"\n{Fore.CYAN}{_linha()}")
    print(f"  {texto}")
    print(f"{_linha()}{Style.RESET_ALL}")


def _moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ─────────────────── Relatório de Saldo ──────────────────────────

def relatorio_saldo():
    """Exibe o saldo atual de todos os produtos em estoque."""
    produtos = db.listar_produtos()

    _titulo("📦  SALDO DE ESTOQUE")

    if not produtos:
        print(f"  {Fore.YELLOW}Nenhum produto cadastrado ainda.{Style.RESET_ALL}")
        print(f"  Dica: diga '{Fore.WHITE}cadastrar [nome do produto]{Style.RESET_ALL}' para começar.\n")
        return

    col_nome = 28
    col_qtd  = 10
    col_preco = 13

    header = (
        f"  {'PRODUTO':<{col_nome}} {'QTD':>{col_qtd}} {'P.VENDA':>{col_preco}}"
    )
    print(f"{Fore.WHITE}{Style.BRIGHT}{header}")
    print(f"  {_linha('·', 53)}{Style.RESET_ALL}")

    total_valor = 0.0
    alertas = []

    for p in produtos:
        nome = p["nome"].title()[:col_nome]
        qtd  = p["quantidade"]
        pv   = p["preco_venda"]
        valor_total = qtd * pv
        total_valor += valor_total

        cor = Fore.RED if qtd <= ESTOQUE_BAIXO_LIMITE else Fore.GREEN
        if qtd <= ESTOQUE_BAIXO_LIMITE:
            alertas.append(nome)

        linha = (
            f"  {nome:<{col_nome}} "
            f"{cor}{qtd:>{col_qtd}.1f}{Style.RESET_ALL} "
            f"{Fore.YELLOW}{_moeda(pv):>{col_preco}}{Style.RESET_ALL}"
        )
        print(linha)

    print(f"\n  {Fore.WHITE}Valor total em estoque: {Fore.GREEN}{Style.BRIGHT}{_moeda(total_valor)}{Style.RESET_ALL}\n")

    if alertas:
        print(f"  {Fore.RED}⚠  Estoque baixo: {', '.join(alertas)}{Style.RESET_ALL}\n")


# ─────────────────── Relatório de Lucro ──────────────────────────

def relatorio_lucro(periodo: str = "hoje"):
    """Calcula e exibe o lucro bruto do período especificado."""
    hoje = date.today()

    if periodo == "hoje":
        inicio = hoje.isoformat()
        fim    = hoje.isoformat()
        label  = "HOJE"
    elif periodo == "semana":
        inicio = (hoje - timedelta(days=7)).isoformat()
        fim    = hoje.isoformat()
        label  = "ÚLTIMOS 7 DIAS"
    else:
        inicio = None
        fim    = None
        label  = "GERAL"

    movs = db.listar_movimentacoes(inicio, fim)

    _titulo(f"💰  RELATÓRIO DE LUCRO — {label}")

    if not movs:
        print(f"  {Fore.YELLOW}Sem movimentações no período.{Style.RESET_ALL}\n")
        return

    receita  = 0.0
    custo    = 0.0
    vendas   = 0
    entradas = 0

    for m in movs:
        if m["tipo"] == "saida":
            receita += m["quantidade"] * m["preco_unitario"]
            vendas  += 1
        elif m["tipo"] == "entrada":
            custo   += m["quantidade"] * m["preco_unitario"]
            entradas += 1

    lucro = receita - custo

    cor_lucro = Fore.GREEN if lucro >= 0 else Fore.RED
    print(f"  {'Receita (vendas):':<30} {Fore.GREEN}{_moeda(receita):>12}{Style.RESET_ALL}")
    print(f"  {'Custo (entradas):':<30} {Fore.RED}{_moeda(custo):>12}{Style.RESET_ALL}")
    print(f"  {_linha('·', 45)}")
    print(f"  {'Lucro Bruto:':<30} {cor_lucro}{Style.BRIGHT}{_moeda(lucro):>12}{Style.RESET_ALL}")
    print(f"\n  {Fore.WHITE}Vendas: {vendas}  |  Entradas de estoque: {entradas}{Style.RESET_ALL}\n")


# ─────────────────── Histórico de Movimentações ──────────────────

def relatorio_historico():
    """Exibe as últimas 50 movimentações."""
    movs = db.listar_movimentacoes()

    _titulo("📋  HISTÓRICO DE MOVIMENTAÇÕES (últimas 50)")

    if not movs:
        print(f"  {Fore.YELLOW}Nenhuma movimentação registrada.{Style.RESET_ALL}\n")
        return

    for m in movs:
        tipo  = m["tipo"]
        emoji = "🟢" if tipo == "entrada" else "🔴"
        cor   = Fore.GREEN if tipo == "entrada" else Fore.RED
        nome  = m["produto_nome"].title()
        qtd   = m["quantidade"]
        preco = m["preco_unitario"]
        ts    = m["timestamp"][:16]  # YYYY-MM-DD HH:MM

        print(
            f"  {emoji} {Fore.WHITE}{ts}{Style.RESET_ALL}  "
            f"{cor}{tipo.upper():<8}{Style.RESET_ALL}  "
            f"{nome:<25} "
            f"x{qtd:.1f}  "
            f"{Fore.YELLOW}{_moeda(preco)}{Style.RESET_ALL}"
        )
    print()


# ─────────────────── Relatório geral rápido ──────────────────────

def relatorio_geral():
    """Exibe saldo + lucro do dia em sequência."""
    relatorio_saldo()
    relatorio_lucro("hoje")
