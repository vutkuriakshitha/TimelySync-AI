# TimelySync

AI-assisted personal time management for students and early-career professionals.

TimelySync helps you plan work across academics, opportunities, and personal goals — then flags tasks that are likely to slip before the deadline hits.

---

## What it does

- **Multi-context tasks** — academic work, opportunities, goals, and events in one place
- **Smart task intake** — paste a messy note; get category, priority, and due date suggestions
- **Failure risk & impact** — ML estimates of miss probability and how bad a slip would be
- **Document deadline extraction** — upload a PDF/image notice; OCR + models pull out deadlines
- **Post-deadline analysis** — when something finishes late, surface a likely root cause
- **Dashboard & accountability** — today snapshot, cognitive load cues, progress tracking

---

## Architecture

Three services, one MongoDB:

| Layer | Tech | Port |
|-------|------|------|
| Frontend | React 19, React Router, Bootstrap, Recharts | `3000` |
| Backend | Java 21, Spring Boot 3.4, Spring Security + JWT | `8080` |
| AI service | Python, FastAPI, scikit-learn, pdfplumber / Tesseract | `8000` |
| Database | MongoDB Atlas (or local MongoDB) | — |

```
React UI ──► Spring Boot API ──► MongoDB
                 │
                 └──► FastAPI (predictions / OCR)
```

The Java backend owns auth and business logic. It calls the AI service over an internal API key. If the AI service is down, the backend falls back to conservative estimates instead of failing hard.

---

## Project layout

```
PROJECT2/
├── timelysyncc-frontend/     # React SPA
├── timelysync-backend/
│   └── timelysync-backend/   # Spring Boot app
└── ai-service/               # FastAPI + trained models
```

---

## Quick start

### Prerequisites

- Node.js 18+
- Java 21 + Maven
- Python 3.10+
- MongoDB (local or Atlas)
- Optional for OCR: [Tesseract](https://github.com/tesseract-ocr/tesseract)

### 1. Backend

```bash
cd timelysync-backend/timelysync-backend
cp .env.example .env
# edit MONGODB_URI, JWT_SECRET, AI_INTERNAL_API_KEY
./mvnw spring-boot:run
```

### 2. AI service

```bash
cd ai-service
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit MONGODB_URI + AI_INTERNAL_API_KEY (same key as backend)

python -m app.training.train_all
uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/health`

### 3. Frontend

```bash
cd timelysyncc-frontend
cp .env.example .env
npm install
npm start
```

Open [http://localhost:3000](http://localhost:3000).

---

## AI models

Trained scikit-learn pipelines (not hand-tuned if/else rules):

| Endpoint | Purpose |
|----------|---------|
| `POST /predict/failure` | Task failure-risk probability |
| `POST /predict/impact` | Deadline-miss impact severity |
| `POST /predict/postanalysis` | Root cause of a late completion |
| `POST /predict/intake` | Category + priority from free text |
| `POST /predict/deadline-extraction` | Deadlines from pasted notice text |
| `POST /predict/document-deadlines` | PDF/image → OCR → deadlines |

Models ship trained on structured synthetic data that mirrors real time-management patterns. Outcomes reported back via `POST /feedback/outcome` are stored for future retraining on real usage.

---

## Security notes

- JWT auth on the API
- Shared `AI_INTERNAL_API_KEY` between backend and AI service
- `.env` files are gitignored — copy from `.env.example` locally
- Never commit real MongoDB / JWT / SMTP credentials

---

## Tech highlights (for reviewers)

- Clean split between product API (Spring) and ML inference (FastAPI)
- Graceful AI degradation on the backend
- OCR pipeline for real-world notice documents
- Feedback loop designed for later model refresh
- Protected React routes + account/session handling

---

## Status

Local full-stack project. Backend and AI expect a reachable MongoDB URI. Train models once before first AI startup.

---

## Author

**V Akshitha**
