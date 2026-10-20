-- ============================================================
-- schema.sql  —  Script de criação do banco de dados do Stokc
-- SGBD: SQLite 3 (nativo no Python)
-- Executar: Python executa automaticamente ao iniciar app.py
--           OU manualmente: sqlite3 stokc.db < database/schema.sql
-- ============================================================

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS produtos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    quantidade  REAL    NOT NULL DEFAULT 0,
    preco_custo REAL    NOT NULL DEFAULT 0,
    preco_venda REAL    NOT NULL DEFAULT 0,
    unidade     TEXT    NOT NULL DEFAULT 'unidade'
);

-- Tabela de movimentações (histórico de entradas e saídas)
CREATE TABLE IF NOT EXISTS movimentacoes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id      INTEGER NOT NULL,
    tipo            TEXT    NOT NULL CHECK(tipo IN ('entrada', 'saida')),
    quantidade      REAL    NOT NULL,
    preco_unitario  REAL    NOT NULL DEFAULT 0,
    timestamp       TEXT    NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- ── Dados iniciais para demonstração (opcional) ──────────────
-- Descomente as linhas abaixo para popular o banco com exemplos:

-- INSERT OR IGNORE INTO produtos (nome, quantidade, preco_custo, preco_venda, unidade)
-- VALUES
--   ('arroz',        50, 4.50, 7.00, 'kg'),
--   ('feijao',       30, 6.00, 9.50, 'kg'),
--   ('refrigerante', 24, 3.00, 5.50, 'unidade');
