# Deadline extraction — ML evaluation (deadline-ml-v7)

## Architecture

| Layer | Method |
|---|---|
| Date finding | ML char TF-IDF + LR window scorer |
| Date normalize | `strptime` + dateparser absolute-time |
| Ranges | Consecutive ML dates linked by separators (`-`, `to`, `and`, …) + ML purpose label |
| Type / category | TF-IDF + Logistic Regression |

## Retrain + reload

```bash
python -m app.training.train_deadline_model
# then either restart uvicorn, or:
curl -X POST http://localhost:8010/admin/reload-models -H "x-internal-api-key: $AI_INTERNAL_API_KEY"
```

## Tests

```bash
python -m unittest discover -s tests -v
```

Includes regression fixtures, ANU circular, and API/PDF integration tests.
