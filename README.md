# TimelySync

AI-assisted personal time management for students and early-career professionals.

TimelySync helps you plan work across academics, opportunities, and personal goals — then flags tasks that are likely to slip before the deadline hits.

**Live deploy:** see [`DEPLOY.md`](./DEPLOY.md) (Vercel frontend + Oracle Always Free API/AI)  
**Legacy Render:** `render.yaml` (free tier sleeps — not recommended for daily use)  
**Repo:** https://github.com/vutkuriakshitha/TimelySync-AI

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

| Layer | Tech | Local port | Render service |
|-------|------|------------|----------------|
| Frontend | React 19, Bootstrap, Recharts | `3000` | `timelysync-frontend` |
| Backend | Java 21, Spring Boot 3.4, JWT | `8080` | `timelysync-api` |
| AI | FastAPI, scikit-learn, OCR | `8010` / `8000` | `timelysync-ai` |
| DB | MongoDB Atlas (or local) | — | Atlas URI |

```
React UI ──► Spring Boot API ──► MongoDB
                 │
                 └──► FastAPI (predictions / OCR)
```

---

## Quick start (local)

### Prerequisites

- Node.js 18+
- Java 21 + Maven
- Python 3.10+
- MongoDB (local or Atlas)
- For OCR: [Tesseract](https://github.com/tesseract-ocr/tesseract) **and** [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) (scanned PDFs)

### 1. Backend

```bash
cd timelysync-backend/timelysync-backend
cp .env.example .env
# set MONGODB_URI, JWT_SECRET, AI_INTERNAL_API_KEY
# optional: MAIL_* for real forgot-password emails
./mvnw spring-boot:run
```

### 2. AI service

```bash
cd ai-service
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env
# same AI_INTERNAL_API_KEY as backend

python -m app.training.train_all   # skip if models/ already has .joblib files
uvicorn app.main:app --reload --port 8010
```

### 3. Frontend

```bash
cd timelysyncc-frontend
cp .env.example .env
npm install
npm start
```

Open http://localhost:3000

---

## Auth & email

- Register / login / reset-password work end-to-end
- Forgot-password **tries SMTP first**
- If SMTP fails (or `MAIL_ENABLED=false`), an in-app reset link is returned when `ALLOW_IN_APP_RESET_FALLBACK=true` (default for demos)
- For real inbox delivery: set Gmail App Password **or** Brevo SMTP in `.env` / Render secrets, then set `ALLOW_IN_APP_RESET_FALLBACK=false`

---

## OCR notes

- Supported: **PDF, PNG, JPG, WEBP, TIFF** (not Word `.docx`)
- Text PDFs work with pdfplumber alone
- Scanned PDFs need Poppler + Tesseract
- On Render free tier, wake AI first: `GET https://timelysync-ai.onrender.com/health` before uploading a document

---

## Deploy

Preferred free long-term setup (no sleep):

1. **MongoDB Atlas** — keep your existing cluster  
2. **Oracle Cloud Always Free** — run API + AI with `docker compose`  
3. **Vercel** — host the React frontend  

Full steps: **[DEPLOY.md](./DEPLOY.md)**

`render.yaml` remains for the old Render free stack (services sleep after idle).

---

## Security

- JWT on the API
- Shared `AI_INTERNAL_API_KEY` between backend and AI
- Never commit real `.env` / Atlas / SMTP secrets

---

## Author

**Vutkuri Akshitha**
