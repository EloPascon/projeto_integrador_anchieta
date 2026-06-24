import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, List, Optional

from etl.converter import normalize_customers, save_payload, OUTPUT_PATH

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)
NEW_PAYLOAD_PATH = DATA_DIR / 'new_system_payload.json'


class LegacyAPIHandler(BaseHTTPRequestHandler):
    def _set_response(self, status: int = 200, content_type: str = 'application/json; charset=utf-8'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_response()

    def do_GET(self):
        if self.path == '/legacy/convert':
            self._handle_legacy_get()
            return

        if self.path == '/new/receive':
            self._handle_new_get()
            return

        self._set_response(404)
        self.wfile.write(json.dumps({'error': 'Endpoint não encontrado'}).encode('utf-8'))

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        raw_body_bytes = self.rfile.read(length)
        raw_body = self._decode_request_body(raw_body_bytes)
        try:
            data = json.loads(raw_body) if raw_body else {}
        except json.JSONDecodeError:
            self._set_response(400)
            self.wfile.write(json.dumps({'error': 'JSON inválido'}, ensure_ascii=False).encode('utf-8'))
            return

        if self.path == '/legacy/convert':
            self._handle_legacy_post(data)
            return

        if self.path == '/new/receive':
            self._handle_new_post(data)
            return

        self._set_response(404)
        self.wfile.write(json.dumps({'error': 'Endpoint não encontrado'}).encode('utf-8'))

    def _handle_legacy_get(self):
        if not OUTPUT_PATH.exists():
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Nenhum payload convertido disponível'}).encode('utf-8'))
            return

        payload = self._load_saved_payload(OUTPUT_PATH)
        self._set_response(200)
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))

    def _handle_new_get(self):
        if not NEW_PAYLOAD_PATH.exists():
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Nenhum payload do sistema novo disponível'}).encode('utf-8'))
            return

        payload = self._load_saved_payload(NEW_PAYLOAD_PATH)
        self._set_response(200)
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))

    def _handle_legacy_post(self, data: Dict):
        raw_customers = self._extract_customers(data)
        if raw_customers is None:
            self._set_response(400)
            self.wfile.write(json.dumps({'error': 'O payload deve conter "raw_customers" como lista'}).encode('utf-8'))
            return

        normalized_customers = normalize_customers(raw_customers)
        payload = {
            'raw_customers': raw_customers,
            'normalized_customers': normalized_customers,
        }
        save_payload(payload, OUTPUT_PATH)

        self._set_response(200)
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))

    def _handle_new_post(self, data: Dict):
        if not isinstance(data, dict):
            self._set_response(400)
            self.wfile.write(json.dumps({'error': 'Payload inválido'}).encode('utf-8'))
            return

        normalized_customers = data.get('normalized_customers')
        if not isinstance(normalized_customers, list):
            self._set_response(400)
            self.wfile.write(json.dumps({'error': 'O payload deve conter "normalized_customers" como lista'}).encode('utf-8'))
            return

        raw_customers = data.get('raw_customers', [])
        if not isinstance(raw_customers, list):
            raw_customers = []

        payload = {
            'raw_customers': raw_customers,
            'normalized_customers': normalized_customers,
        }
        save_payload(payload, NEW_PAYLOAD_PATH)

        self._set_response(200)
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))

    def _decode_request_body(self, raw_body_bytes: bytes) -> str:
        try:
            return raw_body_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return raw_body_bytes.decode('cp1252')
            except UnicodeDecodeError:
                return raw_body_bytes.decode('latin-1', errors='replace')

    def _extract_customers(self, payload: Dict) -> Optional[List[Dict]]:
        if not isinstance(payload, dict):
            return None
        customers = payload.get('raw_customers')
        if not isinstance(customers, list):
            return None
        return [c for c in customers if isinstance(c, dict)]

    def _load_saved_payload(self, path: Path) -> Dict:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)


def run_server(host: str = '127.0.0.1', port: int = 8000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, LegacyAPIHandler)
    print(f'API do sistema legado rodando em http://{host}:{port}')
    print('POST /legacy/convert com JSON {"raw_customers": [...] } para converter dados')
    print('GET  /legacy/convert para ler o último payload convertido')
    print('POST /new/receive com JSON {"normalized_customers": [...] } para enviar dados tratados ao sistema novo')
    print('GET  /new/receive para ler o último payload do sistema novo')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServidor interrompido pelo usuário')
        httpd.server_close()


if __name__ == '__main__':
    run_server()
