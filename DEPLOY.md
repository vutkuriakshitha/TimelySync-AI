# Deploy TimelySync — all 3 free

**Stack (no Oracle needed)**

| Piece | Host | URL pattern |
|-------|------|-------------|
| Frontend | [Vercel](https://vercel.com) free | `https://….vercel.app` |
| API | [Render](https://dashboard.render.com) free | `https://timelysync-api.onrender.com` |
| AI | Render free | `https://timelysync-ai.onrender.com` |
| DB | MongoDB Atlas free | your existing cluster |

> Free Render services **sleep after ~15 min idle**. First open can take 1–2 minutes. Wake AI before Smart Intake: open `https://timelysync-ai.onrender.com/health`.

---

## A) Render — API + AI (keep / fix existing)

You already have `timelysync-api` and `timelysync-ai` from `render.yaml`.

1. Open [Render Dashboard](https://dashboard.render.com)
2. Confirm both services exist and are **not suspended**
3. On **each** service, set env:

### `timelysync-ai`
- `MONGODB_URI` = your Atlas URI (include `/timelysync`)
- `AI_INTERNAL_API_KEY` = long random shared secret (same as API)
- `CORS_ALLOWED_ORIGINS` = `https://YOUR_APP.vercel.app,https://timelysync-api.onrender.com`
- `LOG_LEVEL` = `INFO`

### `timelysync-api`
- `MONGODB_URI` = same Atlas URI
- `JWT_SECRET` = long random (32+ chars)
- `AI_INTERNAL_API_KEY` = **same** as AI
- `AI_SERVICE_URL` = `https://timelysync-ai.onrender.com`
- `FRONTEND_URL` = `https://YOUR_APP.vercel.app` (set after Vercel deploy)
- `CORS_ALLOWED_ORIGINS` = `https://YOUR_APP.vercel.app`
- `ALLOW_IN_APP_RESET_FALLBACK` = `true`
- `MAIL_ENABLED` = `false` (unless you configure SMTP)

4. **Manual Deploy → Deploy latest commit** on AI, then API
5. Wait until both show **Live**
6. Test:
   - `https://timelysync-api.onrender.com/actuator/health`
   - `https://timelysync-ai.onrender.com/health`

Atlas → **Network Access**: allow `0.0.0.0/0` (or Render outbound IPs if you prefer).

You can **suspend/delete** the old `timelysync-frontend` on Render — Vercel replaces it.

---

## B) Vercel — Frontend

1. Go to https://vercel.com → sign in with GitHub  
2. **Add New Project** → import `vutkuriakshitha/TimelySync-AI`  
3. Settings:
   - **Root Directory:** `timelysyncc-frontend`  
   - **Framework Preset:** Create React App  
   - **Build Command:** `npm run build`  
   - **Output Directory:** `build`  
4. **Environment Variables:**
   - Name: `REACT_APP_API_URL`  
   - Value: `https://timelysync-api.onrender.com/api`  
5. Deploy  
6. Copy the production URL, e.g. `https://timelysync-ai-xxxx.vercel.app`

### Wire CORS to Vercel

Back in Render → `timelysync-api` (and AI) → update:

```text
FRONTEND_URL=https://YOUR_REAL_VERCEL_URL
CORS_ALLOWED_ORIGINS=https://YOUR_REAL_VERCEL_URL
```

(AI CORS can include the Vercel URL + API URL.)

Redeploy API (and AI if you changed its CORS).

---

## C) Use the app

1. Open your **Vercel** URL (fast)  
2. Sign up / log in  
3. Before Smart Intake / OCR, wake AI once:  
   `https://timelysync-ai.onrender.com/health`  
4. Then use Smart Intake in the app  

Users appear in Atlas DB **`timelysync`** → collection **`users`**.

---

## Cold-start cheat sheet

| Service | Sleeps? | Wake |
|---------|---------|------|
| Vercel frontend | No | — |
| Render API | Yes | Open site / hit `/actuator/health` |
| Render AI | Yes | Hit `/health` before OCR |

---

## Optional: still keep Oracle path

See `deploy/oracle/` + `docker-compose.yml` if you get Always Free later (always-on API+AI).
