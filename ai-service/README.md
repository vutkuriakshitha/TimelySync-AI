# TimelySync AI Microservice

A standalone Python (FastAPI) machine-learning service that powers every
predictive feature in TimelySync. It is called by the Java Spring Boot
backend over REST - the backend never makes predictions itself.

## Why a separate service?

- Keeps ML dependencies (scikit-learn, pandas, numpy) out of the JVM app.
- Can be scaled, deployed, and retrained independently of the backend.
- Degrades gracefully: if this service is down, the backend falls back to a
  clearly-labelled conservative estimate rather than crashing (see
  `AiClientService` in the backend).

## Models

All models are real, trained scikit-learn models (no if/else heuristics at
inference time):

| Endpoint | Model | Type |
|---|---|---|
| `POST /predict/failure` | Task failure-risk probability | `RandomForestClassifier` (binary) |
| `POST /predict/impact` | Deadline-miss impact severity | `RandomForestClassifier` (multi-class) |
| `POST /predict/postanalysis` | Root-cause of a late completion | `RandomForestClassifier` (multi-class) |
| `POST /predict/intake` | Smart task intake (category + priority) | TF-IDF + `LogisticRegression` (x2), plus `dateparser` for due-date extraction |
| `POST /predict/deadline-extraction` | OCR / notice deadline extraction from pasted text | TF-IDF + `LogisticRegression` deadline-type classifier, `dateparser`, range detection |
| `POST /predict/document-deadlines` | Upload PDF/image → OCR → deadline extraction | `pdfplumber` / `pytesseract` + deadline extractor |

Since this is a brand new product with no historical data yet, the models
are trained on **structured synthetic data** whose feature/label
relationships mirror real time-management dynamics, with random noise so
the relationship must be *learned* rather than memorised (see
`app/training/data_generator.py`). Every prediction, and every real
completed-task outcome the backend reports back via
`POST /feedback/outcome`, is persisted to MongoDB (`ai_predictions`,
`ai_outcome_feedback`, `ai_training_runs` collections) so a future
retraining job can blend in real user data as it accumulates.

## Running locally

```bash
cd ai-service
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # then edit MONGODB_URI / AI_INTERNAL_API_KEY

# Train all models once (writes .joblib artifacts into ./models)
python -m app.training.train_all

# Start the API
uvicorn app.main:app --reload --port 8000
```

Verify it's up: `GET http://localhost:8000/health` -> `{"status": "ok", "modelsReady": true}`

## Retraining

Re-run `python -m app.training.train_all` any time (e.g. after enough real
`ai_outcome_feedback` has accumulated and the generator/training scripts
are extended to blend it in). Then call
`POST /admin/reload-models` (with the `X-Internal-Api-Key` header) to hot
swap the new artifacts into the running process without a restart.

## Security

Set `AI_INTERNAL_API_KEY` to a shared secret and configure the same value
as `AI_INTERNAL_API_KEY` on the Java backend (`AiClientService`). All
prediction/feedback/admin endpoints then require the
`X-Internal-Api-Key` header, so this service is not directly exposed to
end users - only the trusted backend calls it.
