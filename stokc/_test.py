import sys, os
sys.path.insert(0, '.')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import database as db
import nlp
import reports
from colorama import init
init()

# Limpa DB de teste anterior se existir
if os.path.exists("stokc.db"):
    os.remove("stokc.db")

# Cria tabelas
db.criar_tabelas()

# Testa NLP
testes = [
    "chegaram 10 camisetas pretas",
    "vendi 5 fardos de arroz",
    "quanto tem de refrigerante?",
    "relatorio de hoje",
    "cadastrar feijao preco 8,90",
    "listar produtos",
    "ajuda",
    "sair",
]
print("=== TESTE NLP ===")
for t in testes:
    r = nlp.interpretar(t)
    print(f"  [{r['intencao']:>12}]  qtd={r['quantidade']}  prod={r['produto']}  preco={r['preco']}")
    print(f"               entrada: \"{t}\"")
    print()

# Testa DB
db.cadastrar_produto("arroz", preco_custo=10.0, preco_venda=15.0, unidade="fardo")
db.cadastrar_produto("camiseta", preco_custo=20.0, preco_venda=35.0)
db.atualizar_estoque(1, 20)
db.atualizar_estoque(2, 10)
db.registrar_movimentacao(1, "saida", 5, 15.0)
db.registrar_movimentacao(2, "saida", 3, 35.0)

print("=== PRODUTOS ===")
for p in db.listar_produtos():
    print(dict(p))

print()
print("=== MOVIMENTACOES ===")
for m in db.listar_movimentacoes():
    print(dict(m))

print()
print("=== RELATORIO SALDO ===")
reports.relatorio_saldo()

print("=== RELATORIO LUCRO (hoje) ===")
reports.relatorio_lucro("hoje")
