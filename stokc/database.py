"""
database.py — Camada de acesso ao banco de dados SQLite do Stokc.
Responsável por criar tabelas, buscar/cadastrar produtos e registrar movimentações.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "stokc.db")


def get_connection():
    """Retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabelas():
    """Cria as tabelas necessárias caso não existam."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS produtos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nome        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
            quantidade  REAL    NOT NULL DEFAULT 0,
            preco_custo REAL    NOT NULL DEFAULT 0,
            preco_venda REAL    NOT NULL DEFAULT 0,
            unidade     TEXT    NOT NULL DEFAULT 'unidade'
        );

        CREATE TABLE IF NOT EXISTS movimentacoes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id      INTEGER NOT NULL,
            tipo            TEXT    NOT NULL CHECK(tipo IN ('entrada', 'saida')),
            quantidade      REAL    NOT NULL,
            preco_unitario  REAL    NOT NULL DEFAULT 0,
            timestamp       TEXT    NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );
    """)

    conn.commit()
    conn.close()


# ─────────────────────────── PRODUTOS ────────────────────────────

def buscar_produto(nome: str) -> dict | None:
    """Busca um produto pelo nome (case-insensitive). Retorna dict ou None."""
    conn = get_connection()
    cursor = conn.cursor()
    # Busca exata
    cursor.execute("SELECT * FROM produtos WHERE nome = ? COLLATE NOCASE", (nome,))
    row = cursor.fetchone()
    if row is None:
        # Busca parcial (LIKE)
        cursor.execute(
            "SELECT * FROM produtos WHERE nome LIKE ? COLLATE NOCASE LIMIT 1",
            (f"%{nome}%",)
        )
        row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def cadastrar_produto(nome: str, preco_custo: float = 0.0, preco_venda: float = 0.0, unidade: str = "unidade") -> dict:
    """Cadastra um novo produto no banco. Retorna o produto criado."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, quantidade, preco_custo, preco_venda, unidade) VALUES (?, 0, ?, ?, ?)",
        (nome.strip().lower(), preco_custo, preco_venda, unidade)
    )
    conn.commit()
    prod_id = cursor.lastrowid
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (prod_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def atualizar_preco(nome: str, preco_custo: float | None = None, preco_venda: float | None = None) -> bool:
    """Atualiza o preço de custo e/ou venda de um produto."""
    prod = buscar_produto(nome)
    if not prod:
        return False
    conn = get_connection()
    cursor = conn.cursor()
    novo_custo = preco_custo if preco_custo is not None else prod["preco_custo"]
    novo_venda = preco_venda if preco_venda is not None else prod["preco_venda"]
    cursor.execute(
        "UPDATE produtos SET preco_custo = ?, preco_venda = ? WHERE id = ?",
        (novo_custo, novo_venda, prod["id"])
    )
    conn.commit()
    conn.close()
    return True


def atualizar_estoque(produto_id: int, delta: float):
    """Soma ou subtrai quantidade do estoque de um produto."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE produtos SET quantidade = quantidade + ? WHERE id = ?",
        (delta, produto_id)
    )
    conn.commit()
    conn.close()


def listar_produtos() -> list[dict]:
    """Retorna todos os produtos cadastrados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos ORDER BY nome")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─────────────────────────── MOVIMENTAÇÕES ────────────────────────

def registrar_movimentacao(produto_id: int, tipo: str, quantidade: float, preco_unitario: float = 0.0):
    """Registra uma movimentação (entrada ou saída) no histórico."""
    conn = get_connection()
    cursor = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO movimentacoes (produto_id, tipo, quantidade, preco_unitario, timestamp) VALUES (?, ?, ?, ?, ?)",
        (produto_id, tipo, quantidade, preco_unitario, ts)
    )
    conn.commit()
    conn.close()


def listar_movimentacoes(data_inicio: str | None = None, data_fim: str | None = None) -> list[dict]:
    """Retorna movimentações, opcionalmente filtradas por período (YYYY-MM-DD)."""
    conn = get_connection()
    cursor = conn.cursor()
    if data_inicio and data_fim:
        cursor.execute("""
            SELECT m.*, p.nome as produto_nome
            FROM movimentacoes m
            JOIN produtos p ON p.id = m.produto_id
            WHERE date(m.timestamp) BETWEEN ? AND ?
            ORDER BY m.timestamp DESC
        """, (data_inicio, data_fim))
    elif data_inicio:
        cursor.execute("""
            SELECT m.*, p.nome as produto_nome
            FROM movimentacoes m
            JOIN produtos p ON p.id = m.produto_id
            WHERE date(m.timestamp) >= ?
            ORDER BY m.timestamp DESC
        """, (data_inicio,))
    else:
        cursor.execute("""
            SELECT m.*, p.nome as produto_nome
            FROM movimentacoes m
            JOIN produtos p ON p.id = m.produto_id
            ORDER BY m.timestamp DESC
            LIMIT 50
        """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
