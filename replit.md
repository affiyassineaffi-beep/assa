# SSAS — Tunisian Academic Management & Social Platform

## Stack
- **Backend**: Python 3.11, Flask, Flask-SocketIO (threading mode), SQLAlchemy + **Supabase Postgres** (via Transaction pooler, IPv4)
- **Database**: Supabase Postgres 17 (`SUPABASE_DB_URL` secret = pooler URI on `aws-1-eu-central-1.pooler.supabase.com:6543`). The legacy `data/academic_platform.db` SQLite file has been removed; the app is now Autoscale-ready (no local FS persistence).
- **Supabase client**: `supabase-py` (v2) initialized as `supabase_client` for Auth/Storage/Realtime; gated on `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` (or `SUPABASE_ANON_KEY`).
- **AI Coach (Sami) history**: persisted in the `chat_messages` table (`ChatMessage` model). Helpers: `_ai_history_load/append/clear`. Session is used only as a fast read-cache; truth lives in Postgres so it survives restarts.
- **Audit log**: `user_logs` table (`UserLog` model). `record_login(student, method)` writes IP + UA + timestamp on every successful sign-in (password / Google / email-verify). Admin sees per-user history + global recent logins.
- **Session revocation**: `Student.session_version` is bumped by `revoke_all_sessions()` on ban/unban/delete. `current_student()` re-checks `is_banned`, `is_active` and that the cookie's `session_version` matches the DB on every request — banned/deleted users are kicked instantly without a server restart.
- **Admin Dashboard** (`/admin-master`, gated by `is_admin` flag or `ADMIN_EMAIL` env): users table with search + ban + delete + grant-admin + per-user login history; live Supabase row counts (`/admin-master/db-stats`); global recent logins (`/admin-master/recent-logins`); WebSocket broadcast + global neon toggle.
- **Schema bootstrap**: `_ensure_schema()` uses `information_schema.columns` (Postgres-compatible) to add new columns idempotently; called at startup inside `app.app_context()`.
- **IMPORTANT — Supabase URL on Replit**: the *direct* connection (`db.<ref>.supabase.co:5432`) is IPv6-only and unreachable from Replit. Always use the **Transaction pooler** URI (port 6543, `aws-X-<region>.pooler.supabase.com`, user format `postgres.<ref>`).
- **Frontend**: Jinja2 templates, vanilla JS, TomSelect for searchable dropdowns, Lucide SVG icons
- **AI Coach (Sami)**: Hugging Face Inference Providers (Llama-3 via Router) — primary; Google Gemini — fallback
- **Storage**: Cloudinary (optional) for avatars via `storage_manager.py`
- **Auth**: Email/password + Google OAuth (`oauthlib`)

## Brand System (Apr 2026 Rebuild)
- **Logo**: custom inline SVG mark — hexagonal frame + neon **lemniscate (∞)** loop + central spark.
  Represents *AI · Connection · Community*. Files: `static/icon.svg`, `static/favicon.svg`.
  Inline copies: `templates/_intro_splash.html` (animated), `templates/base.html` (navbar brand).
- **Brand palette** (`static/styles.css` — *BRAND REBUILD* block at the bottom):
  - Violet `#a855f7` → Cyan `#38bdf8` → Pink `#f472b6` linear gradient
  - CSS vars: `--brand-violet`, `--brand-cyan`, `--brand-pink`, `--brand-grad`, `--brand-grad-soft`, `--brand-glow`
- **Glass-pill v2**: `gender` & `language` selectors are tri-color glass pills with neon glow,
  hard-overrides ensure they are never white boxes.
- **Settings cards / primary buttons / list hovers / bottom-nav**: all driven by the brand gradient.

## Key Files
| File | Purpose |
|------|---------|
| `main.py` | All Flask routes, API endpoints, AI engines (Gemini SSE + HF Router), school/location data |
| `models.py` | SQLAlchemy models — `Student`, `Grade`, `Message`, `Track`, `Group`, etc. |
| `data/tunisia_geodata.py` | **Single source of truth** for all Tunisia location data (24 governorates → delegations → lycées) |
| `translations.py` | i18n strings + `LANGUAGES` dict (fr/ar/en/de/es/it + 20 more) |
| `subjects.py` | Tunisian curriculum subject/section/coefficient data |
| `storage_manager.py` | Cloudinary upload helper |
| `templates/` | Jinja2 HTML templates |
| `static/styles.css` | All CSS — glassmorphism, neon glow, brand-pill, neon scrollbar |
| `static/icon.svg` / `static/favicon.svg` | Brand mark (futuristic AI/connection logo) |

## Location Data (`data/tunisia_geodata.py`)
**Coverage:** 24 governorates · 257 delegations · 212 curated lycée names ·
101 university / grande école entries (all 13 public universities + ENIT, INSAT,
ESPRIT, ENIM, ENIS, ENISO, IPEIs, ISETs, faculties of medicine/pharmacy/sciences).

