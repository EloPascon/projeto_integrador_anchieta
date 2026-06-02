"""
Extrator: lê os dados sujos do banco de origem.
"""
import sqlite3
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DB = BASE_DIR / 'data' / 'source.db'


def extract_customers() -> List[Dict]:
    """Extrai todos os clientes da tabela customers_raw."""
    conn = sqlite3.connect(str(SOURCE_DB))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM customers_raw')
    rows = cur.fetchall()
    results = [dict(r) for r in rows]
    conn.close()
    return results


def extract_orders() -> List[Dict]:
    """Extrai todos os pedidos da tabela orders_raw."""
    conn = sqlite3.connect(str(SOURCE_DB))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM orders_raw')
    rows = cur.fetchall()
    results = [dict(r) for r in rows]
    conn.close()
    return results


if __name__ == '__main__':
    print('Testing extractor...')
    print(extract_customers())
    print(extract_orders())
