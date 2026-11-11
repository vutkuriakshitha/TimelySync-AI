# TimelySync

**AI-assisted deadline manager for students and early-career professionals.**
Upload any notice, circular or email and TimelySync finds every date, works out what each one *means* (a deadline, an event, an issue date, or just information), and turns the ones that need action into tasks. It also predicts which tasks are likely to slip.

**Live demo:** https://timelysync-frontend-hror.onrender.com
*Hosted on free tiers: the first load after inactivity can take 1 to 3 minutes while the servers wake up.*

**Wake the servers first (recommended).** Open these two links and wait until each shows a status, then open the demo:

- API: https://timelysync-api-hror.onrender.com/actuator/health (shows `{"status":"UP"}`)
- AI service: https://timelysync-ai-hror.onrender.com/health (shows `"modelsReady":true`)

If sign-up or a document upload says "Server took too long to respond", the servers were still waking up. Wait a minute and try again.

---

## Features

- **Smart document intake:** upload a PDF or image (or paste text). An LLM reads the OCR text and returns every date with its meaning, the exact sentence it came from, and a confidence score. It works on notice formats it has never seen.
- **Grounded extraction:** nothing the LLM says is trusted blindly. Each item is checked against the source text (see [How document understanding works](#how-document-understanding-works)).
- **Task suggestions:** only actionable, future dates become tasks, and nothing is created without review. Issue dates, announcements and past dates never do.
- **Failure-risk and impact prediction:** machine-learning models estimate how likely a task is to be missed and how costly a miss would be.
- **Post-deadline analysis:** when something finishes late, the app suggests a likely root cause.
- **Planning views:** dashboard, academic planner, opportunities, personal goals, events, today snapshot and accountability tracking.
- **Accounts:** register, login and password reset with JWT authentication.

## Architecture

```
React UI ──► Spring Boot API ──► MongoDB Atlas
                  │
                  └──► FastAPI AI service ──► LLM (Gemini or any OpenAI-compatible API)
                        ├─ OCR (PDF / image)    └─ fallback: scikit-learn models
                        └─ ML models
```

| Layer | Tech | Local port |
|-------|------|-----------|
| Frontend | React 19, React Router, Bootstrap, Recharts | 3000 |
| Backend | Java 21, Spring Boot 3.4, Spring Security (JWT), MongoDB | 8080 |
| AI service | Python, FastAPI, scikit-learn, Tesseract / pdfplumber OCR | 8010 |
| Database | MongoDB Atlas | n/a |

The three services are separate and stateless. The backend calls the AI service with a shared secret (`AI_INTERNAL_API_KEY`), so the AI service can be scaled or replaced on its own.

## How document understanding works

1. **Text extraction:** embedded PDF text, or OCR for scans and images.
2. **LLM extraction:** the text goes to an LLM, which returns structured JSON for each date: purpose, kind (`deadline`, `event`, `document_date` or `info`), the quoted evidence sentence, priority, a suggested task title and a confidence score.
3. **Validation (no per-document rules):**
   - the quoted evidence must really appear in the document,
   - the date must be a valid calendar date that is actually written in the document,
   - duplicates are merged,
   - past dates get no task,
   - items whose date is missing from the quoted sentence are flagged *Low* confidence for review.
4. **Fallback:** if the LLM is off, rate limited or unreachable, or nothing survives validation, the service uses the built-in classic pipeline (TF-IDF with logistic regression plus `dateparser`) so an upload never fails.

Example: for a circular that says *"workshop on 20 November… register on or before 17 November"*, the output is the issue date (no task), a registration deadline on 17 Nov (task) and the workshop on 20 Nov (task).

## Quick start (local)

Prerequisites: Node.js 18+, Java 21, Python 3.10+, a MongoDB Atlas URI, and optionally [Tesseract](https://github.com/tesseract-ocr/tesseract) and Poppler for scanned PDFs.

**1. AI service** (`ai-service`)
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
uvicorn app.main:app --reload --port 8010
```
Set `AI_INTERNAL_API_KEY` (any long random string), and optionally `LLM_PROVIDER`, `LLM_API_KEY` and `LLM_MODEL`. Check `http://localhost:8010/health`.

**2. Backend** (`timelysync-backend/timelysync-backend`)
```bash
cp .env.example .env
./mvnw spring-boot:run           # Windows: .\mvnw.cmd spring-boot:run
```
Set `MONGODB_URI`, `JWT_SECRET` (32+ characters) and the same `AI_INTERNAL_API_KEY`. For local use, also set `MAIL_ENABLED=false` and `ALLOW_IN_APP_RESET_FALLBACK=true`. Health check: `http://localhost:8080/actuator/health`.

**3. Frontend** (`timelysyncc-frontend`)
```bash
cp .env.example .env
npm install
npm start
```
Open http://localhost:3000.

## Configuration

| Variable | Service | Purpose |
|----------|---------|---------|
| `MONGODB_URI` | backend | MongoDB connection string |
| `JWT_SECRET` | backend | signs login tokens |
| `AI_INTERNAL_API_KEY` | backend and AI | shared secret between the two services |
| `AI_SERVICE_URL` | backend | where the AI service runs |
| `LLM_PROVIDER` | AI | `gemini`, or `openai` (works with Groq and other OpenAI-compatible APIs) |
| `LLM_API_KEY`, `LLM_MODEL` | AI | provider key and model name. Model names get retired, so check your provider's current list |
| `REACT_APP_API_URL` | frontend | backend API base URL, set at build time |

Without `LLM_API_KEY`, the AI service runs on the classic ML pipeline only. Never commit `.env` files.

## Tests and evaluation

```bash
cd ai-service
python -m unittest tests.test_llm_extractor    # LLM layer with a fake model, no network needed
python -m eval.run_eval                        # date recall, precision, kind accuracy and false tasks
python -m eval.run_eval --classic              # same measures for the classic pipeline
```
`eval/documents.json` holds a small set of varied, hand-labelled notices. It is a smoke test, not a benchmark: add your own real documents to measure how it handles unseen formats.

## Deployment

Free-tier setup: **MongoDB Atlas** (database) and **Render** (AI service, API and frontend). The `render.yaml` Blueprint creates all three Render services. Step-by-step instructions are in [DEPLOY.md](./DEPLOY.md).

## Limitations

- **Free-tier hosting sleeps** after about 15 minutes idle, so the first request can be slow.
- **LLM free quotas are limited.** When they run out, the app falls back to the classic pipeline, which is less accurate on unfamiliar formats.
- **The classic models were trained on synthetic data.** Their reported accuracy comes from the same synthetic distribution and should not be read as real-world accuracy.
- **Document text is sent to the configured LLM provider.** Don't upload sensitive documents to a public demo.
- Tasks store a due date only, so event times (for example 11:00 AM) go in the description.
- OCR supports PDF, PNG, JPG, WEBP and TIFF, not Word `.docx` files.

## Author

**Vutkuri Akshitha** · [GitHub](https://github.com/vutkuriakshitha)