```
GEODATA                  = { governorate: [delegation, ...], ... }
LYCEES_BY_DELEGATION     = { delegation: [lycée, ...] }       # 157 delegations curated
UNIVERSITIES_BY_GOVERNORATE = { governorate: [institution, ...] }   # all 24 govs
ALL_GOVERNORATES, ALL_DELEGATIONS, ALL_SECONDARY_SCHOOLS, ALL_UNIVERSITIES

delegations_for_governorate(gov) → list[str]
universities_for_governorate(gov) → list[str]
universities_for_delegation(delegation) → list[str]
schools_for_delegation(delegation, level="") → list[str]
   # Level-aware dispatcher:
   #   level=""  / "Secondary"  → lycées  (curated + Pilote + patterns, ≥6 each)
   #   level="Preparatory"      → collèges (Collège X, Collège Pilote de Gov, …)
   #   level="Primary"          → écoles primaires (École Primaire X 1, X 2, …)
   #   level="University"       → universités + grandes écoles du gouvernorat
```

## API Endpoints
| Endpoint | Description |
|----------|-------------|
| `GET /api/delegations?gov=X` | Returns all delegations for governorate X |
| `GET /api/schools?delegation=X&level=Y` | Returns expanded school list (≥ 4 options) |
| `GET /api/grades?level=X` | Returns class grades for an educational level |
| `POST /ai/hf` | Hugging Face Router chat (primary AI — IT & Sport coach in Darija) |
| `POST /ai/stream` | Gemini SSE chat (fallback) |
| `POST /ai/reset` | Clear AI conversation history |
| `GET /health` | Liveness probe (returns `{status:"ok"}`) |
| `GET /health/secrets` | Public secrets-presence checklist (presence only, never values) |

## AI Coach (Sami v3 — IT & Sport in Darija)
Implemented in `main.py` under *Hugging Face Inference Providers (Sami v3)*.
- **Endpoint**: `https://router.huggingface.co/v1/chat/completions` (OpenAI-compatible)
- **Model chain** (tried in order, override with `HF_MODEL` env var, comma-separated):
  1. `meta-llama/Llama-3.3-70B-Instruct:novita` — best quality
  2. `Qwen/Qwen2.5-72B-Instruct:nebius` — strong multilingual
  3. `meta-llama/Llama-3.1-70B-Instruct:novita`
  4. `meta-llama/Llama-3.1-8B-Instruct:novita` — last-resort fast fallback
- **Generation**: `temperature=0.65`, `top_p=0.9`, `frequency_penalty=0.6`, `presence_penalty=0.3`
  to kill the repetition that smaller models exhibit on Darija.
- **System prompt**: persona Sami — Tunisian student coach. Replies in Tunisian Darija
  written in Latin script (Arabizi: 3, 7, 9 + French loanwords). Specialties: IT
  (programmation, web, mobile, IA, cybersécurité, devops) + Sport (musculation, foot,
  fitness, cardio, nutrition). Mirrors the user's language if they write in fr/ar/en.
- **Frontend**: `templates/ai_chat.html` calls `/ai/hf` first, falls back to `/ai/stream`
  (Gemini) if HF fails. Renders the brand SVG as the AI avatar.
- **Required secret**: `HUGGINGFACE_API_TOKEN`

## Settings UI (`templates/settings.html`)
- **AI Theme section** — gender (glass pills), aesthetic interest, photo upload.
- **Appearance section** — theme (dark/light/system), language (glass pills: fr/ar/en/de/es/it).
- **Profile section** — Level, Governorate → Delegation cascade, School cascade (≥ 4 options), Class.
- **Danger zone** — Account deletion.

## Optional Secrets
- `HUGGINGFACE_API_TOKEN` — **primary AI** (Sami v3, IT & Sport coach in Darija)
- `GEMINI_API_KEY` (`_2`, `_3` for rotation) — fallback AI (used when HF fails or token missing)
- `CLOUDINARY_*` (3 vars) — Avatar image hosting
- `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` — Google login
- `SMTP_*` (3 vars) — Email verification
- `ADMIN_EMAIL` — Admin notifications

## Recent Changes (Apr 2026)
1. **Total Brand Rebuild** — replaced PNG launcher icon with custom inline SVG (hex frame + ∞ loop + spark).
   New brand palette propagates to navbar, settings, glass pills, primary buttons, list hovers, AI avatar.
2. **Tunisia school data fix** — `schools_for_delegation()` now returns 4-6 candidates per delegation
   (curated + Pilote + name-pattern variants) instead of zero or one.
3. **Glass-pill v2** — gender & language selectors are guaranteed tri-color brand glass with neon glow,
   no longer fall back to white boxes in any theme.
4. **Sami v3** — AI coach migrated from legacy `api-inference.huggingface.co` to the modern
   Hugging Face Router (OpenAI-compatible). Persona retargeted to IT + Sport advice in Tunisian Darija.
