"""
Orquestrador do pipeline ETL.
Executa: criar DBs de exemplo -> extrair -> transformar -> carregar -> mostrar resultados.
"""
import logging
from config.logging_config import setup_logging
from database import setup_db
from etl import extractor, transformer, loader
from pathlib import Path
import sqlite3

logger = setup_logging()
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'


def snapshot_source():
    from etl.extractor import extract_customers, extract_orders
    print('\n--- Fonte (raw) - Clientes ---')
    for c in extract_customers():
        print(c)
    print('\n--- Fonte (raw) - Pedidos ---')
    for o in extract_orders():
        print(o)


def snapshot_destination():
    dest_db = DATA_DIR / 'destination.db'
    conn = sqlite3.connect(str(dest_db))
    cur = conn.cursor()
    print('\n--- Destino - Customers ---')
    for row in cur.execute('SELECT * FROM customers'):
        print(row)
    print('\n--- Destino - Products ---')
    for row in cur.execute('SELECT * FROM products'):
        print(row)
    print('\n--- Destino - Orders ---')
    for row in cur.execute('SELECT * FROM orders'):
        print(row)
    print('\n--- Destino - Order Items ---')
    for row in cur.execute('SELECT * FROM order_items'):
        print(row)
    conn.close()


def run_pipeline():
    logger.info('Criando bancos de exemplo...')
    setup_db.create_source_db()
    setup_db.create_destination_db()

    logger.info('Extraindo dados...')
    customers = extractor.extract_customers()
    orders = extractor.extract_orders()

    logger.info('Snapshot antes da transformação:')
    snapshot_source()

    logger.info('Transformando dados...')
    customers_norm, products, orders_norm = transformer.transform(customers, orders)

    logger.info('Carregando dados no destino...')
    loader.load(customers_norm, products, orders_norm)

    logger.info('Snapshot após carga:')
    snapshot_destination()


if __name__ == '__main__':
    run_pipeline()
