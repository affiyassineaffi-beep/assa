# SSAS — Tunisian Academic Management & Social Platform

## Stack
- **Backend**: Python 3.11, Flask, Flask-SocketIO (threading mode), SQLAlchemy + SQLite (`data/academic_platform.db`)
- **Frontend**: Jinja2 templates, vanilla JS, TomSelect for searchable dropdowns, Lucide SVG icons
- **AI**: Google Gemini (via `google.generativeai`) for AI theme generation
- **Storage**: Cloudinary (optional) for avatars via `storage_manager.py`
- **Auth**: Email/password + Google OAuth (`oauthlib`)

## Key Files
| File | Purpose |
|------|---------|
| `main.py` | All Flask routes, API endpoints, AI theme engine, school/location data |
| `models.py` | SQLAlchemy models — `Student`, `Grade`, `Message`, `Track`, `Group`, etc. |
| `data/tunisia_geodata.py` | **Single source of truth** for all Tunisia location data (24 governorates → delegations → lycées) |
| `translations.py` | i18n strings + `LANGUAGES` dict (fr/ar/en/de/es/it + 20 more) |
| `subjects.py` | Tunisian curriculum subject/section/coefficient data |
| `storage_manager.py` | Cloudinary upload helper |
| `templates/` | Jinja2 HTML templates |
| `static/styles.css` | All CSS — glassmorphism, neon glow, glass-pills, neon scrollbar |

## Location Data Structure (`data/tunisia_geodata.py`)
```
GEODATA = { governorate: [delegation, ...], ... }       # 24 governorates, 264 delegations
LYCEES_BY_DELEGATION = { delegation: [school, ...] }    # 200+ lycées mapped by delegation
ALL_GOVERNORATES, ALL_DELEGATIONS, ALL_SECONDARY_SCHOOLS # pre-computed lists
delegations_for_governorate(gov) → list[str]
schools_for_delegation(delegation, level="") → list[str]
```

## API Endpoints
| Endpoint | Description |
|----------|-------------|
| `GET /api/delegations?gov=X` | Returns all delegations for governorate X |
| `GET /api/schools?delegation=X&level=Y` | Returns schools for a delegation (and optional level) |
| `GET /api/grades?level=X` | Returns class grades for an educational level |

## Student Model Fields (relevant to location)
- `governorate` — Governorate name (e.g., "Tunis")
- `region_city` — Delegation name (e.g., "Jebel Jelloud") — cascade from governorate
- `school_name` — School name — cascade from delegation + level
- `delegation` — Legacy field (kept for backward compat / AI context)

## CSS Design System
- **Variables**: `--primary`, `--surface`, `--grad`, `--muted`, `--neon-cyan`, `--neon-border`
- **Glass cards**: `backdrop-filter: blur(20px)` + `rgba(16,16,24,.55)` background
- **Glass pills**: `.glass-pill` radio buttons for gender/language selection
- **Neon scrollbar**: 5px wide, cyan `rgba(56,189,248,.45)` thumb with glow, transparent track
- **Neon hover glow**: All list items get cyan `box-shadow` + `scale(1.018)` on hover
- **Bottom nav**: Active tab gets cyan icon + faint background pill

## Registration Form Cascade
```
Educational Level → Class Grades (via GRADES_BY_LEVEL)
Governorate (reg-governorate) → Delegations (reg-delegation) via /api/delegations
Delegation (reg-delegation) → Schools (reg-school) via /api/schools
```

## Settings
- **AI Theme section**: Gender (glass pills), aesthetic interest, photo upload
- **Appearance section**: Theme (dark/light/system), Language (glass pills: fr/ar/en/de/es/it)
- **Profile section**: Level, Governorate → Delegation cascade, School cascade, Class
- **Danger zone**: Account deletion

## Missing Secrets (optional features)
- `GEMINI_API_KEY` — AI theme generation
- `CLOUDINARY_*` (3 vars) — Avatar image hosting
- `GOOGLE_OAUTH_CLIENT_ID/SECRET` — Google login
- `SMTP_*` (3 vars) — Email verification
- `ADMIN_EMAIL` — Admin notifications

## Chat-First Pivot (Apr 2026)
SSAS now leads with messaging instead of grades:
- **Intro splash** (`templates/_intro_splash.html`) renders the real `static/img/app_icon.png` speech-bubble logo (matches launcher); halo + wordmark use the warm Instagram gradient (amber → pink → purple → blue).
- **Navbar brand** emoji is 💬 (was 📚).
- **Bottom nav center button** is now Messages with an Instagram-style gradient pill + paper-plane icon. Sami AI moved off-center.
- **Dashboard** (`templates/dashboard.html`) shows a "Discussions" preview card above grades, fed by `recent_chats = _conversations_for(student)[:6]` in the `dashboard` route.
- New CSS block at the end of `static/styles.css` (`CHAT-FIRST PIVOT`) styles `.chat-strip-*` and overrides `.bn-center-icon` gradient.
