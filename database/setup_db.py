"""
Cria os bancos SQLite de origem (com dados sujos) e destino (normalizado).
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_DB = DATA_DIR / 'source.db'
DEST_DB = DATA_DIR / 'destination.db'


def create_source_db():
    """Cria um banco de origem com dados bagunçados representando o sistema antigo."""
    if SOURCE_DB.exists():
        try:
            SOURCE_DB.unlink()
        except Exception:
            pass

    conn = sqlite3.connect(str(SOURCE_DB))
    cur = conn.cursor()

    # Tabela de clientes (dados sujos)
    cur.execute("""
    CREATE TABLE customers_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_name TEXT,
        raw_phone TEXT,
        raw_address TEXT
    )
    """)

    # Tabela de pedidos (dados sujos) - itens armazenados como texto bagunçado
    cur.execute("""
    CREATE TABLE orders_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        raw_items TEXT,
        raw_date TEXT,
        raw_total TEXT
    )
    """)

    # Inserir alguns dados sujos de exemplo
    customers = [
        ("joao silva  ", "(11) 9 8765-4321", "Rua das Flores, 123"),
        ("MARIA de souza", "11-987654321", "Av. Brasil, 45 apt 12"),
        ("Carlos  Oliveira", "(11)98765 4321", "Rua das Acacias, 9"),
        ("Ana-Maria", "(+55)11 98765-4321", "Praca Central, s/n"),
    ]

    cur.executemany("INSERT INTO customers_raw (raw_name, raw_phone, raw_address) VALUES (?, ?, ?)", customers)

    # Pedidos com nomes de sabores com erros de digitação e formatos variados
    orders = [
        (1, "2x Muzzarela; 1x calabreza", "2026-05-01", "59.90"),
        (2, "1x muza;1x Pepperoni", "2026/05/02", "39,50"),
        (3, "3x Mussarela;2x catupiry", "02-05-2026", "120.00"),
        (4, "1x portugeza; 1x calabresa", "2026.05.03", "75.00"),
    ]
    cur.executemany("INSERT INTO orders_raw (customer_id, raw_items, raw_date, raw_total) VALUES (?, ?, ?, ?)", orders)

    conn.commit()
    conn.close()


def create_destination_db():
    """Cria um banco destino normalizado (tabelas relacionais)."""
    if DEST_DB.exists():
        try:
            DEST_DB.unlink()
        except Exception:
            pass

    conn = sqlite3.connect(str(DEST_DB))
    cur = conn.cursor()

    # Tabelas normalizadas
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        address TEXT
    );

    CREATE TABLE products (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    );

    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        date TEXT,
        total REAL,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );

    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_source_db()
    create_destination_db()
    print(f"Created source DB at: {SOURCE_DB}")
    print(f"Created destination DB at: {DEST_DB}")
