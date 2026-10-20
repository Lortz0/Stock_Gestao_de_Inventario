import urllib.request, json

BASE = "http://localhost:5000"

def get(path):
    with urllib.request.urlopen(f"{BASE}{path}") as r:
        return json.loads(r.read())

def post(path, payload):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# ── Dashboard ──────────────────────────────────────────
d = get("/api/dashboard")
print("=== /api/dashboard ===")
print(f"  total_produtos : {d['total_produtos']}")
print(f"  valor_estoque  : R$ {d['valor_estoque']:.2f}")
print(f"  receita_hoje   : R$ {d['receita_hoje']:.2f}")
print(f"  alertas        : {d['alertas']}")

# ── Chat: entrada ──────────────────────────────────────
d = post("/api/chat", {"message": "chegaram 5 feijao"})
print()
print("=== /api/chat (entrada) ===")
print(f"  type  : {d['type']}")
print(f"  reply : {d['reply']}")

# ── Chat: venda ────────────────────────────────────────
d = post("/api/chat", {"message": "vendi 2 feijao"})
print()
print("=== /api/chat (venda) ===")
print(f"  type  : {d['type']}")
print(f"  reply : {d['reply']}")

# ── Chat: saldo ────────────────────────────────────────
d = post("/api/chat", {"message": "quanto tem de feijao?"})
print()
print("=== /api/chat (saldo) ===")
print(f"  type  : {d['type']}")
print(f"  reply : {d['reply']}")

# ── Chat: relatório ────────────────────────────────────
d = post("/api/chat", {"message": "relatorio de hoje"})
print()
print("=== /api/chat (relatorio) ===")
print(f"  type  : {d['type']}")
print(f"  reply : {d['reply']}")

# ── Profit hoje ────────────────────────────────────────
d = get("/api/profit/hoje")
print()
print("=== /api/profit/hoje ===")
print(f"  receita : R$ {d['receita']:.2f}")
print(f"  custo   : R$ {d['custo']:.2f}")
print(f"  lucro   : R$ {d['lucro']:.2f}")

# ── Products ───────────────────────────────────────────
prods = get("/api/products")
print()
print("=== /api/products ===")
for p in prods:
    print(f"  {p['nome'].title():<20} qtd={p['quantidade']:.0f}  pv=R${p['preco_venda']:.2f}")

# ── History ────────────────────────────────────────────
movs = get("/api/history")
print()
print("=== /api/history ===")
for m in movs[:5]:
    print(f"  {m['tipo']:<8} {m['produto_nome'].title():<15} x{m['quantidade']:.0f}")

print()
print("=" * 40)
print("  Todos os endpoints OK!")
print("=" * 40)
