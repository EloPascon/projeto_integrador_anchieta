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
