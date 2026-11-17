# COGMO — API de Monitoramento Hidrológico

API REST para consulta de dados hidrológicos simulados. O projeto foi desenvolvido
como parte do Projeto Integrador do IFB e permite consultar estações de
monitoramento, últimas leituras e séries históricas de nível de rio e chuva.

> **Atenção:** todos os dados são sintéticos e têm finalidade exclusivamente
> didática. Eles não representam rios reais e não devem ser usados para alertas,
> previsões ou decisões.

## Sumário

- [Tecnologias](#tecnologias)
- [Como executar](#como-executar)
- [Dados de exemplo](#dados-de-exemplo)
- [API](#api)
- [Documentação interativa](#documentação-interativa)
- [Modelo de dados](#modelo-de-dados)
- [Testes](#testes)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Configuração](#configuração)
- [Documentação complementar](#documentação-complementar)

## Tecnologias

- Python 3.14 ou compatível
- Django 5.2
- Django REST Framework
- drf-spectacular (OpenAPI, Swagger UI e ReDoc)
- django-cors-headers
- SQLite
- CSV para geração e distribuição dos dados sintéticos

As dependências estão listadas em [`requirements.txt`](requirements.txt).

## Como executar

### 1. Clonar e entrar no projeto

```bash
git clone https://github.com/Ana-Beatriz-L/Projeto-Integrador---IFB.git
cd Projeto-Integrador---IFB
```

### 2. Criar e ativar um ambiente virtual

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Criar as tabelas do banco

```bash
python manage.py migrate
```

O banco padrão é o arquivo [`db.sqlite3`](db.sqlite3), configurado para uso
local e didático.

### 5. Gerar e importar os dados

Os CSVs já ficam disponíveis em [`data/`](data/). Para gerar uma nova amostra
com três estações, 73 horários e duas métricas por horário:

```bash
python scripts/generate_seed.py
```

Por padrão, o último horário é a hora cheia atual em UTC. Para gerar dados
reprodutíveis, informe o horário final:

```bash
python scripts/generate_seed.py --end 2026-11-02T10:00:00Z
```

Em seguida, importe os arquivos para o SQLite:

```bash
python manage.py import_observations
```

O comando aceita caminhos alternativos:

```bash
python manage.py import_observations \
  --stations caminho/para/stations.csv \
  --observations caminho/para/observations.csv
```

A importação é repetível: estações são atualizadas e observações duplicadas
não são inseridas novamente.

### 6. Iniciar o servidor

```bash
python manage.py runserver
```

O servidor ficará disponível em <http://127.0.0.1:8000/>.

## API

A base da API é `/api`. As rotas não usam barra final e aceitam somente o
método `GET`.

### Listar estações

```http
GET /api/stations
```

Exemplo:

```bash
curl http://127.0.0.1:8000/api/stations
```

Resposta:

```json
{
  "simulated": true,
  "disclaimer": "Dados simulados para fins didáticos. Não representam rios reais nem devem embasar alertas ou decisões.",
  "count": 3,
  "results": [
    {
      "id": "EST-01",
      "name": "Estação Aurora",
      "river": "Rio Aurora",
      "municipality": "Vila Aurora"
    }
  ]
}
```

### Consultar o resumo de uma estação

```http
GET /api/stations/{station_id}/summary
```

Exemplo:

```bash
curl http://127.0.0.1:8000/api/stations/EST-01/summary
```

A resposta contém a estação e a leitura mais recente de cada métrica. Caso não
exista leitura de uma métrica, seu campo será `null`.

### Consultar uma série histórica

```http
GET /api/stations/{station_id}/series?metric={metric}&hours={hours}
```

Parâmetros:

| Parâmetro | Obrigatório | Valores | Padrão |
|---|---:|---|---:|
| `metric` | Sim | `level` ou `rain` | — |
| `hours` | Não | inteiro entre `1` e `72` | `24` |

Exemplos:

```bash
# Nível do rio nas últimas 24 horas
curl "http://127.0.0.1:8000/api/stations/EST-01/series?metric=level"

# Chuva nas últimas 72 horas
curl "http://127.0.0.1:8000/api/stations/EST-01/series?metric=rain&hours=72"
```

A janela termina na leitura mais recente disponível para a estação e métrica,
não no horário atual do servidor. Os dados são retornados em ordem crescente de
`observed_at`; lacunas não são preenchidas.

As unidades são:

- `level`: metros (`m`);
- `rain`: milímetros por hora (`mm/h`).

### Respostas de erro

Todas as respostas, inclusive erros, contêm `"simulated": true`:

```json
{
  "simulated": true,
  "error": "invalid_metric",
  "message": "O parâmetro 'metric' é obrigatório e deve ser 'level' ou 'rain'."
}
```

| Situação | HTTP | `error` |
|---|---:|---|
| Estação inexistente | 404 | `station_not_found` |
| Rota inexistente | 404 | `not_found` |
| Métrica ausente ou inválida | 400 | `invalid_metric` |
| `hours` inválido | 400 | `invalid_hours` |
| Método diferente de `GET` | 405 | `method_not_allowed` |
| Falha inesperada | 500 | `internal_error` |

## Documentação interativa

Com o servidor em execução, acesse:

- [Swagger UI](http://127.0.0.1:8000/api/docs)
- [ReDoc](http://127.0.0.1:8000/api/redoc)
- [Especificação OpenAPI](http://127.0.0.1:8000/api/schema)
- [Painel administrativo](http://127.0.0.1:8000/admin/)

O painel administrativo usa o sistema de autenticação padrão do Django. Para
criar um usuário administrador:

```bash
python manage.py createsuperuser
```

## Modelo de dados

O banco possui duas entidades principais:

### `Station`

| Campo | Descrição |
|---|---|
| `id` | Identificador textual, como `EST-01` |
| `name` | Nome da estação |
| `river` | Nome do rio |
| `municipality` | Município |

### `Observation`

| Campo | Descrição |
|---|---|
| `station` | Estação relacionada |
| `metric` | `level` ou `rain` |
| `observed_at` | Data e hora da leitura em UTC |
| `value` | Valor numérico da leitura |
| `unit` | `m` ou `mm/h` |
| `source` | Origem do dado, normalmente `synthetic` |

Existe uma restrição de unicidade para a combinação `station`, `metric` e
`observed_at`, impedindo duplicidade durante novas importações.

Os diagramas estão disponíveis em [`docs/DER.png`](docs/DER.png) e
[`docs/MER.png`](docs/MER.png).

## Testes

Execute a suíte de testes do Django com:

```bash
python manage.py test
```

Para validar a configuração do projeto:

```bash
python manage.py check
```

## Estrutura do projeto

```text
.
├── config/                         # Configurações, URLs e entrada WSGI/ASGI
├── data/                           # CSVs e guia de apresentação
├── docs/                           # Diagramas e contrato da API
├── monitoring/                     # Aplicação Django da API
│   ├── management/commands/        # Comando de importação dos CSVs
│   ├── migrations/                 # Migrações do banco
│   ├── models.py                   # Station e Observation
│   ├── serializers.py              # Formatos JSON
│   ├── services.py                 # Regras de negócio e consultas
│   ├── urls.py                     # Rotas da aplicação
│   └── views.py                    # Endpoints HTTP
├── scripts/generate_seed.py        # Geração dos dados sintéticos
├── manage.py                       # CLI do Django
├── db.sqlite3                      # Banco local
└── requirements.txt                # Dependências Python
```

## Configuração

As configurações abaixo podem ser definidas por variáveis de ambiente:

| Variável | Padrão | Finalidade |
|---|---|---|
| `DJANGO_SECRET_KEY` | chave de desenvolvimento | Chave secreta do Django |
| `DJANGO_DEBUG` | `1` | Ativa (`1`) ou desativa (`0`) o modo debug |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Lista de hosts permitidos, separada por vírgulas |

Em produção, defina uma chave secreta própria, desative o debug e configure
explicitamente os hosts permitidos. O projeto usa UTC para armazenar e
serializar datas.

## Documentação complementar

- [Contrato completo da API](docs/api-contract.md)
- [Guia rápido para apresentação](data/GUIA_APRESENTAÇÃO.md)
- [Diagrama de entidade-relacionamento](docs/DER.png)
- [Modelo entidade-relacionamento](docs/MER.png)
