"""
nlp.py — Motor de Processamento de Linguagem Natural do Stokc.
Interpreta comandos em português usando regex e palavras-chave.
Retorna um dicionário de intenção estruturado.
"""

import re

# ─────────────────── Palavras-chave por intenção ──────────────────

_PALAVRAS_VENDA = r"vend[ei]|saiu|saíu|sai[u]?|coloca[r]? na conta|consumido|deu saída|baixei"
_PALAVRAS_ENTRADA = r"cheg(ou|aram|ar)?|entr(ou|aram|ar)?|recebi|comprei|adicionei|reposição|repus|aumentei"
_PALAVRAS_SALDO = r"quan(to|tos|ta|tas)|tem|tenho|restante|saldo|estoque de|qtd de|quantidade de"
_PALAVRAS_RELATORIO = r"relat[oó]rio|resumo|totais?|balanço|lucro|ganho|resultado|histórico|movimentaç"
_PALAVRAS_CADASTRO = r"cadastr[ao]r?|registr[ao]r?|adicionar produto|novo produto|criar produto"
_PALAVRAS_PRECO = r"preço|preco|valor|custa|custou|vende por|vendo por|atualizar preço"
_PALAVRAS_LISTAR = r"listar?|mostrar?|exibir?|ver todos|todos os produtos|lista de"
_PALAVRAS_AJUDA = r"ajuda|help|\?|comandos|como uso|o que (você|voce|vc) (faz|sabe)"
_PALAVRAS_SAIR = r"sair?|exit|quit|tchau|até logo|fechar"

# ─────────────────── Padrões de quantidade e produto ─────────────

# Captura número (inteiro ou decimal, separador vírgula ou ponto)
_NUM = r"(\d+(?:[.,]\d+)?)"
# Captura nome do produto (restante da frase após a quantidade)
_PRODUTO = r"(.+?)(?:\s+por\s+|\s+a\s+|\s+preço|\s+preco|$)"

def _parse_num(s: str) -> float:
    """Converte string numérica para float, aceitando vírgula."""
    return float(s.replace(",", "."))


def _limpar(texto: str) -> str:
    """Normaliza o texto: lower + strip + remove pontuação extra."""
    texto = texto.lower().strip()
    texto = re.sub(r"[!.]+$", "", texto)  # remove pontuação final
    return texto


# ─────────────────── Extração de preço ───────────────────────────

def _extrair_preco(texto: str) -> float | None:
    """Extrai o primeiro valor monetário encontrado no texto."""
    padrao = r"(?:r\$|reais?|por|a)\s*" + _NUM
    match = re.search(padrao, texto, re.IGNORECASE)
    if match:
        return _parse_num(match.group(1))
    # Preço no final: "... 12,50"
    match = re.search(r"[\s,]" + _NUM + r"\s*$", texto)
    if match:
        return _parse_num(match.group(1))
    return None


def _extrair_quantidade(texto: str) -> tuple[float | None, str]:
    """
    Extrai quantidade e remove ela do texto, retornando (qtd, texto_sem_qtd).
    """
    # Padrões: "5 fardos de", "dez unidades de", etc.
    match = re.search(r"\b" + _NUM + r"\b", texto)
    if match:
        qtd = _parse_num(match.group(1))
        texto_sem = texto[:match.start()] + texto[match.end():]
        return qtd, texto_sem.strip()
    return None, texto


def _extrair_produto(texto: str, palavras_gatilho: list[str]) -> str:
    """Remove palavras-gatilho e sobras comuns, deixando apenas o nome do produto."""
    for palavra in palavras_gatilho:
        texto = re.sub(r"\b" + palavra + r"\b", "", texto, flags=re.IGNORECASE)
    # Remove conectores
    texto = re.sub(r"\b(de|do|da|um|uma|o|a|os|as|por|para|no|na)\b", " ", texto, flags=re.IGNORECASE)
    # Remove espaços duplos e strip
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


# ─────────────────── Função principal de parse ───────────────────

