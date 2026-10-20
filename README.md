# Stokc — Gestão de Inventário Conversacional

Assistente web de estoque em português natural para microempreendedores.

## Como rodar localmente

```bash
git clone https://github.com/Lortz0/Stock_Gestao_de_Inventario.git
cd Stock_Gestao_de_Inventario
pip install -r requirements.txt
cp .env.example .env   # edite a SECRET_KEY
cd stokc
python app.py
# Acesse: http://localhost:5000
```

## Exemplos de comandos
- `vendi 5 arroz`
- `chegaram 10 camisetas`
- `quanto tem de feijão?`
- `relatório de hoje`

Ver [`spec.md`](spec.md) para documentação completa.
