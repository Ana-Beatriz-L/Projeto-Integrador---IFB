# Contrato da API | Monitoramento Hidrológico (COGMO)

Este documento é o combinado entre as pessoas do grupo. Se algo precisar mudar, **altere este arquivo primeiro** e avise o grupo.

> Todos os dados são **simulados**. Não descrevem rios reais e não servem para alertas ou decisões.

## 1. Convenções gerais

| Item | Decisão |
|---|---|
| Base da URL | `/api` |
| Barra final | Rotas sem `/` no final (ex: `/api/stations`). Configurar o router com `trailing_slash=False` |
| Formato | JSON, UTF-8 |
| Nomes dos campos | `snake_case`, em inglês |
| Mensagens de erro | Em português |
| Datas | ISO 8601 em UTC, com `Z` no final (ex: `2026-11-02T10:00:00Z`) |
| Unidades | Nível = `m` (metros). Chuva = `mm/h` (milímetros por hora) |
| Métricas | `level` (nível do rio) e `rain` (chuva) |
| IDs de estação | Texto, como no seed (ex: `EST-01`) |
| Aviso de simulação | **Toda** resposta (sucesso ou erro) tem `"simulated": true` |
| Lacunas | Não se inventa leitura. Horário sem leitura simplesmente não aparece na lista |
| Origem dos dados | Seed sintético: 3 estações, 73 horários (72 h até a hora cheia da geração), `source = synthetic` |

Texto padrão do aviso, usado no campo `disclaimer` das respostas de sucesso:

```
Dados simulados para fins didáticos. Não representam rios reais nem devem embasar alertas ou decisões.
```

## 2. Modelo de dados (referência para a API)

Segue as tabelas do `seed.js` original (`stations` e `observations`), com uma linha por métrica e horário.

**Station**

| Campo | Tipo | Observação |
|---|---|---|
| `id` | texto | chave primária (ex: `EST-01`) |
| `name` | texto | nome da estação |
| `river` | texto | nome do rio |
| `municipality` | texto | município |

**Observation** (uma linha por estação + métrica + horário)

| Campo | Tipo | Observação |
|---|---|---|
| `id` | inteiro | chave primária |
| `station` | FK para Station | |
| `metric` | texto | `level` ou `rain` |
| `observed_at` | datetime UTC | horário da leitura |
| `value` | decimal | valor na unidade da métrica |
| `unit` | texto | `m` ou `mm/h` |
| `source` | texto | `synthetic` |

Restrição: única por (`station`, `metric`, `observed_at`), para o seed poder rodar de novo sem duplicar.

## 3. Endpoints

### 3.1 `GET /api/stations`

Lista as estações disponíveis. Sem paginação (são poucas).

**Resposta 200**

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

Ordenação: por `id` crescente.

---

### 3.2 `GET /api/stations/{id}/summary`

Dados da estação e a **última leitura disponível** de cada métrica.

**Resposta 200**

```json
{
  "simulated": true,
  "disclaimer": "Dados simulados para fins didáticos. Não representam rios reais nem devem embasar alertas ou decisões.",
  "station": {
    "id": "EST-01",
    "name": "Estação Aurora",
    "river": "Rio Aurora",
    "municipality": "Vila Aurora"
  },
  "latest_level": {
    "value": 1.13,
    "unit": "m",
    "observed_at": "2026-11-02T10:00:00Z"
  },
  "latest_rain": {
    "value": 1.2,
    "unit": "mm/h",
    "observed_at": "2026-11-02T10:00:00Z"
  }
}
```

Regras:
- `latest_level` e `latest_rain` são independentes: cada um traz a leitura mais recente daquela métrica, com o próprio `observed_at`.
- Se a estação não tiver nenhuma leitura da métrica, o campo vem `null`.

**Erros:** `station_not_found` (404).

---

### 3.3 `GET /api/stations/{id}/series`

Histórico de uma métrica.

**Parâmetros de query**

| Nome | Obrigatório | Tipo | Valores | Padrão |
|---|---|---|---|---|
| `metric` | sim | texto | `level` ou `rain` | (nenhum) |
| `hours` | não | inteiro | de 1 a 72 | 24 |

**Janela de tempo:** a janela termina na **leitura mais recente da estação** (não no horário atual do servidor), porque os dados são sintéticos e fixos. Ou seja, `hours=24` devolve as leituras de `to - 24 h` até `to`, **incluindo as duas pontas** (com dados de hora em hora, são até `hours + 1` pontos; com `hours=72`, os 73 horários do seed).

**Exemplo:** `GET /api/stations/EST-01/series?metric=level&hours=24`

**Resposta 200**

```json
{
  "simulated": true,
  "disclaimer": "Dados simulados para fins didáticos. Não representam rios reais nem devem embasar alertas ou decisões.",
  "station_id": "EST-01",
  "metric": "level",
  "unit": "m",
  "hours": 24,
  "from": "2026-11-01T10:00:00Z",
  "to": "2026-11-02T10:00:00Z",
  "count": 2,
  "data": [
    { "observed_at": "2026-11-02T09:00:00Z", "value": 1.11 },
    { "observed_at": "2026-11-02T10:00:00Z", "value": 1.13 }
  ]
}
```

Regras:
- `data` ordenada por `observed_at` **crescente** (mais antigo primeiro).
- Só entram leituras da métrica pedida. Horários sem leitura (lacunas) ficam de fora.
- Série vazia **não é erro**: devolve 200 com `"count": 0` e `"data": []`.
- Se a estação não tiver nenhuma leitura, `from` e `to` vêm `null`.

**Erros:** `station_not_found` (404), `invalid_metric` (400), `invalid_hours` (400).

## 4. Erros

Formato único para todos os erros:

```json
{
  "simulated": true,
  "error": "invalid_metric",
  "message": "O parâmetro 'metric' é obrigatório e deve ser 'level' ou 'rain'."
}
```

| Situação | Status | `error` | `message` |
|---|---|---|---|
| Estação não existe | 404 | `station_not_found` | Estação não encontrada. |
| `metric` ausente ou diferente de `level`/`rain` | 400 | `invalid_metric` | O parâmetro 'metric' é obrigatório e deve ser 'level' ou 'rain'. |
| `hours` não é inteiro ou está fora de 1 a 72 | 400 | `invalid_hours` | O parâmetro 'hours' deve ser um inteiro entre 1 e 72. |
| Rota inexistente | 404 | `not_found` | Rota não encontrada. |
| Método HTTP não permitido (ex: POST) | 405 | `method_not_allowed` | Método não permitido. Esta API aceita apenas GET. |
| Erro inesperado no servidor | 500 | `internal_error` | Erro interno do servidor. |

Ordem de validação: primeiro a estação (404), depois `metric` e `hours` (400).

## 5. Checklist de conformidade

- [ ] Toda resposta, inclusive de erro, tem `simulated: true`
- [ ] Datas sempre em UTC com `Z`
- [ ] `unit` correta para cada métrica (`m` e `mm/h`)
- [ ] Série ordenada do mais antigo para o mais recente
- [ ] Lacunas não preenchidas
- [ ] Consultas parametrizadas (ORM do Django já cuida disso)
- [ ] Swagger (drf-spectacular) reflete exatamente este contrato

## 6. Histórico de mudanças

| Data | Mudança | Quem |
|---|---|---|
| 2026-11-02 | Versão inicial | grupo |
| 2026-11-02 | Ajustado ao `seed.js`: id de estação em texto, sem latitude/longitude, observações por métrica | grupo |