def interpretar(entrada: str) -> dict:
    """
    Interpreta uma entrada em linguagem natural e retorna um dicionário:
    {
        "intencao": str,          # venda | entrada | saldo | relatorio | cadastro | preco |
                                  # listar | ajuda | sair | desconhecido
        "produto": str | None,
        "quantidade": float | None,
        "preco": float | None,
        "texto_original": str
    }
    """
    original = entrada
    texto = _limpar(entrada)

    resultado = {
        "intencao": "desconhecido",
        "produto": None,
        "quantidade": None,
        "preco": None,
        "texto_original": original,
    }

    # ── Sair ──
    if re.search(_PALAVRAS_SAIR, texto):
        resultado["intencao"] = "sair"
        return resultado

    # ── Relatório ──
    if re.search(_PALAVRAS_RELATORIO, texto):
        resultado["intencao"] = "relatorio"
        # Tenta detectar "hoje", "semana", etc.
        if "hoje" in texto:
            resultado["produto"] = "hoje"
        elif "semana" in texto:
            resultado["produto"] = "semana"
        elif re.search(r"histór|historico", texto):
            resultado["produto"] = "historico"
        else:
            resultado["produto"] = "geral"
        return resultado

    # ── Listar produtos ──
    if re.search(_PALAVRAS_LISTAR, texto) and re.search(r"produto", texto):
        resultado["intencao"] = "listar"
        return resultado

    # ── Cadastro de produto ──
    if re.search(_PALAVRAS_CADASTRO, texto):
        resultado["intencao"] = "cadastro"
        preco = _extrair_preco(texto)
        resultado["preco"] = preco
        # Remove gatilhos
        nome = _extrair_produto(
            texto,
            ["cadastrar", "cadastra", "registrar", "registra", "adicionar produto",
             "novo produto", "criar produto", "produto", "preço", "preco", "r\\$",
             str(preco) if preco else ""]
        )
        nome = re.sub(r"\d+[.,]?\d*", "", nome).strip()
        resultado["produto"] = nome or None
        return resultado

    # ── Atualizar preço ──
    if re.search(_PALAVRAS_PRECO, texto):
        preco = _extrair_preco(texto)
        if preco:
            resultado["intencao"] = "preco"
            resultado["preco"] = preco
            nome = _extrair_produto(
                texto,
                ["preço", "preco", "valor", "custa", "custou",
                 "vende por", "vendo por", "atualizar", "r\\$"]
            )
            nome = re.sub(r"\d+[.,]?\d*", "", nome).strip()
            resultado["produto"] = nome or None
            return resultado

    # ── Venda (saída) ──
    if re.search(_PALAVRAS_VENDA, texto):
        resultado["intencao"] = "venda"
        preco = _extrair_preco(texto)
        resultado["preco"] = preco
        qtd, restante = _extrair_quantidade(texto)
        resultado["quantidade"] = qtd
        nome = _extrair_produto(
            restante,
            ["vendi", "vendei", "saiu", "saíu", "saiu", "sai",
             "coloca na conta", "consumido", "deu saída", "baixei"]
        )
        resultado["produto"] = nome or None
        return resultado

    # ── Entrada (recebimento) ──
    if re.search(_PALAVRAS_ENTRADA, texto):
        resultado["intencao"] = "entrada"
        preco = _extrair_preco(texto)
        resultado["preco"] = preco
        qtd, restante = _extrair_quantidade(texto)
        resultado["quantidade"] = qtd
        nome = _extrair_produto(
            restante,
            ["chegou", "chegaram", "chegar", "entrou", "entraram",
             "entrar", "recebi", "comprei", "adicionei",
             "reposição", "repus", "aumentei"]
        )
        resultado["produto"] = nome or None
        return resultado

    # ── Consulta de saldo ──
    if re.search(_PALAVRAS_SALDO, texto):
        resultado["intencao"] = "saldo"
        nome = _extrair_produto(
            texto,
            ["quanto", "quantos", "quanta", "quantas", "tem", "tenho",
             "restante", "saldo", "estoque", "qtd", "quantidade"]
        )
        # Remove '?' que possa ter sobrado
        nome = nome.replace("?", "").strip() if nome else None
        resultado["produto"] = nome or None
        return resultado

    # ── Ajuda (por último para não capturar '?' de perguntas de saldo) ──
    if re.search(_PALAVRAS_AJUDA, texto):
        resultado["intencao"] = "ajuda"
        return resultado

    return resultado
