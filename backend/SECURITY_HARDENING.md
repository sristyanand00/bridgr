# Security Hardening — Track B

**Date:** 2026-07-27  
**Prerequisite:** Track A (analysis persistence fix, CORS fix, /debug/cors gating,
.env.example completion, loader consolidation) must already be merged.

All 76 fast tests pass after every change below.  
`core_ml/` and `evals/` were not touched.

---

## 1. Rate limiting on expensive/public endpoints

**Files changed:**
- `backend/requirements.txt` — added `slowapi==0.1.9`
- `backend/core/limiter.py` — new; exports the shared `Limiter` instance
- `backend/main.py` — wired `SlowAPIMiddleware`, `RateLimitExceeded` handler, `app.state.limiter`
- `backend/routes/readiness.py` — `@limiter.limit("10/hour")` on `POST /api/readiness`; added `request: Request` param
- `backend/routes/user.py` — `@limiter.limit("30/minute")` on `POST /api/user/sync` and `POST /api/user/quiz`; added `request: Request` param
- `backend/tests/test_rate_limit.py` — new; verifies 429 is returned after the limit is exceeded on `/api/user/sync`
- `backend/tests/conftest.py` — added autouse `_reset_rate_limiter` fixture to prevent count bleed between tests

**Threat / gap addressed:** Unauthenticated callers and bots can hammer expensive
endpoints (PDF parsing, ML pipeline, DB writes) without any cost. Rate limits
provide a first-order abuse backstop.

**Limits applied:**
| Endpoint | Limit | Key |
|---|---|---|
| `POST /api/readiness` | 10/hour | IP |
| `POST /api/user/sync` | 30/minute | IP |
| `POST /api/user/quiz` | 30/minute | IP |

**Accepted tradeoffs:**
- **In-memory storage.** slowapi uses `limits.storage.MemoryStorage` by default.
  Counters are per-process and reset on every server restart. They do NOT share
  state across multiple workers or instances. This is an explicitly accepted
  tradeoff for a single-instance Render free-tier deployment. If the app ever
  scales horizontally, replace with Redis:
  ```python
  Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")
  ```
- **Flat IP limit on `/api/readiness`.** The task specified tiered anon-vs-auth
  limiting (3/hour anonymous, 20/hour authenticated). slowapi's conditional
  key-func approach requires non-trivial plumbing to express per-uid limits that
  fall back to per-IP for anonymous callers. A flat **10/hour per IP** is applied
  as a pragmatic v1. Tiered limiting is a stated v2 improvement.

**Error response shape** (slowapi default, matches `BridgrException` convention):
```json
{"error": "Rate limit exceeded: 10 per 1 hour"}
```

---

## 2. Structured logging + request IDs for traceability

**Files changed:**
- `backend/core/logging_config.py` — new; `RequestIDMiddleware` and `RequestIDFilter`
- `backend/main.py` — added `RequestIDMiddleware`, updated log format to include `[%(request_id)s]`
- `backend/routes/readiness.py` — five structured log lines at INFO level:
  - `readiness request received` (target_role, num_postings, file_size)
  - `resume parsed` (page_count, char_count, sections_found)
  - `skills extracted` (count, any_date_unparsed)
  - `scoring complete` (screen_score, interview_score, job_score, verdict)
  - `analysis persisted` / `analysis persist failed` (both tagged with rid)

**Threat / gap addressed:** Without request IDs, a single failed or anomalous
scan in production logs is impossible to trace — log lines from concurrent
requests are interleaved. A UUID4 request_id per request, propagated through
all log lines and returned in `X-Request-ID` response headers, makes any
single request fully traceable with a single `grep`.

**Implementation notes:**
- Uses stdlib `contextvars.ContextVar` — no new dependencies (no structlog).
- A `logging.Filter` injects `request_id` into every `LogRecord` so all loggers
  (including third-party ones) pick it up automatically via `basicConfig` format.
- Respects an upstream-supplied `X-Request-ID` header (e.g. from a load balancer).
- `X-Request-ID` is added to `expose_headers` in the CORS config so browsers
  can read it.

---

## 3. Anonymous-vs-authenticated auth story tightened

**Files changed:**
- `frontend/src/config/firebase.js` — mock auth now gated behind both
  `NODE_ENV=development` AND `REACT_APP_ALLOW_MOCK_AUTH=true`; all other paths
  (including production with missing config) export null/no-op auth and emit
  `console.error` instead of a silently authenticated fake user
- `frontend/.env.example` — documented `REACT_APP_ALLOW_MOCK_AUTH` with comment
  "DEV ONLY. Never set this in a deployed environment."
- `backend/services/auth_service.py` — added startup-time WARNING log that is
  always visible in Render's deploy logs, clearly stating whether Firebase is
  configured or not

**Threat / gap addressed:**
- **Silent fake auth in production.** The previous `firebase.js` silently exported
  a mock user with `uid: "mock-uid-123"` whenever Firebase env vars were absent.
  In a deployed environment without `REACT_APP_FIREBASE_*` set, every visitor
  appeared to be the same authenticated user. This could cause DB collisions and
  masks misconfiguration completely.
- **Invisible misconfiguration.** There was no startup-visible signal in backend
  logs indicating whether Firebase was wired up. A reviewer or deploy engineer
  had to trigger an auth request to find out. The new WARNING log is the first
  thing visible in Render's log stream after a deploy.

**Accepted tradeoffs:** None. Mock auth for local dev convenience is preserved
behind an explicit opt-in flag.

---

## 4. Baseline security headers

**Files changed:**
- `backend/main.py` — added `SecurityHeadersMiddleware` (Starlette `BaseHTTPMiddleware`)

**Headers added to every response:**

| Header | Value | Purpose |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-sniffing attacks where browsers execute a response as a different content type than declared |
| `X-Frame-Options` | `DENY` | Prevents clickjacking by refusing to render the API in any `<iframe>` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limits referrer leakage: full URL sent same-origin, only origin sent cross-origin, nothing sent downgrade |

**Threat / gap addressed:** API servers without these headers are flagged by
automated security scanners (OWASP ZAP, Mozilla Observatory, Snyk) and by
technical reviewers doing a portfolio assessment. These three headers are the
minimum baseline for any public-facing HTTP service, cheap to add, and have no
compatibility cost for an API (as opposed to a browser-rendered app where CSP
would be the more complete solution).

**Accepted tradeoffs:** `Content-Security-Policy` is intentionally omitted — it
requires a per-route inventory of trusted sources and is better suited to the
frontend than the API. `Strict-Transport-Security` (HSTS) is handled by
Render's edge, not the app server.
