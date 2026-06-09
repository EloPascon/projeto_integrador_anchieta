import json
import re
from pathlib import Path
from typing import Dict, List

from etl.transformer import clean_name

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = DATA_DIR / "legacy_to_new.json"


def clean_address(raw: str) -> str:
    if not raw:
        return ''
    address = str(raw).replace(chr(0), ' ').strip()
    address = re.sub(r"\s+", ' ', address)
    return address.title()


def clean_cep(raw: str) -> str:
    if not raw:
        return ''
    digits = re.sub(r"\D+", '', str(raw))
    if len(digits) == 8:
        return f"{digits[:5]}-{digits[5:]}"
    return digits


def normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]", '', str(key or '').strip().lower())


def find_raw_value(source: Dict, aliases: List[str]) -> str:
    if not isinstance(source, dict):
        return ''
    normalized_aliases = {normalize_key(alias) for alias in aliases}
    for key, value in source.items():
        if normalize_key(key) in normalized_aliases and value not in (None, ''):
            return value
    for value in source.values():
        if isinstance(value, dict):
            found = find_raw_value(value, aliases)
            if found:
                return found
    return ''


def clean_pizza_flavor(raw: str) -> str:
    if not raw:
        return ''
    s = re.sub(r"[^ -~]+", '', str(raw)).strip().lower()
    s = re.sub(r"[^\w\s]", ' ', s)
    s = re.sub(r"\s+", ' ', s).strip()
    mapping = {
        'muzzarela': 'Mussarela',
        'mussarela': 'Mussarela',
        'muza': 'Mussarela',
        'muzarela': 'Mussarela',
        'calabresa': 'Calabresa',
        'calabreza': 'Calabresa',
        'pepperoni': 'Pepperoni',
        'peperoni': 'Pepperoni',
        'catupiry': 'Catupiry',
        'portuguesa': 'Portuguesa',
    }
    for key, value in mapping.items():
        if key in s:
            return value
    return s.title()


def clean_payment_method(raw: str) -> str:
    if not raw:
        return ''
    s = str(raw).strip().lower()
    s = s.replace('ã', 'a').replace('á', 'a').replace('é', 'e').replace('ê', 'e').replace('í', 'i').replace('ó', 'o').replace('ô', 'o').replace('ú', 'u').replace('ç', 'c')
    s = re.sub(r"[^\w\s]", ' ', s)
    s = re.sub(r"\s+", ' ', s).strip()
    mapping = {
        'cartao': 'Cartão',
        'cartao credito': 'Cartão de Crédito',
        'cartao de credito': 'Cartão de Crédito',
        'credito': 'Cartão de Crédito',
        'debito': 'Cartão de Débito',
        'cartao debito': 'Cartão de Débito',
        'dinheiro': 'Dinheiro',
        'boleto': 'Boleto',
        'pix': 'PIX',
    }
    if s in mapping:
        return mapping[s]
    return s.title()


def normalize_customer(raw_customer: Dict) -> Dict:
    raw_name = find_raw_value(raw_customer, ['raw_name', 'nome_cliente', 'clientenome', 'nome', 'cliente'])
    raw_address = find_raw_value(raw_customer, ['raw_address', 'endereco', 'enderecoTexto', 'info_endereco', 'address'])
    raw_cep = find_raw_value(raw_customer, ['raw_cep', 'cep', 'cep_raw', 'cep_code', 'postal_code', 'codigoPostal'])
    raw_flavor = find_raw_value(raw_customer, ['raw_flavor', 'sabor', 'saborPizza', 'pizzasabor', 'pizza'])
    raw_payment = find_raw_value(raw_customer, ['raw_payment', 'payment', 'formapagamento', 'pagamento', 'payment_method'])

    return {
        'name': clean_name(raw_name),
        'address': clean_address(raw_address),
        'cep': clean_cep(raw_cep),
        'flavor': clean_pizza_flavor(raw_flavor),
        'payment_method': clean_payment_method(raw_payment),
    }


def normalize_customers(raw_customers: List[Dict]) -> List[Dict]:
    return [normalize_customer(raw) for raw in raw_customers]


def save_payload(payload: Dict, path: Path = OUTPUT_PATH):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return path


def load_payload(path: Path = OUTPUT_PATH) -> Dict:
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)
