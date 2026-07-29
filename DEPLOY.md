# Deploy TimelySync (free long-term)

**Stack**
- Frontend → [Vercel](https://vercel.com) (free, no sleep)
- API + AI → [Oracle Cloud Always Free](https://www.oracle.com/cloud/free/) Ampere VM + Docker Compose
- Database → MongoDB Atlas (keep what you already have)

---

## 1) Oracle Cloud VM

1. Sign up: https://www.oracle.com/cloud/free/
2. Create **Compute → Instance**
   - Image: **Ubuntu 22.04**
   - Shape: **VM.Standard.A1.Flex** (Ampere, Always Free)
   - OCPUs: 2–4, Memory: 12–24 GB (within Always Free quota)
   - Add SSH key; note the **public IP**
3. **Networking → Subnet → Security List** ingress rules:
   - TCP **22** (SSH)
   - TCP **8080** (API) from `0.0.0.0/0`
   - (Later) TCP **80/443** if you add Caddy + a domain

### Install Docker on the VM

```bash
ssh ubuntu@YOUR_PUBLIC_IP

sudo apt-get update
sudo apt-get install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
# log out and back in so docker works without sudo
```

### Run API + AI

```bash
git clone https://github.com/vutkuriakshitha/TimelySync-AI.git
cd TimelySync-AI
cp deploy/oracle/.env.example .env
nano .env   # set MONGODB_URI, JWT_SECRET, AI_INTERNAL_API_KEY, FRONTEND_URL, CORS

docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8080/actuator/health
```

Public API base (until you add a domain):

`http://YOUR_PUBLIC_IP:8080/api`

Atlas Network Access: allow the VM public IP (or `0.0.0.0/0` for demos).

---

## 2) Frontend on Vercel

1. https://vercel.com → **Add New Project** → import `TimelySync-AI`
2. Root Directory: `timelysyncc-frontend`
3. Framework: Create React App (or Other)
4. Build Command: `npm run build`
5. Output Directory: `build`
6. Environment variable:
   - `REACT_APP_API_URL` = `http://YOUR_PUBLIC_IP:8080/api`  
     (or `https://api.yourdomain.com/api` after HTTPS)
7. Deploy → copy the `*.vercel.app` URL

### Point API CORS at Vercel

On the VM, edit `.env`:

```env
FRONTEND_URL=https://YOUR_APP.vercel.app
CORS_ALLOWED_ORIGINS=https://YOUR_APP.vercel.app
```

```bash
docker compose up -d --force-recreate api
```

---

## 3) Smoke test

1. Open `https://YOUR_APP.vercel.app`
2. Sign up / log in
3. Create a task
4. Smart Intake: wake is not needed (AI stays up on the VM)

Check users in **Atlas** (same cluster as `MONGODB_URI`), DB **`timelysync`**, collection **`users`**.

---

## Optional HTTPS (domain)

1. Point `api.yourdomain.com` A record → VM IP
2. Edit `deploy/oracle/Caddyfile` with your domain
3. Uncomment the `caddy` service in `docker-compose.yml`
4. `docker compose up -d`
5. Set Vercel `REACT_APP_API_URL=https://api.yourdomain.com/api` and redeploy frontend
6. Update `FRONTEND_URL` / `CORS_ALLOWED_ORIGINS`, recreate API

---

## Useful commands

```bash
docker compose logs -f api
docker compose logs -f ai
docker compose pull   # after git pull + rebuild
git pull && docker compose up -d --build
```

---

## Cost

Oracle Always Free Ampere + Atlas free + Vercel free ≈ **$0 / month** if you stay in Always Free limits.
