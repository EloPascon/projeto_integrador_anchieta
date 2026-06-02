"""
Loader: carrega os dados transformados no banco destino usando bulk inserts.
Inclui tratamento de erros, logs e rollback em caso de falha.
"""
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parents[1]
DEST_DB = BASE_DIR / 'data' / 'destination.db'


def load(customers: List[Dict], products: List[Dict], orders: List[Dict]):
    """Carrega clientes, produtos, pedidos e itens no banco destino.

    Usa transações e executemany para desempenho (bulk inserts).
    """
    conn = sqlite3.connect(str(DEST_DB))
    cur = conn.cursor()
    try:
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('BEGIN')

        # Inserir produtos (UPSERT simplificado via INSERT OR REPLACE)
        prod_tuples = [(p['id'], p['name']) for p in products]
        logger.info('Inserindo %d produtos', len(prod_tuples))
        if prod_tuples:
            cur.executemany('INSERT OR REPLACE INTO products (id, name) VALUES (?, ?)', prod_tuples)

        # Inserir clientes (note: usamos o id do sistema legado como referência temporária)
        cust_tuples = [(c['id'], c['name'], c['phone'], c['address']) for c in customers]
        logger.info('Inserindo %d clientes', len(cust_tuples))
        if cust_tuples:
            # Como a tabela customers usa autoincrement, inserimos sem preservar id do sistema antigo.
            # Para manter referência, podemos inserir e mapear um campo auxiliar, mas para simplicidade,
            # vamos inserir mantendo o id legado no campo id (aceitável para SQLite em estudo acadêmico).
            cur.executemany('INSERT OR REPLACE INTO customers (id, name, phone, address) VALUES (?, ?, ?, ?)', cust_tuples)

        # Inserir pedidos e itens em lote
        order_tuples = []
        order_items_tuples = []
        for o in orders:
            order_tuples.append((o['id'], o['customer_id'], o['date'], o['total']))
            for it in o['items']:
                # preço unitário não está disponível nos dados brutos; deixar None ou estimado
                order_items_tuples.append((o['id'], it['product_id'], it['quantity'], None))

        logger.info('Inserindo %d pedidos e %d itens', len(order_tuples), len(order_items_tuples))
        if order_tuples:
            cur.executemany('INSERT OR REPLACE INTO orders (id, customer_id, date, total) VALUES (?, ?, ?, ?)', order_tuples)
        if order_items_tuples:
            cur.executemany('INSERT OR REPLACE INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)', order_items_tuples)

        conn.commit()
        logger.info('Carga concluída com sucesso')
    except Exception as e:
        conn.rollback()
        logger.exception('Falha ao carregar dados: %s', e)
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    print('Loader test placeholder')
