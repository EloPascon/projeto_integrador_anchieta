"""
Transformador: aplica regex e regras de negócio para limpar e padronizar dados.
"""
import re
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

# Padrões regex para normalizar nomes de sabores (variações comuns)
# Essas expressões foram pensadas para capturar erros de digitação comuns e abreviações.
PRODUCT_PATTERNS = [
    # Mussarela: muzzarela, mussarela, muza, muzarela
    (re.compile(r"\b(muzzarel?a|mussarel?a|muza|muzarel?a)\b", re.IGNORECASE), ('PZ001', 'Mussarela')),
    # Calabresa: calabreza, calabresa, calabresa (com erro)
    (re.compile(r"\b(calabres[ao]|calabreza)\b", re.IGNORECASE), ('PZ002', 'Calabresa')),
    # Pepperoni: pepperoni, peperoni
    (re.compile(r"\b(pepperoni|peperoni)\b", re.IGNORECASE), ('PZ003', 'Pepperoni')),
    # Catupiry variations
    (re.compile(r"\b(catupiry|catupyri)\b", re.IGNORECASE), ('PZ004', 'Catupiry')),
    # Portuguesa
    (re.compile(r"\b(portugue?s?a|portugeza)\b", re.IGNORECASE), ('PZ005', 'Portuguesa')),
]

# Função utilitária para limpar nomes
def clean_name(raw: str) -> str:
    """Limpa e padroniza nomes de clientes."""
    if not raw:
        return ''
    # Remover caracteres nulos e excesso de espaços
    s = raw.replace('\x00', ' ').strip()
    # Normalizar espaços múltiplos
    s = re.sub(r"\s+", ' ', s)
    # Capitalizar corretamente (mantendo acentuação quando presente)
    s = s.title()
    return s


def clean_phone(raw: str) -> str:
    """Extrai apenas dígitos e formata em padrão +55 (opcional)."""
    if not raw:
        return ''
    digits = re.sub(r"\D+", '', raw)
    # Normaliza para formato nacional; se já tem 11 dígitos assume DDD + número
    if len(digits) == 11:
        return f"+55{digits}"
    elif len(digits) == 10:
        return f"+55{digits}"
    else:
        return digits


def parse_price(raw: str) -> float:
    """Converte strings de preço com vírgula ou ponto para float."""
    if raw is None:
        return 0.0
    s = str(raw).strip()
    s = s.replace('.', '').replace(',', '.')  # '39,50' -> '39.50', '1.200,00' -> '1200.00'
    try:
        return float(s)
    except ValueError:
        logger.warning('Não foi possível parsear preço: %s', raw)
        return 0.0


def normalize_product_name(token: str) -> Tuple[str, str]:
    """Dado um token (ex: 'Muzzarela'), retorna uma tupla (product_id, product_name) padronizada."""
    t = token.strip()
    # remover quantificadores e caracteres extras
    t = re.sub(r"[^\w\s-]", '', t)
    t = t.strip()

    for pattern, mapping in PRODUCT_PATTERNS:
        if pattern.search(t):
            return mapping

    # Se não houver correspondência, criar um código baseado no nome simplificado
    key = re.sub(r"\W+", '', t).upper()
    if not key:
        key = 'PZZZZ'
    product_id = f'P_{key[:6]}'
    product_name = t.title()
    return product_id, product_name


def parse_items(raw_items: str) -> List[Dict]:
    """Converte uma string de itens bagunçada em uma lista de dicionários {product_id, name, quantity}.

    Exemplos de formatos suportados: '2x Muzzarela; 1x calabreza', '1x muza;1x Pepperoni'
    """
    items = []
    if not raw_items:
        return items
    # Separadores possíveis
    parts = re.split(r"[;|,]", raw_items)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Procurar um padrão como '2x', '1 x', 'x' opcional
        m = re.match(r"^(\d+)\s*[xX]\s*(.+)$", part)
        if m:
            qty = int(m.group(1))
            name = m.group(2).strip()
        else:
            # Tentar extrair número no início
            m2 = re.match(r"^(\d+)\s+(.+)$", part)
            if m2:
                qty = int(m2.group(1))
                name = m2.group(2).strip()
            else:
                # Sem quantidade explícita, assumir 1
                qty = 1
                name = part
        pid, pname = normalize_product_name(name)
        items.append({
            'product_id': pid,
            'product_name': pname,
            'quantity': qty,
        })
    return items


def transform(customers: List[Dict], orders: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Transforma dados brutos em estruturas normalizadas prontas para carregamento.

    Retorna três listas: customers_normalized, products, orders_with_items
    """
    products_map = {}  # product_id -> name
    customers_out = []
    orders_out = []

    # Transformar clientes
    for c in customers:
        try:
            cid = c.get('id')
            name = clean_name(c.get('raw_name'))
            phone = clean_phone(c.get('raw_phone'))
            address = (c.get('raw_address') or '').replace('\x00', ' ').strip()
            customers_out.append({'id': cid, 'name': name, 'phone': phone, 'address': address})
        except Exception as e:
            logger.exception('Erro ao transformar cliente %s: %s', c, e)

    # Transformar pedidos
    for o in orders:
        try:
            oid = o.get('id')
            customer_id = o.get('customer_id')
            date_raw = o.get('raw_date')
            total = parse_price(o.get('raw_total'))
            items = parse_items(o.get('raw_items'))

            # Atualizar mapa de produtos
            for it in items:
                products_map[it['product_id']] = it['product_name']

            orders_out.append({'id': oid, 'customer_id': customer_id, 'date': date_raw, 'total': total, 'items': items})
        except Exception as e:
            logger.exception('Erro ao transformar pedido %s: %s', o, e)

    # Construir lista de produtos única
    products = [{'id': pid, 'name': name} for pid, name in products_map.items()]

    return customers_out, products, orders_out


if __name__ == '__main__':
    # Testes rápidos
    sample = '2x Muzzarela; 1x calabreza'
    print(parse_items(sample))
    print(clean_name(' joAO   silva '))
    print(clean_phone('(11) 9 8765-4321'))
