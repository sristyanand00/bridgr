# Deploying Bridgr for demos

Target: a public link you can send to companies, that costs nothing and stays
live indefinitely. Backend on Hugging Face Spaces, frontend on Vercel.

Hands-on time ~20 minutes, most of it waiting on the first build.

## Why this combination

The backend loads torch, spaCy, and a sentence-transformers model — around
700MB–1GB resident. That rules out most free tiers.

| Host | Cost | Verdict |
|---|---|---|
| **HF Spaces** | free, no clock | 2 vCPU / 16GB RAM. Sleeps after 48h idle. ✅ |
| Railway | $5 trial, expires in 30 days | Bills for uptime, not requests. Always warm, but ~$7–10/mo after. |
| Render free | free | 512MB RAM will OOM; sleeps after 15 min. ❌ |

Railway is worth it only if you want an always-warm link and don't mind $5/mo.
For a demo that sits idle between presentations, HF Spaces wins: you'd be
enabling Railway's sleep mode anyway, which gives up its only advantage.

## What you need

| Thing | Where | Cost |
|---|---|---|
| One new Google account | mail.google.com | free |
| Gemini API key | aistudio.google.com | free (Flash tier) |
| Hugging Face account | huggingface.co | free |
| Vercel account | vercel.com | free (Hobby) |

Firebase is **not** needed — see "Auth" below.

---

## Step 1 — Gemini key

1. Sign in to https://aistudio.google.com with the new Google account.
2. **Get API key** → **Create API key** → copy it.

The backend asks for `gemini-2.0-flash`, on the permanent free tier (10 req/min,
250 req/day). Far more than a demo needs.

Paste the key only into the host's secrets UI. Never into a file, a commit, or
a chat window. If it leaks, delete it in AI Studio and make a new one.

Two things to know: Google's free tier permits using free-tier prompts for model
training, and this app sends resume text. Demo with your own resume or a fake
one, not a real third party's. Google has also cut free quotas without notice
before — the deterministic ML scoring works with no key at all, so the demo
degrades rather than dies.

## Step 2 — Backend on Hugging Face Spaces

1. https://huggingface.co → sign up with the new Gmail.
2. **New** → **Space**. Name it `bridgr-api`. SDK: **Docker** → *Blank*.
   Hardware: **CPU basic (free)**. Visibility: **Public**.
3. **Settings** → **Variables and secrets**:

   | Type | Key | Value |
   |---|---|---|
   | Secret | `GEMINI_API_KEY` | your key |
   | Variable | `PORT` | `7860` |
   | Variable | `DEBUG` | `false` |

   Don't set `DATABASE_URL` — without it the app uses a local SQLite file,
   which is all a demo needs. It resets on restart; nothing in the demo path
   depends on it.

4. Push the code to the Space. From the repo root:

   ```bash
   git remote add hf https://huggingface.co/spaces/<your-username>/bridgr-api
   git push hf main
   ```

   Use a **write** access token as the password (Settings → Access Tokens).

5. The Space needs Docker config in its `README.md` frontmatter. Easiest route:
   edit `README.md` in the Space's web editor and put this at the very top:

   ```yaml
   ---
   title: Bridgr API
   sdk: docker
   app_port: 7860
   ---
   ```

   This must match the `PORT` variable from step 3.

**The first build takes 8–12 minutes** and produces a ~3GB image — it installs
torch, spaCy, and bakes in the `all-MiniLM-L6-v2` weights. Watch the **Logs**
tab. Later builds are faster because the pip layer caches.

Verify: `https://<your-username>-bridgr-api.hf.space/health` →
`{"status":"ok","ready":true}`

## Step 3 — Frontend on Vercel

1. https://vercel.com → sign up with the new Gmail → connect GitHub, granting
   access to `bridgr` only.
2. **Add New** → **Project** → import `bridgr`.
3. Set **Root Directory** to `frontend`. Vercel reads `frontend/vercel.json`
   for the rest.
4. **Environment Variables**:

   ```
   REACT_APP_API_URL = https://<your-username>-bridgr-api.hf.space
   ```

   No trailing slash. This is baked in at build time, so changing it later
   needs a redeploy, not just a restart.

5. **Deploy**. About a minute.

CORS needs no configuration — the backend's default `ALLOWED_ORIGIN_REGEX`
already matches any `*.vercel.app` origin.

## Step 4 — Smoke test

1. Open the Vercel URL.
2. Land → take or skip the quiz → you're in the app. **No login required.**
3. Upload `test_resume.pdf` from the repo root, pick a target role, generate.
4. The first report is slow (~20–40s) — the ML core loads on first use. Reports
   after that are fast.

## Before you present

**Open the link 3–4 minutes early and generate one report.** This matters more
than anything else here. If the Space has been idle 48h it needs to wake
(~30–60s), and then the ML core loads on the first report. Both are one-time
costs, and you want to pay them before anyone is watching, not during.

## Auth

The whole demo path — landing, quiz, resume upload, readiness report — works
without signing in. `POST /api/readiness` requires no token; the frontend only
prompts for auth when you try to *save* a report to history.

Because no Firebase keys are set, that save button surfaces "Authentication is
not configured". Nothing crashes, but **don't click save during a
presentation.** To enable history later, create a Firebase project and set
`REACT_APP_FIREBASE_API_KEY`, `_AUTH_DOMAIN`, `_PROJECT_ID` in Vercel, plus the
service-account JSON as a Space secret.

## If you later want an always-warm link

Railway, $5/mo, no sleep. Deploy from GitHub, root directory blank — the
`Dockerfile` works there unchanged, since `$PORT` binding is already handled.
Set `GEMINI_API_KEY` and `DEBUG=false`, generate a domain under Settings →
Networking, then repoint `REACT_APP_API_URL` at it and redeploy Vercel.
