# Deploying Bridgr for demos

A public link you can send to companies. Free, no credit card, no expiry.
Backend on Render, frontend on Vercel.

## Live

| | URL |
|---|---|
| **Share this one** | https://bridgr-satyam-projects.vercel.app |
| Backend API | https://bridgr-api-j9ca.onrender.com |

Share the alias above, not a `bridgr-<hash>-satyam-projects.vercel.app` URL.
The alias always points at the current production deployment; the hashed ones
are frozen to a single build and will still serve an old bundle after a
redeploy.

Two settings that are easy to lose and break the demo silently:

- **Deployment Protection must stay Disabled** (Vercel → Settings → Deployment
  Protection). It defaults to on for new projects and puts a Vercel login wall
  in front of the site — visitors get an SSO redirect instead of the app.
- **`REACT_APP_API_URL` changes need a redeploy**, not just a save. CRA
  compiles it into the bundle at build time.

## Why this combination

Free hosting for a Python service got thin in 2026. Railway and Fly are
trial-based now, and Hugging Face moved Docker Spaces behind PRO ($9/mo) —
only Static Spaces stay free, and those cannot run Python.

Render's free tier is the remaining option that runs a real backend with no
card on file. The constraint is **512MB RAM**, which the full ML stack does not
fit: torch alone holds ~300MB resident.

So the deployed backend installs `backend/requirements-render.txt` instead of
`requirements.txt` — no torch, sentence-transformers, scikit-learn or
firebase-admin. Skill extraction runs on the spaCy PhraseMatcher and fuzzy
tiers rather than embeddings: roughly **0.59 F1 instead of 0.67** per `evals/`.
Everything else — parsing, gap analysis, scoring, roadmaps, LLM narrative —
is unchanged, and readiness scores stay correctly normalised.

`requirements.txt` remains the full set for local work and for any host with
real memory.

## What you need

| Thing | Where | Cost |
|---|---|---|
| Gemini API key | aistudio.google.com | free (Flash tier) |
| Render account | render.com | free, no card |
| Vercel account | vercel.com | free (Hobby) |

Firebase is not needed — see "Auth" below.

---

## Step 1 — Gemini key

https://aistudio.google.com → **Get API key** → **Create API key**.

The backend requests `gemini-2.0-flash`, on the permanent free tier (10 req/min,
250 req/day). Paste it only into Render's env var UI — never into a file or a
commit.

Google's free tier permits using free-tier prompts for model training, and this
app sends resume text. Demo with your own resume or a fake one. Quotas have been
cut without notice before; the deterministic scoring works with no key at all,
so the demo degrades rather than dies.

## Step 2 — Backend on Render

1. https://render.com → sign up with GitHub.
2. **New** → **Blueprint** → pick the `bridgr` repo → **Connect**.

   Render reads `render.yaml` and configures the service itself: build command,
   start command, health check, Python version.

3. It will prompt for **`GEMINI_API_KEY`** — paste the key. That is the only
   value not in the repo.
4. **Apply**. First build takes about 5 minutes.
5. Copy the service URL from the dashboard. It is usually
   `https://bridgr-api.onrender.com`, but Render appends a suffix if the name
   is taken — **use whatever the dashboard shows**, not what this file guesses.

Verify: `<your-render-url>/health` → `{"status":"ok","ready":true}`

## Step 3 — Frontend on Vercel

1. Your Vercel project already exists and is connected to this repo.
2. **Settings** → **Environment Variables**. `REACT_APP_API_URL` is already
   there — **edit it**, don't add a second one. Set it to your Render URL, no
   trailing slash.
3. **Settings** → **Build & Deployment** → **Root Directory** must be
   `frontend`. Set it if blank.
4. **Deployments** → newest → `•••` → **Redeploy**.

   The redeploy is required, not optional: CRA compiles env vars into the
   bundle at build time, so editing the value alone changes nothing.

CORS needs no setup — the backend's default `ALLOWED_ORIGIN_REGEX` matches any
`*.vercel.app` origin, preview deploys included.

## Step 4 — Smoke test

1. Open the Vercel URL.
2. Land → skip the quiz → you're in. **No login required.**
3. Upload `test_resume.pdf`, pick a target role, generate the report.

## Before you present

**Open the link and generate one report 3–4 minutes before you show anyone.**

Render's free tier sleeps after 15 minutes idle, so the first request to a cold
service waits ~30–60s for the container to start, and the first report after
that loads the skill taxonomy. Both are one-time costs. Pay them before anyone
is watching.

## Auth

The whole demo path — landing, quiz, resume upload, readiness report — works
without signing in. `POST /api/readiness` requires no token; the frontend only
prompts for auth when you try to *save* a report to history.

With no Firebase configured, that save button surfaces "Authentication is not
configured", and `/api/user/*` returns 503. Nothing crashes, but **don't click
save during a presentation.**

## Talking about this honestly

If asked about the live demo's ML: the deployed instance runs the lexical
extraction tiers, not the embedding tier, because the free host caps at 512MB.
The full cascade and its eval numbers are in `evals/` and reproduce locally
with `requirements.txt`. That is a straight infrastructure tradeoff and reads
as competent — claiming the embedding tier is running when it isn't does not.

## Restoring the full ML stack

Any host with ~1GB: deploy with `requirements.txt` and the `Dockerfile`, which
already handles `$PORT` binding and non-root filesystem permissions. The
embedding tier switches itself back on when `sentence-transformers` imports
successfully — no code change. Railway ($5/mo) also removes the cold start.
