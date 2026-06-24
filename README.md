# Sistema Inteligente de Integração de Pedidos e Clientes (Pizzaria)

Projeto acadêmico: Etapa 2 — Desenvolvimento da Aplicação

Resumo
- Implementação em Python de um pipeline ETL (Extract, Transform, Load) que simula a integração entre um sistema legado (desktop, dados sujos) e um sistema moderno (banco normalizado).
- Uso de SQLite local para simular o sistema de origem (`data/source.db`) e destino (`data/destination.db`).

Estrutura do projeto
- `config/` — configuração de logs
- `database/` — script para criar bancos de dados de origem e destino
- `etl/` — módulos `extractor.py`, `transformer.py`, `loader.py`
- `data/` — arquivos SQLite gerados
- `logs/` — arquivos de log do ETL
- `main.py` — orquestrador do pipeline

Como executar (VS Code / terminal)
1. (Opcional) criar e ativar um ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Executar o pipeline

```powershell
python main.py
```

O script `main.py` irá:
- criar bancos de exemplo em `data/`
- extrair registros brutos de `customers_raw` e `orders_raw`
- aplicar transformações (limpeza via regex, padronização de nomes de produtos, parse de preços e quantidades)
- carregar os registros normalizados no banco destino
- imprimir no console o estado antes e depois da carga

### Novos sistemas interativos

O repositório agora inclui três formas de usar o fluxo de integração:

- `legacy_system.py` — sistema legado interativo que permite cadastrar clientes pelo terminal e salva os dados brutos em `data/legacy_to_new.json`.
- `new_system.py` — sistema novo que lê esse arquivo gerado e mostra os dados convertidos no formato do sistema moderno.
- `api/server.py` — servidor HTTP simples que expõe um endpoint REST para enviar dados do sistema legado e receber o payload convertido.

Como usar o sistema legado interativo:

```powershell
python legacy_system.py
```

O `legacy_system.py` pede nome, endereço, CEP, sabor da pizza e forma de pagamento, e salva os dados em um JSON legado desorganizado que simula uma tabela bagunçada. Ele usa o conversor de dados para normalizar as informações e, ao final, pergunta se você deseja abrir o `new_system.py` imediatamente.

O `new_system.py` mostra o valor original e o valor convertido lado a lado, incluindo o sabor da pizza e a forma de pagamento.

### API do sistema legado (MCP)

Executar o servidor API:

```powershell
python -m api
```

Endpoints do sistema legado:

- `POST /legacy/convert`
  - Enviar JSON com `raw_customers` como lista de registros legados.
  - Retorna `raw_customers` e `normalized_customers`.
  - Salva em `data/legacy_to_new.json`.
- `GET /legacy/convert`
  - Retorna o último payload convertido salvo.

Endpoints do sistema novo:

- `POST /new/receive`
  - Enviar JSON com `normalized_customers` como lista de registros tratados.
  - Aceita opcionalmente `raw_customers`.
  - Retorna o mesmo payload e salva em `data/new_system_payload.json`.
- `GET /new/receive`
  - Retorna o último payload recebido pelo sistema novo.

Exemplo de requisição para o sistema legado:

```powershell
$body = '{
  "raw_customers": [
    {
      "clienteNome": "  joao  ",
      "dadosEnderecos": {"enderecoTexto": "  rua central 123  ", "cep_code": "12345-678"},
      "pedido": {"saborPizza": "muzzarela", "formaPagamento": "cartao"}
    }
  ]
}'

Invoke-RestMethod -Uri http://127.0.0.1:8000/legacy/convert -Method POST -Body $body -ContentType 'application/json'
```

Exemplo de requisição para o sistema novo:

```powershell
$body = '{
  "normalized_customers": [
    {
      "name": "Joao",
      "address": "Rua Central 123",
      "cep": "12345-678",
      "flavor": "Mussarela",
      "payment_method": "Cartão"
    }
  ]
}'

Invoke-RestMethod -Uri http://127.0.0.1:8000/new/receive -Method POST -Body $body -ContentType 'application/json'
```

Uso de IA no desenvolvimento (para relatório acadêmico)
- As expressões regulares usadas em `etl/transformer.py` foram projetadas para capturar variações de grafia e erros de digitação (ex.: "Muzzarela", "Mussarela", "muza") e mapear para identificadores padrão de produto (ex.: `PZ001` -> "Mussarela").
- A lógica de normalização (regex, parsing de quantidades, normalização de telefones) representa técnicas que podem ser derivadas ou refinadas com o auxílio de modelos de IA para identificar padrões de erro e sugerir regras.
- O sistema evidencia onde a IA ajudou: criação e refinamento das regex e regras de mapeamento entre tokens sujos e IDs canônicos de produto.

Notas de implementação
- O loader usa `executemany` e transações para inserções em lote (bulk inserts).
- Há tratamento de exceções e rollback no `etl/loader.py` para garantir resiliência.

Possíveis extensões
- Adicionar tokenização/contexto semântico via modelos de linguagem para mapear produtos mais ambíguos.
- Adicionar testes automatizados e cobertura.


***Fim***
