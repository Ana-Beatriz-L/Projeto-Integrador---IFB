# API de Monitoramento Hidrológico | Desafio COGMO

API REST em Python + Django que simula o monitoramento de rios e chuvas em estações fictícias.
Todos os dados são **simulados** e não descrevem rios reais.

> TODO (Pessoa 3): completar esta descrição com as decisões do grupo.

## Estrutura

```
config/                 configurações do Django e URLs raiz
monitoring/
  models.py             Station e Observation
  serializers.py        formatos de resposta
  services.py           consultas e regras de negócio
  views.py              endpoints
  exceptions.py         erros no formato do contrato
  management/commands/  import_observations (CSVs -> banco)
  tests/                testes
scripts/generate_seed.py   gera data/stations.csv e data/observations.csv (adaptação do seed.js)
data/                   CSVs da amostra simulada
docs/api-contract.md    contrato da API (fonte da verdade)
```

## Como rodar

### 1. Criar o ambiente virtual

```bash
python -m venv .venv
```

Ativar:

- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- Linux/macOS: `source .venv/bin/activate`

### 2. Instalar os pacotes

```bash
pip install -r requirements.txt
```

### 3. Criar o banco (migrations)

```bash
python manage.py migrate
```

### 4. Gerar e importar os dados sintéticos

```bash
python scripts/generate_seed.py
python manage.py import_observations
```

### 5. Subir o servidor

```bash
python manage.py runserver
```

### 6. Testes

```bash
python manage.py test
```

## Documentação da API

Com o servidor rodando:

- Swagger: http://localhost:8000/api/docs
- Redoc: http://localhost:8000/api/redoc
- Schema OpenAPI: http://localhost:8000/api/schema
- Contrato em texto: [docs/api-contract.md](docs/api-contract.md)

## Modelo de dados

> TODO (Pessoa 1): incluir MER e DER (imagens em `docs/`) e explicar as decisões.

## Divisão de trabalho

| Pessoa | Foco | Arquivos principais |
|---|---|---|
| 1 | Dados e banco | `scripts/generate_seed.py`, `models.py`, `import_observations.py`, MER/DER |
| 2 | API | `services.py`, `views.py`, `serializers.py`, `urls.py` |
| 3 | Documentação e qualidade | drf-spectacular, `README.md`, `tests/`, organização do GitHub |

## Fluxo de Git sugerido

- `main` sempre estável
- uma branch por tarefa (`feat/seed`, `feat/series-endpoint`, `docs/readme`...)
- Pull Request revisado por outra pessoa antes de entrar na `main`
