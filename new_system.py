import json
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path(__file__).resolve().parent / 'data'
PAYLOAD_PATH = DATA_DIR / 'legacy_to_new.json'


try:
    from tabulate import tabulate
except ImportError:
    tabulate = None


def load_payload(path: Path = PAYLOAD_PATH) -> Dict:
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def render_table(rows: List[Dict], headers: List[str]) -> str:
    if tabulate:
        values = [[row.get(h, '') for h in headers] for row in rows]
        return tabulate(values, headers=headers, tablefmt='grid', stralign='left')

    lines = []
    header_line = ' | '.join(headers)
    separator = '-+-'.join('-' * len(h) for h in headers)
    lines.append(header_line)
    lines.append(separator)
    for row in rows:
        lines.append(' | '.join(str(row.get(h, '')) for h in headers))
    return '\n'.join(lines)


def show_new_system_data(payload: Dict) -> None:
    raw_customers = payload.get('raw_customers', [])
    normalized_customers = payload.get('normalized_customers', [])

    if not raw_customers:
        print('Não há dados do sistema legado para mostrar. Execute primeiro python legacy_system.py')
        return

    print('=== Sistema Novo - Visualização de Clientes Convertidos ===')
    rows = []
    for idx, (raw, norm) in enumerate(zip(raw_customers, normalized_customers), start=1):
        rows.append({
            'ID': idx,
            'Nome (orig.)': raw.get('raw_name', ''),
            'Endereço (orig.)': raw.get('raw_address', ''),
            'CEP (orig.)': raw.get('raw_cep', ''),
            'Nome (novo)': norm.get('name', ''),
            'Endereço (novo)': norm.get('address', ''),
            'CEP (novo)': norm.get('cep', ''),
        })

    print(render_table(rows, ['ID', 'Nome (orig.)', 'Endereço (orig.)', 'CEP (orig.)', 'Nome (novo)', 'Endereço (novo)', 'CEP (novo)']))


def run_new_system() -> None:
    if not PAYLOAD_PATH.exists():
        print('Arquivo de dados não encontrado. Execute primeiro python legacy_system.py')
        return

    payload = load_payload(PAYLOAD_PATH)
    show_new_system_data(payload)


if __name__ == '__main__':
    run_new_system()
