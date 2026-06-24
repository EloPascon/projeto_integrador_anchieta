import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE_URL = 'http://127.0.0.1:8000'
HEADERS = {'Content-Type': 'application/json; charset=utf-8'}

legacy_payload = {
    'raw_customers': [
        {
            'clienteNome': '  joao  ',
            'dadosEnderecos': {
                'enderecoTexto': '  rua central 123  ',
                'cep_code': '12345-678',
            },
            'pedido': {
                'saborPizza': 'muzzarela',
                'formaPagamento': 'cartao',
            },
        }
    ]
}

new_payload = {
    'normalized_customers': [
        {
            'name': 'Joao',
            'address': 'Rua Central 123',
            'cep': '12345-678',
            'flavor': 'Mussarela',
            'payment_method': 'Cartao',
        }
    ]
}


def do_request(path, payload=None, method='GET'):
    url = f'{BASE_URL}{path}'
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = Request(url, data=data, method=method)
    for key, value in HEADERS.items():
        req.add_header(key, value)
    try:
        with urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            return resp.status, json.loads(body)
    except HTTPError as err:
        body = err.read().decode('utf-8', errors='ignore')
        return err.code, {'error': body}


def main():
    print('Testing POST /legacy/convert...')
    status, response = do_request('/legacy/convert', legacy_payload, method='POST')
    print(f'Status: {status}')
    print(json.dumps(response, ensure_ascii=False, indent=2))
    print('\nTesting GET /legacy/convert...')
    status, response = do_request('/legacy/convert', method='GET')
    print(f'Status: {status}')
    print(json.dumps(response, ensure_ascii=False, indent=2))

    print('\nTesting POST /new/receive...')
    status, response = do_request('/new/receive', new_payload, method='POST')
    print(f'Status: {status}')
    print(json.dumps(response, ensure_ascii=False, indent=2))
    print('\nTesting GET /new/receive...')
    status, response = do_request('/new/receive', method='GET')
    print(f'Status: {status}')
    print(json.dumps(response, ensure_ascii=False, indent=2))

    if status == 200:
        print('\nAPI test completed successfully.')
    else:
        print('\nAPI test completed with errors.')


if __name__ == '__main__':
    main()
