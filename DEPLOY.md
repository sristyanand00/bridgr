# Deploying Bridgr for demos

Target: a public link you can send to companies. Backend on Railway, frontend on
Vercel. Total hands-on time ~20 minutes, most of it waiting on the first build.

## What you need before starting

| Thing | Where | Cost |
|---|---|---|
| One new Google account | mail.google.com | free |
| Gemini API key | aistudio.google.com | free (Flash tier) |
| Railway account | railway.com | $5 trial credit, then $5/mo |
| Vercel account | vercel.com | free (Hobby) |

Sign up for Railway and Vercel **with the new Gmail**. Both let you register by
email and connect GitHub separately, so the account email and the GitHub
identity that owns the code do not have to match.

Firebase is **not** needed. See "Auth" below.

---

## Step 1 — Gemini key

1. Sign in to https://aistudio.google.com with the new Google account.
2. **Get API key** → **Create API key** → copy it.

The backend asks for `gemini-2.0-flash`, which is on the permanent free tier
(10 req/min, 250 req/day). Far more than a demo needs.

Two things to know: Google's free tier permits using your prompts for model
training, and this app sends resume text. Demo with your own resume or a fake
one, not a real third party's. Google has also cut free quotas without notice
before — the deterministic ML scoring works with no key at all, so the demo
degrades rather than dies.

## Step 2 — Backend on Railway

1. https://railway.com → sign up with the new Gmail.
2. **New Project** → **Deploy from GitHub repo** → authorize GitHub, granting
   access to `sristyanand00/bridgr` only.
3. Pick the repo. Leave **Root Directory** blank — the `Dockerfile` is at the
   repo root and Railway auto-detects it.
4. **Variables** → add:

   ```
   GEMINI_API_KEY = <paste your key>
   DEBUG          = false
   ENVIRONMENT    = production
   ```

   Do not set `PORT`; Railway injects it and the container reads it.
   Do not set `DATABASE_URL`; without it the app uses a local SQLite file,
   which is all a demo needs.

5. **Settings** → **Networking** → **Generate Domain**. Copy the
   `*.up.railway.app` URL.

**The first build takes 8–12 minutes** and produces a ~3GB image — it installs
torch, spaCy, and bakes in the `all-MiniLM-L6-v2` weights. Later builds are
faster because the pip layer caches. Don't panic at the wait.

Verify: open `https://<your-railway-url>/health` → `{"status":"ok","ready":true}`

## Step 3 — Frontend on Vercel

1. https://vercel.com → sign up with the new Gmail → connect the same GitHub.
2. **Add New** → **Project** → import `bridgr`.
3. Set **Root Directory** to `frontend`. Vercel reads `frontend/vercel.json`
   for the rest.
4. **Environment Variables** → add:

   ```
   REACT_APP_API_URL = https://<your-railway-url>
   ```

   No trailing slash. This is baked in at build time, so if you change it later
   you must redeploy, not just restart.

5. **Deploy**. Takes about a minute.

CORS needs no configuration: the backend's default `ALLOWED_ORIGIN_REGEX`
already matches any `*.vercel.app` origin.

## Step 4 — Smoke test

1. Open the Vercel URL.
2. Land → take or skip the quiz → you're in the app. **No login required.**
3. Upload `test_resume.pdf` from the repo root, pick a target role, generate the
   report.
4. The first report is slow (~20–40s) — the ML core loads on first use. Every
   report after that is fast.

## Before you present

- **Open the link 2–3 minutes early** and generate one report. That warms the
  ML core so the live demo is fast.
- Railway does not sleep, so the container stays warm between sessions as long
  as you have credit.
- Watch your Railway credit. ~700MB–1GB resident at roughly $10/GB-month means
  the $5 trial covers about 2–3 weeks of uptime. Railway's **App Sleeping**
  setting stretches that much further at the cost of a cold start.

## Auth

The whole demo path — landing, quiz, resume upload, readiness report — works
without signing in. `POST /api/readiness` requires no token, and the frontend
only prompts for auth when you try to *save* a report to history.

Because no Firebase keys are set, that save button will surface
"Authentication is not configured". Nothing crashes, but **don't click save
during a presentation.** If you later want history working, add a Firebase
project and set `REACT_APP_FIREBASE_API_KEY`, `_AUTH_DOMAIN`, `_PROJECT_ID`
in Vercel plus the service-account JSON on Railway.

## If Railway credit runs out and you want $0 forever

Swap the backend to Hugging Face Spaces: free 2 vCPU / 16GB RAM, Docker SDK,
sleeps only after 48h idle. The `Dockerfile` already works there unchanged —
`$PORT` binding and the non-root-readable `HF_HOME` were done with that in
mind. Then repoint `REACT_APP_API_URL` at the `*.hf.space` URL and redeploy
Vercel.

Avoid Render's free tier for this backend: 512MB RAM will OOM once torch and
MiniLM load, and it cold-starts after 15 minutes idle.
