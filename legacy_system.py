import json
from pathlib import Path
from typing import Dict, List

from etl.converter import normalize_customers, save_payload, OUTPUT_PATH

DATA_DIR = Path(__file__).resolve().parent / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)


try:
    from tabulate import tabulate
except ImportError:
    tabulate = None


def prompt_input(prompt: str, required: bool = True) -> str:
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print('Este campo é obrigatório. Tente novamente.')


def collect_customers() -> List[Dict]:
    customers = []
    print('=== Sistema Legado - Cadastro de Clientes ===')
    print('Digite os dados do cliente. Para encerrar, deixe o nome vazio e pressione Enter.')
    while True:
        raw_name = prompt_input('Nome: ', required=False)
        if not raw_name:
            break
        raw_address = prompt_input('Endereço: ')
        raw_cep = prompt_input('CEP: ')
        customers.append({
            'raw_name': raw_name,
            'raw_address': raw_address,
            'raw_cep': raw_cep,
        })
        print('Cliente adicionado. Informe o próximo ou deixe o nome vazio para finalizar.\n')

    return customers


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


def show_summary(raw_customers: List[Dict], normalized_customers: List[Dict]) -> None:
    print('\n=== Dados enviados pelo sistema legado ===')
    raw_rows = [
        {'Nome': r['raw_name'], 'Endereço': r['raw_address'], 'CEP': r['raw_cep']}
        for r in raw_customers
    ]
    print(render_table(raw_rows, ['Nome', 'Endereço', 'CEP']))

    print('\n=== Dados após conversão para o sistema novo ===')
    normalized_rows = [
        {'Nome': n['name'], 'Endereço': n['address'], 'CEP': n['cep']}
        for n in normalized_customers
    ]
    print(render_table(normalized_rows, ['Nome', 'Endereço', 'CEP']))


def prompt_yes_no(prompt: str) -> bool:
    while True:
        answer = input(prompt).strip().lower()
        if answer in ('s', 'sim'):
            return True
        if answer in ('n', 'nao', 'não', ''):
            return False
        print('Responda S para sim ou N para não.')


def run_legacy_system() -> None:
    raw_customers = collect_customers()
    if not raw_customers:
        print('\nNenhum cliente foi cadastrado. Encerrando.')
        return

    normalized_customers = normalize_customers(raw_customers)
    payload = {
        'raw_customers': raw_customers,
        'normalized_customers': normalized_customers,
    }
    save_payload(payload, OUTPUT_PATH)

    print(f'\nDados salvos em: {OUTPUT_PATH}')
    show_summary(raw_customers, normalized_customers)

    if prompt_yes_no('\nDeseja abrir o sistema novo agora? [S/N]: '):
        from new_system import run_new_system
        run_new_system()
    else:
        print('\nExecução concluída. Para ver os dados posteriormente, execute python new_system.py.')


if __name__ == '__main__':
    run_legacy_system()
