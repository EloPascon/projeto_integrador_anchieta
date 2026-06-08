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
    address = str(raw).replace('\x00', ' ').strip()
    address = re.sub(r"\s+", ' ', address)
    return address.title()


def clean_cep(raw: str) -> str:
    if not raw:
        return ''
    digits = re.sub(r"\D+", '', str(raw))
    if len(digits) == 8:
        return f"{digits[:5]}-{digits[5:]}"
    return digits


def normalize_customer(raw_customer: Dict) -> Dict:
    return {
        'name': clean_name(raw_customer.get('raw_name', '')),
        'address': clean_address(raw_customer.get('raw_address', '')),
        'cep': clean_cep(raw_customer.get('raw_cep', '')),
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
