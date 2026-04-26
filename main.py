"""Tunisian Academic Platform — main Flask application."""
from __future__ import annotations
import json, os
from pathlib import Path
import csv
from datetime import datetime

import requests
from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_socketio import SocketIO, emit, join_room
from oauthlib.oauth2 import WebApplicationClient
from sqlalchemy import or_, and_, text
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, Student, Grade, Message, Track, Group, GroupMember, Resource, UserFile, SystemSetting
import storage_manager as sm
from datetime import timedelta
from werkzeug.utils import secure_filename
import re, uuid, time, secrets, random

try:
    import google.generativeai as genai
    _GEMINI_AVAILABLE = True
except Exception:
    genai = None
    _GEMINI_AVAILABLE = False
from subjects import (SECTIONS, get_subjects, subject_names_fr, compute_average,
                      generate_mentor_advice, GradeEntry,
                      coefficient as get_coefficient, is_optional as get_optional)
from translations import tr, LANGUAGES, RTL_LANGS, language_label
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# ─── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-me")
_DB_PATH = Path(__file__).parent / "data" / "academic_platform.db"
_DB_PATH.parent.mkdir(exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{_DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB upload cap
# Persistent session ("Remember me") — 90-day cookie when session.permanent = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=90)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = bool(os.environ.get("REPLIT_DOMAINS"))
app.config["SESSION_COOKIE_HTTPONLY"] = True
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
SCHOOLS_DATA_PATH = Path("data/schools.csv")

import sys
sys.path.insert(0, str(Path(__file__).parent / "data"))
from tunisia_geodata import (
    GEODATA, ALL_GOVERNORATES, ALL_DELEGATIONS,
    delegations_for_governorate, LYCEES_BY_DELEGATION,
    schools_for_delegation, ALL_SECONDARY_SCHOOLS,
)

# ─── Media player config ─────────────────────────────────────────────────────
AUDIO_UPLOAD_DIR = Path(__file__).parent / "static" / "uploads" / "audio"
AUDIO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

RESOURCE_UPLOAD_DIR = Path(__file__).parent / "static" / "uploads" / "resources"
RESOURCE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESOURCE_ALLOWED = {"pdf", "doc", "docx", "ppt", "pptx", "txt", "md",
                    "png", "jpg", "jpeg", "webp", "zip"}

AVATAR_UPLOAD_DIR = Path(__file__).parent / "static" / "uploads" / "avatars"
AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
AVATAR_ALLOWED = {"png", "jpg", "jpeg", "webp", "gif"}
ALLOWED_AUDIO_EXT = {".mp3", ".m4a", ".ogg", ".wav", ".webm", ".aac"}
MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB per file
DEFAULT_PLAYLISTS = ["Study Tracks", "Relaxing Music"]

YOUTUBE_ID_RE = re.compile(
    r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/|v/))"
    r"([A-Za-z0-9_-]{11})"
)

def extract_youtube_id(url_or_id: str) -> str | None:
    s = (url_or_id or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    m = YOUTUBE_ID_RE.search(s)
    return m.group(1) if m else None

EDUCATIONAL_LEVELS = ["Primary", "Preparatory", "Secondary", "University"]

# ─── Tunisian grade lists, by educational level ──────────────────────────────
# These mirror the official Ministère de l'Éducation grade naming.
GRADES_BY_LEVEL: dict[str, list[str]] = {
    "Primary": [
        "1ère année primaire",
        "2ème année primaire",
        "3ème année primaire",
        "4ème année primaire",
        "5ème année primaire",
        "6ème année primaire",
    ],
    "Preparatory": [
        "7ème année de base",
        "8ème année de base",
        "9ème année de base",
    ],
    "Secondary": [
        "1ère année secondaire (Tronc commun)",
        # 2nd year — orientation
        "2ème année — Sciences",
        "2ème année — Lettres",
        "2ème année — Économie & Services",
        "2ème année — Technologies de l'informatique",
        "2ème année — Sciences techniques",
        "2ème année — Sport",
        # 3rd year — pre-Bac specialisations
        "3ème année — Mathématiques",
        "3ème année — Sciences expérimentales",
        "3ème année — Lettres",
        "3ème année — Économie & Gestion",
        "3ème année — Sciences techniques",
        "3ème année — Sciences de l'informatique",
        "3ème année — Sport",
        # Bac year
        "Bac Mathématiques",
        "Bac Sciences expérimentales",
        "Bac Lettres",
        "Bac Économie & Gestion",
        "Bac Sciences techniques",
        "Bac Sciences de l'informatique",
        "Bac Sport",
    ],
    "University": [
        "Licence 1",
        "Licence 2",
        "Licence 3",
        "Master 1",
        "Master 2",
        "Doctorat",
    ],
}

# Flat list — used for global validation and as the default option set.
CLASS_SECTIONS: list[str] = [g for grades in GRADES_BY_LEVEL.values() for g in grades]

SCHOOL_BADGE_COLORS = {
    "jebel jeloud": "#0f766e",
    "djebel jelloud": "#0f766e",
    "lycée": "#1e40af",
    "université": "#7c3aed",
    "primaire": "#b45309",
    "préparatoire": "#065f46",
}


# ─── School data ──────────────────────────────────────────────────────────────
def load_school_rows() -> list[dict]:
    if not SCHOOLS_DATA_PATH.exists():
        return [
            {"name": "L.JEBEL JELOUD", "location": "Tunis 1", "level": "Secondary"},
            {"name": "E.PREP. 2 MARS 34 JEBEL JLOUD", "location": "Tunis 1", "level": "Preparatory"},
            {"name": "University of Tunis", "location": "Tunis 1", "level": "University"},
        ]
    with SCHOOLS_DATA_PATH.open(newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("name") and r.get("location")]


SCHOOL_ROWS = load_school_rows()
# Merge legacy CSV schools with the new geodata schools
_csv_schools = sorted({r["name"] for r in SCHOOL_ROWS})
ALL_SCHOOLS = sorted(set(_csv_schools) | set(ALL_SECONDARY_SCHOOLS))
# ALL_REGIONS = all delegations (used for validation of existing region_city values)
ALL_REGIONS = sorted(set(ALL_DELEGATIONS) | {r["location"] for r in SCHOOL_ROWS})


def schools_for_region_level(region: str, level: str = "") -> list[str]:
    """Look up schools for a delegation+level.
    Primary source: LYCEES_BY_DELEGATION (geodata).
    Fallback: legacy CSV rows.
    """
    from_geo  = schools_for_delegation(region, level) if level else sorted(
        LYCEES_BY_DELEGATION.get(region, []))
    from_csv  = sorted({r["name"] for r in SCHOOL_ROWS
                        if r["location"] == region
                        and (not level or r.get("level") == level)})
    combined = sorted(set(from_geo) | set(from_csv))
    return combined if combined else sorted(LYCEES_BY_DELEGATION.get(region, []))


def school_badge_color(school_name: str) -> str:
    lower = (school_name or "").lower()
    for keyword, color in SCHOOL_BADGE_COLORS.items():
        if keyword in lower:
            return color
    return "#2557d6"


def is_djebel_school(school_name: str) -> bool:
    normalized = (school_name or "").lower().replace(".", " ").replace("-", " ")
    return any(p in normalized for p in ["djebel jelloud", "jebel jelloud", "jebel jloud", "jebel jeloud"])


# ─── Language helpers ─────────────────────────────────────────────────────────
SUPPORTED_LANGS = tuple(LANGUAGES.keys())
SUPPORTED_THEMES = ("dark", "light", "system")


def detect_browser_lang() -> str:
    """Pick the best language from the browser's Accept-Language header."""
    try:
        match = request.accept_languages.best_match(SUPPORTED_LANGS)
        if match:
            return match
        # Try the primary subtag too (e.g. "pt-BR" → "pt")
        for code, _q in request.accept_languages:
            base = code.split("-")[0].lower()
            if base in SUPPORTED_LANGS:
                return base
    except Exception:
        pass
    return "fr"


def get_lang() -> str:
    """Resolve the active language. Priority chain:
       1. explicit session override
       2. signed-in user's saved preference
       3. browser Accept-Language auto-detection (cached in session)
       4. default 'fr'
    """
    sl = session.get("lang")
    if sl in SUPPORTED_LANGS:
        return sl
    sid = session.get("student_id")
    if sid:
        st = db.session.get(Student, sid)
        if st and st.language in SUPPORTED_LANGS:
            return st.language
    detected = detect_browser_lang()
    session["lang"] = detected
    return detected


def get_theme() -> str:
    sid = session.get("student_id")
    if sid:
        st = db.session.get(Student, sid)
        if st and st.theme in SUPPORTED_THEMES:
            return st.theme
    return session.get("theme", "dark")


def t(key: str) -> str:
    return tr(key, get_lang())


def level_display(level: str, lang: str | None = None) -> str:
    return tr(f"level_{level}", lang or get_lang()) or level


# ─── Auth helpers ─────────────────────────────────────────────────────────────
def current_student() -> Student | None:
    sid = session.get("student_id")
    if not sid:
        return None
    return db.session.get(Student, sid)


def save_session(student: Student, remember: bool = True) -> None:
    session["student_id"] = student.id
    session["username"] = student.username
    # Default = remember: 90-day persistent cookie. If remember=False, cookie expires on browser close.
    session.permanent = bool(remember)


def _smtp_configured() -> bool:
    return bool(os.environ.get("SMTP_HOST") and os.environ.get("SMTP_USER")
                and os.environ.get("SMTP_PASSWORD"))


def _send_email(to_addr: str, subject: str, html_body: str,
                text_body: str | None = None) -> bool:
    """Send a real email via SMTP. Returns True on success.

    Required env vars:
      SMTP_HOST, SMTP_PORT (default 587), SMTP_USER, SMTP_PASSWORD,
      SMTP_FROM (defaults to SMTP_USER), SMTP_FROM_NAME (optional),
      SMTP_USE_SSL ("1" for SMTPS / port 465).
    Returns False if SMTP is not configured — the caller MUST handle this
    case (we never log verification links to the console for security).
    """
    if not _smtp_configured():
        print("[email-error] SMTP_HOST/SMTP_USER/SMTP_PASSWORD not set — "
              "email NOT sent.", flush=True)
        return False

    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    pwd  = os.environ["SMTP_PASSWORD"]
    from_addr = os.environ.get("SMTP_FROM", user)
    from_name = os.environ.get("SMTP_FROM_NAME", "Plateforme Académique")
    use_ssl = os.environ.get("SMTP_USE_SSL", "0") == "1" or port == 465

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr((from_name, from_addr))
    msg["To"] = to_addr

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=15)
        else:
            server = smtplib.SMTP(host, port, timeout=15)
            server.ehlo()
            try:
                server.starttls()
                server.ehlo()
            except smtplib.SMTPException:
                pass
        server.login(user, pwd)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[email-error] SMTP send to {to_addr} failed: {exc}", flush=True)
        return False


def send_verification_email(student: Student) -> bool:
    """Send the activation link via real SMTP. Returns True on success."""
    if not student.email or not student.email_verify_token:
        return False
    try:
        host = request.host_url.rstrip("/")
    except RuntimeError:
        host = (os.environ.get("REPLIT_DEV_DOMAIN") or "http://localhost:5000")
        if not host.startswith("http"):
            host = "https://" + host
    link = f"{host}/verify-email/{student.email_verify_token}"
    subject = "Active ton compte — Plateforme Académique"
    html = f"""
      <div style="font-family:Cairo,system-ui,sans-serif;max-width:480px;margin:0 auto;
                  background:#0a0a0f;color:#fafafa;padding:32px;border-radius:16px">
        <h1 style="margin:0 0 12px">Bienvenue {student.username} 👋</h1>
        <p style="color:#cbd5e1;line-height:1.6">
          Clique sur le bouton ci-dessous pour activer ton compte sur la
          Plateforme Académique. Ce lien est personnel — ne le partage pas.
        </p>
        <p style="text-align:center;margin:28px 0">
          <a href="{link}"
             style="background:linear-gradient(135deg,#7c5cff,#38bdf8);color:#fff;
                    text-decoration:none;padding:14px 28px;border-radius:999px;
                    font-weight:700;display:inline-block">Activer mon compte</a>
        </p>
        <p style="color:#94a3b8;font-size:.85rem;word-break:break-all">
          Ou colle ce lien dans ton navigateur : <br>{link}
        </p>
      </div>"""
    text = f"Bienvenue {student.username}! Active ton compte : {link}"
    return _send_email(student.email, subject, html, text)


def send_password_reset_email(student: Student) -> bool:
    """Send the password-reset link via real SMTP. Returns True on success."""
    if not student.email or not student.password_reset_token:
        return False
    try:
        host = request.host_url.rstrip("/")
    except RuntimeError:
        host = (os.environ.get("REPLIT_DEV_DOMAIN") or "http://localhost:5000")
        if not host.startswith("http"):
            host = "https://" + host
    link = f"{host}/reset-password/{student.password_reset_token}"
    subject = "Réinitialisation du mot de passe — Plateforme Académique"
    html = f"""
      <div style="font-family:Cairo,system-ui,sans-serif;max-width:480px;margin:0 auto;
                  background:#0a0a0f;color:#fafafa;padding:32px;border-radius:16px">
        <h1 style="margin:0 0 12px">Salut {student.username} 👋</h1>
        <p style="color:#cbd5e1;line-height:1.6">
          Tu as demandé à réinitialiser ton mot de passe. Ce lien est
          valable 1&nbsp;heure et ne peut être utilisé qu'une seule fois.
          Si tu n'es pas à l'origine de la demande, ignore cet email.
        </p>
        <p style="text-align:center;margin:28px 0">
          <a href="{link}"
             style="background:linear-gradient(135deg,#7c5cff,#38bdf8);color:#fff;
                    text-decoration:none;padding:14px 28px;border-radius:999px;
                    font-weight:700;display:inline-block">Choisir un nouveau mot de passe</a>
        </p>
        <p style="color:#94a3b8;font-size:.85rem;word-break:break-all">
          Ou colle ce lien dans ton navigateur :<br>{link}
        </p>
      </div>"""
    text = f"Réinitialise ton mot de passe : {link}"
    return _send_email(student.email, subject, html, text)


def send_phone_otp(student: Student) -> str:
    """Generate a 6-digit OTP, store it on the student, and 'send' it via SMS.

    Replace the print() with a real Twilio/Vonage call when ready.
    """
    code = f"{random.randint(0, 999999):06d}"
    student.phone_otp = code
    student.phone_otp_expires = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()
    print("\n" + "=" * 60)
    print(f"📱  SMS OTP  →  {student.phone}")
    print(f"    Code: {code}  (valid 10 min)")
    print("=" * 60 + "\n", flush=True)
    return code


def google_is_configured() -> bool:
    return bool(os.environ.get("GOOGLE_OAUTH_CLIENT_ID") and
                os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"))


def get_google_redirect_url() -> str:
    """Build the OAuth redirect URI dynamically.

    Order of preference:
      1. The Host header of the current request (works for both the
         internal Replit preview and the external .replit.app domain).
      2. REPLIT_DOMAINS env var (comma-separated, first entry).
      3. REPLIT_DEV_DOMAIN as a final fallback.
    The scheme is always forced to HTTPS — Google OAuth rejects http.
    The path is fixed to /auth/callback so it always matches what is
    registered in Google Cloud Console.
    """
    host = None
    try:
        host = request.host
    except RuntimeError:
        host = None
    if not host:
        domains = os.environ.get("REPLIT_DOMAINS", "")
        host = (domains.split(",")[0].strip()
                or os.environ.get("REPLIT_DEV_DOMAIN", "")).strip()
    return f"https://{host}/auth/callback"


def unique_username(base: str) -> str:
    cleaned = "".join(c for c in base.lower() if c.isalnum() or c in "-_").strip("-_") or "student"
    candidate = cleaned
    i = 2
    while Student.query.filter_by(username=candidate).first():
        candidate = f"{cleaned}{i}"
        i += 1
    return candidate


def profile_is_complete(student: Student) -> bool:
    return bool(
        student and student.educational_level in EDUCATIONAL_LEVELS
        and student.class_section in CLASS_SECTIONS
        and student.profile_completed
    )


def validate_profile_form(form) -> tuple[dict | None, str | None]:
    level      = form.get("educational_level", "").strip()
    governorate = form.get("governorate", "").strip()
    region     = form.get("region_city", "").strip()   # delegation
    school     = form.get("school_name", "").strip()
    cls        = form.get("class_section", "").strip()
    section    = form.get("section", "").strip() or None

    if level not in EDUCATIONAL_LEVELS:
        return None, t("err_invalid_level")
    if cls not in GRADES_BY_LEVEL.get(level, []):
        return None, t("err_invalid_class")

    return {
        "educational_level": level,
        "governorate": governorate or None,
        "region_city": region or None,
        "school_name": school or None,
        "class_section": cls,
        "section": section,
    }, None


# ─── Template context ─────────────────────────────────────────────────────────
@app.template_filter("from_json")
def _jinja_from_json(s):
    """Parse a JSON string in templates. Returns None on failure."""
    if not s:
        return None
    try:
        return _json.loads(s)
    except Exception:
        return None


@app.context_processor
def global_context():
    student = current_student()
    unread = 0
    if student:
        unread = Message.query.filter_by(recipient_id=student.id, is_read=0).count()
    return dict(
        t=t,
        lang=get_lang(),
        theme=get_theme(),
        is_rtl=(get_lang() in RTL_LANGS),
        supported_langs=SUPPORTED_LANGS,
        LANGUAGES=LANGUAGES,
        language_label=language_label,
        supported_themes=SUPPORTED_THEMES,
        is_djebel_school=is_djebel_school,
        school_badge_color=school_badge_color,
        level_display=level_display,
        current_student=student,
        unread_count=unread,
        google_configured=google_is_configured(),
        SECTIONS=SECTIONS,
        GRADES_BY_LEVEL=GRADES_BY_LEVEL,
    )


# ─── DB init ──────────────────────────────────────────────────────────────────
def _ensure_schema():
    """Lightweight migration: create tables and add missing columns on SQLite."""
    db.create_all()
    try:
        # messages.seen_at + messages.group_id
        cols = {row[1] for row in db.session.execute(text("PRAGMA table_info(messages)"))}
        if "seen_at" not in cols:
            db.session.execute(text("ALTER TABLE messages ADD COLUMN seen_at DATETIME"))
        if "group_id" not in cols:
            db.session.execute(text("ALTER TABLE messages ADD COLUMN group_id INTEGER"))
        # students.theme + students.language
        scols = {row[1] for row in db.session.execute(text("PRAGMA table_info(students)"))}
        if "theme" not in scols:
            db.session.execute(text("ALTER TABLE students ADD COLUMN theme VARCHAR(16) DEFAULT 'dark'"))
        if "language" not in scols:
            db.session.execute(text("ALTER TABLE students ADD COLUMN language VARCHAR(8) DEFAULT 'fr'"))
        # Gamification + avatar columns
        for col, ddl in [
            ("points",      "ALTER TABLE students ADD COLUMN points INTEGER DEFAULT 0"),
            ("level",       "ALTER TABLE students ADD COLUMN level INTEGER DEFAULT 1"),
            ("experience",  "ALTER TABLE students ADD COLUMN experience INTEGER DEFAULT 0"),
            ("reputation",  "ALTER TABLE students ADD COLUMN reputation INTEGER DEFAULT 0"),
            ("badge_icon",  "ALTER TABLE students ADD COLUMN badge_icon VARCHAR(8)"),
            ("avatar_url",  "ALTER TABLE students ADD COLUMN avatar_url VARCHAR(500)"),
            ("is_active",          "ALTER TABLE students ADD COLUMN is_active INTEGER DEFAULT 0"),
            ("email_verified",     "ALTER TABLE students ADD COLUMN email_verified INTEGER DEFAULT 0"),
            ("email_verify_token", "ALTER TABLE students ADD COLUMN email_verify_token VARCHAR(80)"),
            ("phone_verified",     "ALTER TABLE students ADD COLUMN phone_verified INTEGER DEFAULT 0"),
            ("phone_otp",          "ALTER TABLE students ADD COLUMN phone_otp VARCHAR(8)"),
            ("phone_otp_expires",  "ALTER TABLE students ADD COLUMN phone_otp_expires DATETIME"),
            ("gender",             "ALTER TABLE students ADD COLUMN gender VARCHAR(16)"),
            ("custom_theme",       "ALTER TABLE students ADD COLUMN custom_theme TEXT"),
            ("password_reset_token",   "ALTER TABLE students ADD COLUMN password_reset_token VARCHAR(80)"),
            ("password_reset_expires", "ALTER TABLE students ADD COLUMN password_reset_expires DATETIME"),
            ("is_admin",               "ALTER TABLE students ADD COLUMN is_admin INTEGER DEFAULT 0"),
            ("delegation",             "ALTER TABLE students ADD COLUMN delegation VARCHAR(120)"),
            ("governorate",            "ALTER TABLE students ADD COLUMN governorate VARCHAR(120)"),
        ]:
            if col not in scols:
                db.session.execute(text(ddl))
                if col == "is_active":
                    db.session.execute(text("UPDATE students SET is_active=1"))
                elif col == "email_verified":
                    db.session.execute(text("UPDATE students SET email_verified=1"))
        db.session.commit()
    except Exception:
        db.session.rollback()


_schema_ready = False


@app.before_request
def ensure_db():
    global _schema_ready
    if not _schema_ready:
        _ensure_schema()
        _schema_ready = True


# ─── Language toggle ──────────────────────────────────────────────────────────
@app.route("/set-lang/<lang>")
def set_lang(lang: str):
    if lang in SUPPORTED_LANGS:
        session["lang"] = lang
        # Persist to user profile if logged in
        st = current_student()
        if st:
            st.language = lang
            db.session.commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/set-theme/<theme>")
def set_theme(theme: str):
    if theme in SUPPORTED_THEMES:
        session["theme"] = theme
        st = current_student()
        if st:
            st.theme = theme
            db.session.commit()
    return redirect(request.referrer or url_for("index"))


# ─── Public index ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    student = current_student()
    public_grades = (
        db.session.query(Grade, Student)
        .join(Student, Grade.student_id == Student.id)
        .filter(Grade.is_public == 1)
        .order_by(Grade.created_at.desc())
        .all()
    )
    return render_template("index.html", student=student, public_grades=public_grades)


# ─── Registration ─────────────────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    ctx = dict(educational_levels=EDUCATIONAL_LEVELS, regions=ALL_REGIONS,
               governorates=ALL_GOVERNORATES,
               all_schools=ALL_SCHOOLS, class_sections=CLASS_SECTIONS, sections=SECTIONS)
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        profile, err = validate_profile_form(request.form)

        if len(username) < 3:
            flash(t("err_username_short"), "error")
            return render_template("register.html", **ctx)
        if "@" not in email:
            flash(t("err_invalid_email"), "error")
            return render_template("register.html", **ctx)
        if len(password) < 4:
            flash(t("err_password_short"), "error")
            return render_template("register.html", **ctx)
        if err:
            flash(err, "error")
            return render_template("register.html", **ctx)

        if Student.query.filter(
                (Student.email == email) | (Student.username == username)).first():
            flash(t("err_email_taken"), "error")
            return render_template("register.html", **ctx)

        gender = (request.form.get("gender") or "").strip().lower()
        if gender not in {"female", "male", "other"}:
            gender = "other"

        # AI-generated personal theme:
        #   1) If a photo was uploaded, analyze it directly.
        #   2) Else, if an "interest" was provided, web-search inspiration
        #      images and let Gemini design a theme from them.
        #   3) Else, use the gender default.
        interest = (request.form.get("interest") or "").strip()
        delegation_for_theme = (request.form.get("delegation") or "").strip()
        theme_obj = dict(DEFAULT_THEMES.get(gender, DEFAULT_THEMES["other"]))
        photo = request.files.get("theme_photo")
        if photo and photo.filename:
            try:
                img_bytes = photo.read()
                if img_bytes:
                    mime = photo.mimetype or "image/jpeg"
                    theme_obj = generate_theme_from_image(img_bytes, mime, gender, delegation=delegation_for_theme)
            except Exception as exc:
                print(f"[theme] upload failed: {exc}", flush=True)
        elif interest:
            try:
                theme_obj = generate_theme_from_interest(interest, gender, delegation=delegation_for_theme)
            except Exception as exc:
                print(f"[theme] interest gen failed: {exc}", flush=True)

        delegation = (request.form.get("delegation") or "").strip()
        governorate = (request.form.get("governorate") or "").strip()
        student = Student(
            username=username, email=email,
            password_hash=generate_password_hash(password),
            auth_provider="password", phone=phone or None,
            profile_completed=1, **profile,
            is_active=0, email_verified=0,
            email_verify_token=secrets.token_urlsafe(32),
            gender=gender,
            delegation=delegation or None,
            governorate=governorate or None,
            custom_theme=_json.dumps(theme_obj),
        )
        db.session.add(student)
        db.session.commit()
        if not send_verification_email(student):
            # Roll back: delete the just-created account so the user can retry
            db.session.delete(student)
            db.session.commit()
            flash("Impossible d'envoyer l'email de vérification pour le moment. "
                  "Réessaie dans quelques instants ou contacte le support.",
                  "error")
            return render_template("register.html", **ctx)
        flash("Compte créé. Vérifie ton email pour activer ton compte.", "success")
        return redirect(url_for("verify_pending", email=email))

    return render_template("register.html", **ctx)


# ─── Login ────────────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember", "1") == "1"
        student = Student.query.filter(
            (Student.email == email) | (Student.username == email)).first()
        if student and student.password_hash and check_password_hash(student.password_hash, password):
            if not student.email_verified:
                flash("Ton email n'est pas encore vérifié. Vérifie ta boîte mail.", "error")
                return redirect(url_for("verify_pending", email=student.email or ""))
            save_session(student, remember=remember)
            flash(t("success_welcome"), "success")
            return redirect(url_for("dashboard"))
        flash(t("err_login_failed"), "error")
    return render_template("login.html")


# ─── Email & Phone verification ───────────────────────────────────────────────
@app.route("/verify-pending")
def verify_pending():
    email = request.args.get("email", "")
    return render_template("verify_pending.html", email=email)


@app.route("/verify-email/<token>")
def verify_email(token: str):
    student = Student.query.filter_by(email_verify_token=token).first()
    if not student:
        flash("Lien de vérification invalide ou expiré.", "error")
        return redirect(url_for("login"))
    student.email_verified = 1
    student.is_active = 1
    student.email_verify_token = None
    db.session.commit()
    save_session(student)
    flash("Email vérifié ! Bienvenue 🎉", "success")
    return redirect(url_for("dashboard"))


# ─── Password Reset (Forgot Password) ────────────────────────────────────────
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    sent = False
    email = ""
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        if email and "@" in email:
            student = Student.query.filter_by(email=email).first()
            if student:
                student.password_reset_token = secrets.token_urlsafe(32)
                student.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
                db.session.commit()
                # Best-effort send. We never reveal whether the email exists.
                try:
                    send_password_reset_email(student)
                except Exception as exc:
                    print(f"[reset] email send failed: {exc}", flush=True)
            sent = True
    return render_template("forgot_password.html", sent=sent, email=email)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    student = Student.query.filter_by(password_reset_token=token).first()
    valid = bool(student and student.password_reset_expires
                 and student.password_reset_expires > datetime.utcnow())
    if not valid:
        flash("Lien de réinitialisation invalide ou expiré.", "error")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_pw = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        if len(new_pw) < 4:
            flash(t("err_password_short"), "error")
        elif new_pw != confirm:
            flash("Les deux mots de passe ne correspondent pas.", "error")
        else:
            student.password_hash = generate_password_hash(new_pw)
            student.password_reset_token = None
            student.password_reset_expires = None
            # A successful reset implicitly verifies the email
            student.email_verified = 1
            student.is_active = 1
            db.session.commit()
            flash("Mot de passe mis à jour. Tu peux te connecter.", "success")
            return redirect(url_for("login"))
    return render_template("reset_password.html", token=token)


@app.route("/verify-email/resend", methods=["POST"])
def verify_email_resend():
    email = request.form.get("email", "").strip().lower()
    student = Student.query.filter_by(email=email).first()
    if student and not student.email_verified:
        if not student.email_verify_token:
            student.email_verify_token = secrets.token_urlsafe(32)
            db.session.commit()
        if send_verification_email(student):
            flash("Lien de vérification renvoyé.", "success")
        else:
            flash("Impossible d'envoyer l'email pour le moment. Réessaie plus tard.",
                  "error")
    else:
        flash("Aucun compte non vérifié pour cet email.", "error")
    return redirect(url_for("verify_pending", email=email))


@app.route("/verify-phone", methods=["GET", "POST"])
def verify_phone():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    if request.method == "POST":
        action = request.form.get("action", "verify")
        if action == "send":
            phone = request.form.get("phone", "").strip()
            if phone:
                student.phone = phone
                db.session.commit()
            if not student.phone:
                flash("Renseigne d'abord un numéro de téléphone.", "error")
                return redirect(url_for("verify_phone"))
            send_phone_otp(student)
            flash("Code envoyé par SMS (voir la console pour l'instant).", "success")
            return redirect(url_for("verify_phone"))
        # action == verify
        code = request.form.get("code", "").strip()
        if (student.phone_otp and student.phone_otp == code
                and student.phone_otp_expires
                and student.phone_otp_expires > datetime.utcnow()):
            student.phone_verified = 1
            student.phone_otp = None
            student.phone_otp_expires = None
            db.session.commit()
            flash("Téléphone vérifié ✅", "success")
            return redirect(url_for("dashboard"))
        flash("Code invalide ou expiré.", "error")
        return redirect(url_for("verify_phone"))
    return render_template("verify_phone.html", student=student)


# ─── Google OAuth ─────────────────────────────────────────────────────────────
@app.route("/google_login")
def google_login():
    if not google_is_configured():
        flash(t("google_needs_config"), "error")
        return redirect(url_for("login"))
    client = WebApplicationClient(os.environ["GOOGLE_OAUTH_CLIENT_ID"])
    cfg = requests.get(GOOGLE_DISCOVERY_URL, timeout=10).json()
    uri = client.prepare_request_uri(
        cfg["authorization_endpoint"],
        redirect_uri=get_google_redirect_url(),
        scope=["openid", "email", "profile"],
    )
    return redirect(uri)


@app.route("/auth/callback")
@app.route("/google_login/callback")  # legacy alias
def google_callback():
    if not google_is_configured():
        flash(t("google_needs_config"), "error")
        return redirect(url_for("login"))
    code = request.args.get("code")
    if not code:
        flash("Google did not return a code.", "error")
        return redirect(url_for("login"))
    client = WebApplicationClient(os.environ["GOOGLE_OAUTH_CLIENT_ID"])
    cfg = requests.get(GOOGLE_DISCOVERY_URL, timeout=10).json()
    token_url, headers, body = client.prepare_token_request(
        cfg["token_endpoint"],
        authorization_response=request.url.replace("http://", "https://"),
        redirect_url=get_google_redirect_url(), code=code,
    )
    token_resp = requests.post(token_url, headers=headers, data=body,
                               auth=(os.environ["GOOGLE_OAUTH_CLIENT_ID"],
                                     os.environ["GOOGLE_OAUTH_CLIENT_SECRET"]), timeout=10)
    client.parse_request_body_response(json.dumps(token_resp.json()))
    uri, headers, body = client.add_token(cfg["userinfo_endpoint"])
    info = requests.get(uri, headers=headers, data=body, timeout=10).json()
    if not info.get("email_verified"):
        flash(t("err_google_no_email"), "error")
        return redirect(url_for("login"))
    email = info["email"].lower()
    google_id = info["sub"]
    display = info.get("given_name") or info.get("name") or email.split("@")[0]
    student = Student.query.filter(
        (Student.google_id == google_id) | (Student.email == email)).first()
    picture = info.get("picture") or None
    if student:
        student.google_id = google_id
        student.auth_provider = "google"
        if picture and not student.avatar_url:
            student.avatar_url = picture
    else:
        student = Student(username=unique_username(display), email=email,
                          google_id=google_id, auth_provider="google", profile_completed=0,
                          avatar_url=picture,
                          is_active=1, email_verified=1)
        db.session.add(student)
    # Google has already verified the email, so always trust it.
    student.email_verified = 1
    student.is_active = 1
    db.session.commit()
    save_session(student)
    if not profile_is_complete(student):
        flash(t("complete_profile_prompt"), "success")
        return redirect(url_for("complete_profile"))
    flash(t("success_google"), "success")
    return redirect(url_for("dashboard"))


# ─── Profile ──────────────────────────────────────────────────────────────────
@app.route("/profile", methods=["GET", "POST"])
@app.route("/complete-profile", methods=["GET", "POST"])
def complete_profile():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    ctx = dict(student=student, educational_levels=EDUCATIONAL_LEVELS,
               regions=ALL_REGIONS, all_schools=ALL_SCHOOLS,
               class_sections=CLASS_SECTIONS, sections=SECTIONS)
    if request.method == "POST":
        profile, err = validate_profile_form(request.form)
        phone = request.form.get("phone", "").strip()
        if err:
            flash(err, "error")
        else:
            for k, v in profile.items():
                setattr(student, k, v)
            student.profile_completed = 1
            if phone:
                student.phone = phone
            db.session.commit()
            flash(t("success_profile"), "success")
            return redirect(url_for("dashboard"))
    return render_template("profile.html", **ctx)


# ─── Dashboard ────────────────────────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    if not profile_is_complete(student):
        return redirect(url_for("complete_profile"))

    grades = Grade.query.filter_by(student_id=student.id)\
                        .order_by(Grade.created_at.desc()).all()

    subjects = get_subjects(student.educational_level, student.section)

    # Build GradeEntry list for mentor/average
    entries = [
        GradeEntry(g.subject, g.note, student.educational_level, student.section)
        for g in grades
    ]
    avg_data = compute_average(entries)
    mentor_tips = generate_mentor_advice(entries, get_lang())

    # Recent direct conversations — surfaced at the top of the dashboard
    # so the experience is chat-first (Instagram-DM style), not just grades.
    recent_chats = _conversations_for(student)[:6]

    return render_template(
        "dashboard.html",
        student=student,
        grades=grades,
        subjects=subjects,
        avg_data=avg_data,
        mentor_tips=mentor_tips,
        recent_chats=recent_chats,
    )


# ─── AJAX: schools for region+level ───────────────────────────────────────────
@app.route("/api/delegations")
def api_delegations():
    """Return delegations for a given governorate."""
    gov = request.args.get("gov", "").strip()
    return jsonify(delegations_for_governorate(gov) if gov else ALL_DELEGATIONS)


@app.route("/api/schools")
def api_schools():
    region = request.args.get("region", "").strip()
    delegation = request.args.get("delegation", "").strip()
    level = request.args.get("level", "").strip()
    lookup = delegation or region
    schools = schools_for_region_level(lookup, level) if lookup else ALL_SECONDARY_SCHOOLS
    return jsonify(schools)


@app.route("/api/grades")
def api_grades():
    """Return the Tunisian grade list for a given educational level."""
    level = request.args.get("level", "")
    return jsonify(GRADES_BY_LEVEL.get(level, []))


# ─── Grades ───────────────────────────────────────────────────────────────────
@app.route("/grades", methods=["POST"])
def add_grade():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    if not profile_is_complete(student):
        return redirect(url_for("complete_profile"))

    subject = request.form.get("subject", "").strip()
    note_text = request.form.get("note", "").strip()
    is_public = 1 if request.form.get("is_public") == "on" else 0
    allowed = subject_names_fr(student.educational_level, student.section)

    if subject not in allowed:
        flash(t("err_invalid_subject"), "error")
        return redirect(url_for("dashboard"))
    try:
        note = float(note_text)
        if not (0 <= note <= 20):
            raise ValueError
    except ValueError:
        flash(t("err_invalid_note"), "error")
        return redirect(url_for("dashboard"))

    coef = get_coefficient(subject, student.educational_level, student.section)
    opt = 1 if get_optional(subject, student.educational_level, student.section) else 0

    g = Grade(student_id=student.id, subject=subject, note=note,
              coefficient=coef, is_optional=opt, is_public=is_public)
    db.session.add(g)
    db.session.commit()
    flash(t("success_grade"), "success")
    return redirect(url_for("dashboard"))


@app.route("/grades/<int:gid>/visibility", methods=["POST"])
def toggle_visibility(gid: int):
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    grade = Grade.query.filter_by(id=gid, student_id=student.id).first_or_404()
    grade.is_public = 1 if request.form.get("is_public") == "on" else 0
    db.session.commit()
    flash(t("success_visibility"), "success")
    return redirect(url_for("dashboard"))


@app.route("/grades/<int:gid>/delete", methods=["POST"])
def delete_grade(gid: int):
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    grade = Grade.query.filter_by(id=gid, student_id=student.id).first_or_404()
    db.session.delete(grade)
    db.session.commit()
    flash(t("success_deleted"), "success")
    return redirect(url_for("dashboard"))


# ─── Messages — conversation-based DM system ─────────────────────────────────
def _conversations_for(student: Student) -> list[dict]:
    """Return one entry per peer the student has talked with: peer + last msg + unread."""
    msgs = (Message.query
            .filter(Message.group_id.is_(None))
            .filter(or_(Message.sender_id == student.id,
                        Message.recipient_id == student.id))
            .order_by(Message.created_at.desc()).all())
    seen_peers: dict[int, dict] = {}
    for m in msgs:
        peer_id = m.recipient_id if m.sender_id == student.id else m.sender_id
        if peer_id in seen_peers:
            continue
        peer = db.session.get(Student, peer_id)
        if not peer:
            continue
        unread = Message.query.filter_by(
            sender_id=peer_id, recipient_id=student.id, is_read=0).count()
        seen_peers[peer_id] = {
            "peer": peer, "last": m, "unread": unread,
        }
    return list(seen_peers.values())


@app.route("/messages")
def messages():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    convs = _conversations_for(student)
    groups = _user_groups(student)
    all_students = (Student.query.filter(Student.id != student.id)
                    .order_by(Student.username).all())
    return render_template("messages.html", student=student,
                           conversations=convs, all_students=all_students,
                           groups=groups)


@app.route("/chat/<int:peer_id>")
def chat(peer_id: int):
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    if peer_id == student.id:
        return redirect(url_for("messages"))
    peer = db.session.get(Student, peer_id)
    if not peer:
        abort(404)
    thread = (Message.query
        .filter(Message.group_id.is_(None))
        .filter(or_(and_(Message.sender_id == student.id, Message.recipient_id == peer_id),
                    and_(Message.sender_id == peer_id, Message.recipient_id == student.id)))
        .order_by(Message.created_at.asc()).all())
    # Mark all incoming as read+seen
    now = datetime.utcnow()
    changed = False
    for m in thread:
        if m.recipient_id == student.id and not m.is_read:
            m.is_read = 1
            m.seen_at = now
            changed = True
    if changed:
        db.session.commit()
    return render_template("chat.html", student=student, peer=peer, thread=thread)


@app.route("/messages/send", methods=["POST"])
def send_message():
    """Legacy non-socket fallback (form post)."""
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    recipient_id = request.form.get("recipient_id", type=int)
    body = request.form.get("body", "").strip()
    if not recipient_id or not body:
        flash("Destinataire et message requis.", "error")
        return redirect(url_for("messages"))
    recipient = db.session.get(Student, recipient_id)
    if not recipient:
        flash("Destinataire introuvable.", "error")
        return redirect(url_for("messages"))
    msg = Message(sender_id=student.id, recipient_id=recipient_id, body=body)
    db.session.add(msg)
    db.session.commit()
    return redirect(url_for("chat", peer_id=recipient_id))


@app.route("/messages/poll")
def poll_messages():
    student = current_student()
    if not student:
        return jsonify({"unread": 0})
    count = Message.query.filter_by(recipient_id=student.id, is_read=0).count()
    return jsonify({"unread": count})


# ─── SocketIO real-time events ───────────────────────────────────────────────
def _user_room(uid: int) -> str:
    return f"user_{uid}"


@socketio.on("connect")
def _sio_connect():
    student = current_student()
    if not student:
        return False  # reject unauthenticated socket
    join_room(_user_room(student.id))
    emit("connected", {"user_id": student.id})


@socketio.on("send_message")
def _sio_send(data):
    student = current_student()
    if not student:
        return
    try:
        peer_id = int(data.get("peer_id"))
    except (TypeError, ValueError):
        return
    body = (data.get("body") or "").strip()
    if not body or peer_id == student.id:
        return
    peer = db.session.get(Student, peer_id)
    if not peer:
        return
    msg = Message(sender_id=student.id, recipient_id=peer_id, body=body)
    db.session.add(msg)
    db.session.commit()
    payload = msg.to_dict()
    payload["sender_username"] = student.username
    payload["sender_level"] = student.level
    payload["sender_badge"] = student.badge_icon or badge_for_level(student.level or 1)
    payload["sender_avatar"] = student.avatar_url
    payload["peer_id"] = peer_id            # so client knows which thread
    # Emit to recipient (live notification + chat update)
    emit("new_message", payload, room=_user_room(peer_id))
    # Echo back to sender (confirmed save → swaps optimistic bubble)
    emit("message_sent", payload, room=_user_room(student.id))
    # +5 XP for sending a message
    award_xp(student, 5, "message_sent")


@socketio.on("mark_seen")
def _sio_mark_seen(data):
    student = current_student()
    if not student:
        return
    try:
        peer_id = int(data.get("peer_id"))
    except (TypeError, ValueError):
        return
    now = datetime.utcnow()
    unread = Message.query.filter_by(
        sender_id=peer_id, recipient_id=student.id, is_read=0).all()
    if not unread:
        return
    ids = []
    for m in unread:
        m.is_read = 1
        m.seen_at = now
        ids.append(m.id)
    db.session.commit()
    # Tell the original sender their messages were seen
    emit("messages_seen", {
        "by_user_id": student.id,
        "message_ids": ids,
        "seen_at": now.isoformat(),
    }, room=_user_room(peer_id))


@socketio.on("typing")
def _sio_typing(data):
    student = current_student()
    if not student:
        return
    try:
        peer_id = int(data.get("peer_id"))
    except (TypeError, ValueError):
        return
    emit("peer_typing", {"from_user_id": student.id,
                         "is_typing": bool(data.get("is_typing"))},
         room=_user_room(peer_id))


# ─── Media Player ─────────────────────────────────────────────────────────────
def _user_tracks(student: Student) -> list[Track]:
    return (Track.query.filter_by(student_id=student.id)
            .order_by(Track.playlist, Track.position, Track.id).all())


@app.route("/player")
def player():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    tracks = _user_tracks(student)
    playlists = sorted({t.playlist for t in tracks} | set(DEFAULT_PLAYLISTS))
    return render_template("player.html", tracks=tracks, playlists=playlists,
                           default_playlists=DEFAULT_PLAYLISTS)


@app.route("/player/add", methods=["POST"])
def player_add():
    student = current_student()
    if not student:
        return redirect(url_for("login"))

    title = (request.form.get("title", "") or "").strip()
    playlist = (request.form.get("playlist", "") or "Study Tracks").strip() or "Study Tracks"
    kind = request.form.get("kind", "youtube")

    if kind == "youtube":
        url = (request.form.get("youtube_url", "") or "").strip()
        vid = extract_youtube_id(url)
        if not vid:
            flash("Lien YouTube invalide.", "error")
            return redirect(url_for("player"))
        track = Track(student_id=student.id,
                      title=title or f"YouTube · {vid}",
                      kind="youtube", source=vid, playlist=playlist)
    elif kind == "audio":
        f = request.files.get("audio_file")
        if not f or not f.filename:
            flash("Aucun fichier audio sélectionné.", "error")
            return redirect(url_for("player"))
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOWED_AUDIO_EXT:
            flash(f"Format non supporté ({ext}). Utilisez : "
                  + ", ".join(sorted(ALLOWED_AUDIO_EXT)), "error")
            return redirect(url_for("player"))
        safe_name = f"{student.id}_{uuid.uuid4().hex}{ext}"
        dest = AUDIO_UPLOAD_DIR / safe_name
        f.save(dest)
        rel_url = url_for("static", filename=f"uploads/audio/{safe_name}")
        track = Track(student_id=student.id,
                      title=title or secure_filename(f.filename),
                      kind="audio", source=rel_url, playlist=playlist)
    else:
        flash("Type de piste inconnu.", "error")
        return redirect(url_for("player"))

    last = (Track.query.filter_by(student_id=student.id, playlist=playlist)
            .order_by(Track.position.desc()).first())
    track.position = (last.position + 1) if last else 0
    db.session.add(track)
    db.session.commit()
    flash("Piste ajoutée.", "success")
    return redirect(url_for("player"))


@app.route("/player/<int:tid>/delete", methods=["POST"])
def player_delete(tid: int):
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    track = Track.query.filter_by(id=tid, student_id=student.id).first_or_404()
    # Best-effort cleanup of the local audio file
    if track.kind == "audio" and track.source.startswith("/static/uploads/audio/"):
        local = Path(__file__).parent / track.source.lstrip("/")
        try:
            if local.exists():
                local.unlink()
        except OSError:
            pass
    db.session.delete(track)
    db.session.commit()
    flash("Piste supprimée.", "success")
    return redirect(url_for("player"))


@app.route("/api/player/tracks")
def api_player_tracks():
    student = current_student()
    if not student:
        return jsonify([])
    return jsonify([t.to_dict() for t in _user_tracks(student)])


# ─── YouTube Search ───────────────────────────────────────────────────────────
# Two paths:
#   (1) YOUTUBE_API_KEY env var → YouTube Data API v3 (10,000 units/day free)
#   (2) Fallback: scrape youtube.com/results page (no key, lighter but fragile)
import json as _json
import urllib.parse as _urlparse
import urllib.request as _urlreq

YT_SEARCH_CACHE: dict[str, tuple[float, list]] = {}
YT_CACHE_TTL = 600  # 10 min


def _yt_search_api(query: str, max_results: int = 18) -> list[dict] | None:
    """Use YouTube Data API v3 if a key is configured. Returns None on failure."""
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not key:
        return None
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": str(max_results),
        "key": key,
        "safeSearch": "moderate",
    }
    url = "https://www.googleapis.com/youtube/v3/search?" + _urlparse.urlencode(params)
    try:
        with _urlreq.urlopen(url, timeout=8) as resp:
            data = _json.loads(resp.read().decode("utf-8"))
        out = []
        for it in data.get("items", []):
            vid = (it.get("id") or {}).get("videoId")
            sn = it.get("snippet") or {}
            if not vid:
                continue
            thumbs = sn.get("thumbnails") or {}
            thumb = ((thumbs.get("medium") or thumbs.get("high")
                      or thumbs.get("default") or {}).get("url"))
            out.append({
                "video_id": vid,
                "title": sn.get("title", ""),
                "channel": sn.get("channelTitle", ""),
                "thumbnail": thumb or f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg",
            })
        return out
    except Exception:
        return None


def _yt_search_scrape(query: str, max_results: int = 18) -> list[dict]:
    """Fallback: parse YouTube's results page HTML — no API key needed."""
    q = _urlparse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={q}&hl=en"
    req = _urlreq.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with _urlreq.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return []

    # Extract ytInitialData JSON blob
    m = re.search(r"var ytInitialData\s*=\s*(\{.*?\});</script>", html)
    if not m:
        m = re.search(r'ytInitialData"\]\s*=\s*(\{.*?\});\s*\(function', html)
    if not m:
        return []
    try:
        data = _json.loads(m.group(1))
    except Exception:
        return []

    results = []
    try:
        sections = (data["contents"]["twoColumnSearchResultsRenderer"]
                    ["primaryContents"]["sectionListRenderer"]["contents"])
        for sec in sections:
            items = (sec.get("itemSectionRenderer") or {}).get("contents", [])
            for it in items:
                v = it.get("videoRenderer")
                if not v:
                    continue
                vid = v.get("videoId")
                title_runs = (v.get("title") or {}).get("runs") or []
                title = "".join(r.get("text", "") for r in title_runs)
                channel = ""
                owner = (v.get("ownerText") or v.get("longBylineText") or {}).get("runs") or []
                if owner:
                    channel = owner[0].get("text", "")
                thumbs = ((v.get("thumbnail") or {}).get("thumbnails") or [])
                thumb = thumbs[-1]["url"] if thumbs else f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg"
                if vid and title:
                    results.append({
                        "video_id": vid,
                        "title": title,
                        "channel": channel,
                        "thumbnail": thumb,
                    })
                if len(results) >= max_results:
                    break
            if len(results) >= max_results:
                break
    except Exception:
        return results
    return results


@app.route("/api/youtube/search")
def api_youtube_search():
    student = current_student()
    if not student:
        return jsonify({"error": "auth"}), 401

    q = (request.args.get("q", "") or "").strip()
    mode = (request.args.get("mode", "music") or "music").lower()
    if not q:
        return jsonify({"results": []})
    if len(q) > 120:
        q = q[:120]

    # Append filter to query for better targeting
    if mode == "music":
        full_q = f"{q} music"
    elif mode == "edu":
        full_q = f"{q} cours tutoriel education"
    else:
        full_q = q

    cache_key = f"{mode}::{full_q.lower()}"
    now = time.time()
    cached = YT_SEARCH_CACHE.get(cache_key)
    if cached and (now - cached[0]) < YT_CACHE_TTL:
        return jsonify({"results": cached[1], "source": "cache"})

    results = _yt_search_api(full_q) or _yt_search_scrape(full_q)
    YT_SEARCH_CACHE[cache_key] = (now, results)
    # Trim cache if it grows too big
    if len(YT_SEARCH_CACHE) > 200:
        oldest = sorted(YT_SEARCH_CACHE.items(), key=lambda x: x[1][0])[:50]
        for k, _ in oldest:
            YT_SEARCH_CACHE.pop(k, None)

    return jsonify({"results": results,
                    "source": "api" if os.environ.get("YOUTUBE_API_KEY") else "scrape"})


@app.route("/player/quick_add", methods=["POST"])
def player_quick_add():
    """Add a YouTube video directly from search results (no URL parsing needed)."""
    student = current_student()
    if not student:
        return jsonify({"error": "auth"}), 401
    payload = request.get_json(silent=True) or {}
    vid = (payload.get("video_id") or "").strip()
    title = (payload.get("title") or "").strip() or f"YouTube · {vid}"
    channel = (payload.get("channel") or "").strip()
    playlist = (payload.get("playlist") or "Study Tracks").strip() or "Study Tracks"
    if not vid or not re.match(r"^[A-Za-z0-9_-]{6,20}$", vid):
        return jsonify({"error": "invalid_id"}), 400

    # Avoid duplicates in same playlist
    existing = Track.query.filter_by(student_id=student.id, kind="youtube",
                                     source=vid, playlist=playlist).first()
    if existing:
        return jsonify({"track": existing.to_dict(), "duplicate": True})

    last = (Track.query.filter_by(student_id=student.id, playlist=playlist)
            .order_by(Track.position.desc()).first())
    full_title = f"{title} — {channel}" if channel and channel not in title else title
    track = Track(student_id=student.id, title=full_title[:200],
                  kind="youtube", source=vid, playlist=playlist,
                  position=(last.position + 1) if last else 0)
    db.session.add(track)
    db.session.commit()
    return jsonify({"track": track.to_dict(), "duplicate": False})


# ─── AI-generated personal themes ───────────────────────────────────────────
# Default themes — sleek dark + neon for everyone. NO floral/pink defaults.
# A cohesive personal theme is generated by the AI from the user's chosen
# aesthetic (Cyberpunk, Minimal, Pastel…); this is only the safe fallback.
_DEFAULT_NEON = {
    "primary":   "#22d3ee",
    "accent":    "#3b82f6",
    "bg":        "#0a0a0f",
    "surface":   "#15151f",
    "text":      "#fafafa",
    "muted":     "#9aa0aa",
    "decoration":"none",
}
DEFAULT_THEMES = {
    "female": dict(_DEFAULT_NEON),
    "male":   dict(_DEFAULT_NEON),
    "other":  dict(_DEFAULT_NEON),
}

DECORATIONS = {"hearts", "butterflies", "floral", "grid", "waves", "stars",
               "geometric", "none"}


def _safe_hex(s: str, fallback: str) -> str:
    """Coerce arbitrary AI output into a valid 6-digit #hex color."""
    s = (s or "").strip()
    if re.fullmatch(r"#?[0-9a-fA-F]{6}", s):
        return "#" + s.lstrip("#").lower()
    if re.fullmatch(r"#?[0-9a-fA-F]{3}", s):
        h = s.lstrip("#").lower()
        return "#" + "".join(c * 2 for c in h)
    return fallback


def _normalize_theme(raw: dict, gender: str) -> dict:
    base = DEFAULT_THEMES.get(gender, DEFAULT_THEMES["other"])
    out = {
        "primary":  _safe_hex(raw.get("primary", ""),  base["primary"]),
        "accent":   _safe_hex(raw.get("accent", ""),   base["accent"]),
        "bg":       _safe_hex(raw.get("bg", ""),       base["bg"]),
        "surface":  _safe_hex(raw.get("surface", ""),  base["surface"]),
        "text":     _safe_hex(raw.get("text", ""),     base["text"]),
        "muted":    _safe_hex(raw.get("muted", ""),    base["muted"]),
    }
    deco = (raw.get("decoration") or "").lower().strip()
    out["decoration"] = deco if deco in DECORATIONS else base["decoration"]
    return out


def _fetch_web_images(query: str, count: int = 3) -> list[tuple[bytes, str]]:
    """Fetch a few inspiration images for the user's interest from free image
    services. Returns a list of (bytes, mime_type) — empty list on failure.

    Tries loremflickr.com (Flickr CC-licensed photos). No API key required.
    """
    out: list[tuple[bytes, str]] = []
    if not query:
        return out
    q = re.sub(r"[^A-Za-z0-9, ]", "", query).strip().replace(" ", ",") or "abstract"
    sources = [
        f"https://loremflickr.com/600/400/{q}?lock={i}" for i in range(1, count + 1)
    ]
    for url in sources:
        try:
            r = requests.get(url, timeout=8, allow_redirects=True,
                             headers={"User-Agent": "SSAS-Theme/1.0"})
            if r.status_code == 200 and r.content and len(r.content) > 1024:
                ctype = r.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
                if ctype.startswith("image/"):
                    out.append((r.content, ctype))
        except Exception as exc:
            print(f"[theme] web image fetch failed for {url}: {exc}", flush=True)
    return out


def generate_theme_from_interest(interest: str, gender: str,
                                  delegation: str = "") -> dict:
    """AI-enhanced theme: search the web for images matching the user's interest,
    feed them to Gemini Vision, and return a custom theme.

    Falls back to gender defaults if web fetch or Gemini fails.
    """
    base = DEFAULT_THEMES.get(gender, DEFAULT_THEMES["other"])
    interest = (interest or "").strip()
    if not interest:
        return dict(base)

    images = _fetch_web_images(interest, count=3)
    if not images or not _gemini_ready():
        return dict(base)

    deco_hint = ("stars, waves or geometric" if gender == "female"
                 else "grid, geometric or waves" if gender == "male"
                 else "any tasteful decoration")
    location_hint = f" from the delegation of {delegation} (Tunisia)" if delegation else ""
    prompt = (
        f"The user (gender: {gender or 'unspecified'}{location_hint}) is interested in: "
        f"\"{interest}\". Analyze the mood, dominant colors and aesthetic of "
        "the attached inspiration images and design ONE cohesive UI color "
        "theme that captures that vibe. Prefer decorations like " + deco_hint
        + ". Return ONLY a compact JSON object (no markdown, no comments) "
        'with exactly these keys: {"primary":"#hex","accent":"#hex",'
        '"bg":"#hex","surface":"#hex","text":"#hex","muted":"#hex",'
        '"decoration":"<one of: hearts, butterflies, floral, grid, waves, '
        'stars, geometric, none>"}. Use 6-digit hex colors. Ensure text is '
        "readable on bg/surface."
    )
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        parts: list = [prompt]
        for img_bytes, mime in images:
            parts.append({"mime_type": mime, "data": img_bytes})
        resp = model.generate_content(parts)
        txt = (getattr(resp, "text", "") or "").strip()
        txt = re.sub(r"^```(?:json)?|```$", "", txt, flags=re.MULTILINE).strip()
        data = _json.loads(txt)
        if not isinstance(data, dict):
            raise ValueError("not a dict")
        return _normalize_theme(data, gender)
    except Exception as exc:
        print(f"[theme] interest-based generation failed: {exc}", flush=True)
        return dict(base)


def generate_theme_from_image(image_bytes: bytes, mime_type: str,
                              gender: str, delegation: str = "") -> dict:
    """Use Gemini Vision to extract a custom theme from a user-uploaded image.

    Falls back to a gender-based default theme if Gemini is unavailable
    or returns invalid data.
    """
    base = DEFAULT_THEMES.get(gender, DEFAULT_THEMES["other"])
    if not _gemini_ready() or not image_bytes:
        return dict(base)

    deco_hint = ("stars, waves or geometric" if gender == "female"
                 else "grid, geometric or waves" if gender == "male"
                 else "any tasteful decoration")
    location_hint = f" The user is from {delegation} (Tunisia)." if delegation else ""
    prompt = (
        "Analyze this image and propose a UI color theme that matches its "
        "mood and dominant colors. The user's gender is "
        f"'{gender or 'unspecified'}'.{location_hint} Prefer decorations like " + deco_hint
        + ". Return ONLY a compact JSON object with exactly these keys "
        '(no markdown): {"primary":"#hex","accent":"#hex","bg":"#hex",'
        '"surface":"#hex","text":"#hex","muted":"#hex","decoration":"<one '
        'of: hearts, butterflies, floral, grid, waves, stars, geometric, none>"}. '
        "Use 6-digit hex colors. Make sure text is readable on bg/surface."
    )
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp = model.generate_content([
            prompt,
            {"mime_type": mime_type or "image/jpeg", "data": image_bytes},
        ])
        txt = (getattr(resp, "text", "") or "").strip()
        # Strip ```json fences if present
        txt = re.sub(r"^```(?:json)?|```$", "", txt, flags=re.MULTILINE).strip()
        data = _json.loads(txt)
        if not isinstance(data, dict):
            raise ValueError("not a dict")
        return _normalize_theme(data, gender)
    except Exception as exc:
        print(f"[theme] Gemini analysis failed: {exc}", flush=True)
        return dict(base)


# ─── Gemini AI Companion ─────────────────────────────────────────────────────
GEMINI_MODEL = "gemini-2.0-flash"
AI_HISTORY_KEY = "ai_history"
AI_MAX_TURNS = 20

# ── Multi-key rotation ────────────────────────────────────────────────────────
# Add backup keys here (or via env): GEMINI_API_KEY, GEMINI_API_KEY_2, GEMINI_API_KEY_3.
# When one key hits a 429/quota error, we automatically fall back to the next.
GEMINI_KEY_ENVS = ["GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"]
_gemini_key_idx = 0          # current active key index
_gemini_active_key = None    # currently configured key (raw value)


def _available_keys() -> list[str]:
    """Return the list of non-empty API keys, in priority order."""
    return [os.environ.get(k, "").strip() for k in GEMINI_KEY_ENVS
            if os.environ.get(k, "").strip()]


def _gemini_ready() -> bool:
    """Configure Gemini with the currently selected key, if any."""
    global _gemini_active_key
    if not _GEMINI_AVAILABLE:
        return False
    keys = _available_keys()
    if not keys:
        return False
    idx = min(_gemini_key_idx, len(keys) - 1)
    target = keys[idx]
    if target != _gemini_active_key:
        genai.configure(api_key=target)
        _gemini_active_key = target
    return True


def _rotate_gemini_key() -> bool:
    """Move to the next available key. Returns True if a new key was activated."""
    global _gemini_key_idx, _gemini_active_key
    keys = _available_keys()
    if len(keys) <= 1:
        return False
    next_idx = (_gemini_key_idx + 1) % len(keys)
    if next_idx == _gemini_key_idx:
        return False
    _gemini_key_idx = next_idx
    _gemini_active_key = None  # force reconfigure on next _gemini_ready()
    return _gemini_ready()


def _is_rate_limit(exc: Exception) -> bool:
    """Detect rate-limit / quota errors across SDK versions."""
    msg = str(exc).lower()
    if "429" in msg or "quota" in msg or "rate" in msg or "exhaust" in msg:
        return True
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    return code == 429


def _ai_system_prompt(student: Student | None) -> str:
    profile_bits = []
    if student:
        if student.username:
            profile_bits.append(f"prénom : {student.username}")
        if student.educational_level:
            profile_bits.append(f"cycle : {student.educational_level}")
        if student.class_section:
            profile_bits.append(f"classe : {student.class_section}")
        if student.section:
            profile_bits.append(f"spécialité : {student.section}")
        if student.school_name:
            profile_bits.append(f"établissement : {student.school_name}")
        if student.region_city:
            profile_bits.append(f"gouvernorat : {student.region_city}")
    profile_line = " · ".join(profile_bits) if profile_bits else "profil inconnu"
    return (
        "Tu es Sami, le compagnon IA de SSAS — une plateforme académique tunisienne. "
        "Tu parles à un étudiant tunisien (français/arabe/darija accepté, réponds dans la langue qu'il utilise). "
        f"Profil de l'étudiant : {profile_line}. "
        "Ta personnalité : intelligent, vif, drôle quand il le faut, ami avant tout — pas un manuel scolaire. "
        "Évite absolument les listes de conseils génériques répétitifs (« révise régulièrement », « dors bien »…). "
        "Engage de vraies discussions : éducation, technologie, vie quotidienne, doutes, projets. "
        "Adapte tes exemples au système tunisien (Bac, sections, coefficients, gouvernorats) quand c'est utile. "
        "Si l'étudiant pose une question scolaire, donne une réponse concrète et utilisable, pas du blabla. "
        "Réponses courtes par défaut (2–4 phrases) sauf si une explication détaillée est demandée."
    )


@app.route("/ai")
def ai_chat():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    history = session.get(AI_HISTORY_KEY, [])
    return render_template("ai_chat.html", student=student, history=history,
                           ai_configured=_gemini_ready(),
                           hf_configured=_hf_ready())


@app.route("/ai/reset", methods=["POST"])
def ai_reset():
    session.pop(AI_HISTORY_KEY, None)
    return redirect(url_for("ai_chat"))


# How many of the most recent turns we actually send to Gemini per call.
# (We still STORE up to AI_MAX_TURNS in the session for UI display.)
AI_CONTEXT_TURNS = 6        # = 6 user + 6 model = 12 messages
AI_MAX_CHARS_PER_MSG = 1200 # truncate long pasted blobs before sending
RETRY_BACKOFFS = [1.0, 3.0, 7.0]  # seconds — exponential-ish


def _trim_history_for_api(history: list[dict]) -> list[dict]:
    """Keep only the last AI_CONTEXT_TURNS exchanges, and cap each message size."""
    trimmed = history[-(AI_CONTEXT_TURNS * 2):]
    out = []
    for h in trimmed:
        text = h.get("text", "") or ""
        if len(text) > AI_MAX_CHARS_PER_MSG:
            text = text[:AI_MAX_CHARS_PER_MSG] + " […]"
        out.append({"role": h["role"], "parts": [text]})
    return out


@app.route("/ai/stream", methods=["POST"])
def ai_stream():
    """Server-Sent Events streaming endpoint for Gemini responses.

    Includes:
    - Friendly 429 / rate-limit handling
    - Exponential backoff retries
    - Trimmed history (only last few turns sent to API)
    - Automatic API key rotation (GEMINI_API_KEY → GEMINI_API_KEY_2 → _3)
    """
    from flask import Response, stream_with_context
    import time

    student = current_student()
    if not student:
        return jsonify({"error": "auth"}), 401
    if not _gemini_ready():
        return jsonify({"error": "Gemini non configuré (GEMINI_API_KEY manquant)."}), 503

    payload = request.get_json(silent=True) or {}
    user_msg = (payload.get("message") or "").strip()
    if not user_msg:
        return jsonify({"error": "empty"}), 400
    if len(user_msg) > AI_MAX_CHARS_PER_MSG:
        user_msg = user_msg[:AI_MAX_CHARS_PER_MSG] + " […]"

    history = session.get(AI_HISTORY_KEY, [])
    gem_history = _trim_history_for_api(history)
    system_prompt = _ai_system_prompt(student)

    def build_chat():
        model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompt)
        return model.start_chat(history=gem_history)

    def event_stream():
        full: list[str] = []
        last_err: Exception | None = None
        keys_tried = 0
        max_keys = max(1, len(_available_keys()))

        # Outer loop: try each available API key
        while keys_tried < max_keys:
            keys_tried += 1

            # Inner loop: retry the same key with exponential backoff
            for attempt in range(len(RETRY_BACKOFFS) + 1):
                try:
                    chat_obj = build_chat()
                    for chunk in chat_obj.send_message(user_msg, stream=True):
                        txt = getattr(chunk, "text", "") or ""
                        if not txt:
                            continue
                        full.append(txt)
                        safe = txt.replace("\r", "")
                        for line in safe.split("\n"):
                            yield f"data: {line}\n"
                        yield "data: \\n\n\n"
                    # Success → persist + done
                    reply = "".join(full).strip()
                    new_hist = history + [
                        {"role": "user", "text": user_msg},
                        {"role": "model", "text": reply},
                    ]
                    session[AI_HISTORY_KEY] = new_hist[-(AI_MAX_TURNS * 2):]
                    yield "event: done\ndata: ok\n\n"
                    return

                except Exception as exc:
                    last_err = exc
                    full.clear()  # discard any partial text so retry is clean

                    if _is_rate_limit(exc):
                        # Tell the user we're waiting / retrying
                        if attempt < len(RETRY_BACKOFFS):
                            wait = RETRY_BACKOFFS[attempt]
                            yield (f"event: status\n"
                                   f"data: ⏳ Sami réfléchit… nouvelle tentative dans {wait:.0f}s\n\n")
                            time.sleep(wait)
                            continue
                        # Backoffs exhausted on this key → try rotating
                        break
                    else:
                        # Non-rate-limit error → surface immediately
                        yield f"event: error\ndata: {str(exc)[:240]}\n\n"
                        return

            # Try next key if available
            if keys_tried < max_keys and _rotate_gemini_key():
                yield "event: status\ndata: 🔄 Bascule vers une clé API de secours…\n\n"
                continue
            break

        # All keys + retries exhausted
        if last_err and _is_rate_limit(last_err):
            friendly = ("Sami réfléchit beaucoup en ce moment 🧠 — "
                        "patiente quelques secondes avant ta prochaine question. "
                        "(Limite d'utilisation Gemini atteinte.)")
        else:
            friendly = f"Erreur Gemini : {str(last_err)[:200] if last_err else 'inconnue'}"
        yield f"event: error\ndata: {friendly}\n\n"

    return Response(stream_with_context(event_stream()),
                    mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache",
                             "X-Accel-Buffering": "no"})


# ─── People Search / Discover ───────────────────────────────────────────────
@app.route("/search")
def search_page():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    return render_template("search.html", student=student)


@app.route("/api/search/people")
def api_search_people():
    student = current_student()
    if not student:
        return jsonify({"results": []}), 401
    q = (request.args.get("q", "") or "").strip()
    base = Student.query.filter(Student.id != student.id)
    if q:
        like = f"%{q}%"
        base = base.filter(or_(
            Student.username.ilike(like),
            Student.school_name.ilike(like),
            Student.region_city.ilike(like),
            Student.class_section.ilike(like),
        ))
    rows = base.order_by(Student.username).limit(50).all()
    return jsonify({"results": [s.to_dict() | {"class_section": s.class_section} for s in rows]})


# ─── Settings ────────────────────────────────────────────────────────────────
@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    student = current_student()
    if not student:
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "appearance":
            theme = request.form.get("theme", "dark")
            language = request.form.get("language", "fr")
            if theme in SUPPORTED_THEMES:
                student.theme = theme
                session["theme"] = theme
            if language in SUPPORTED_LANGS:
                student.language = language
                session["lang"] = language
            db.session.commit()
            flash("Préférences enregistrées.", "success")
        elif action == "profile":
            new_name = (request.form.get("username") or "").strip()
            if len(new_name) >= 3 and new_name != student.username:
                exists = Student.query.filter(Student.username == new_name,
                                              Student.id != student.id).first()
                if exists:
                    flash(t("err_email_taken"), "error")
                    return redirect(url_for("settings_page"))
                student.username = new_name
                session["username"] = new_name
            # Allow updating school/level/class via the same form (optional)
            for field in ("educational_level", "region_city", "school_name",
                          "class_section", "section", "phone", "delegation", "governorate"):
                val = (request.form.get(field) or "").strip()
                if val:
                    setattr(student, field, val)
            db.session.commit()
            flash(t("success_profile"), "success")
        elif action == "regen_theme":
            # Regenerate the AI personal theme from a fresh photo OR from an
            # interest keyword (which triggers a web image search + analysis)
            new_gender = (request.form.get("gender") or student.gender or "other").lower()
            if new_gender not in {"female", "male", "other"}:
                new_gender = "other"
            student.gender = new_gender
            new_delegation = (request.form.get("delegation") or "").strip()
            if new_delegation:
                student.delegation = new_delegation
            interest = (request.form.get("interest") or "").strip()
            photo = request.files.get("theme_photo")
            theme_obj = dict(DEFAULT_THEMES.get(new_gender, DEFAULT_THEMES["other"]))
            try:
                if photo and photo.filename:
                    img_bytes = photo.read()
                    if img_bytes:
                        mime = photo.mimetype or "image/jpeg"
                        theme_obj = generate_theme_from_image(img_bytes, mime, new_gender,
                                                              delegation=student.delegation or "")
                elif interest:
                    theme_obj = generate_theme_from_interest(interest, new_gender,
                                                             delegation=student.delegation or "")
            except Exception as exc:
                print(f"[theme] regen failed: {exc}", flush=True)
                flash("Analyse impossible — thème par défaut appliqué.", "error")
            student.custom_theme = _json.dumps(theme_obj)
            db.session.commit()
            flash("✨ Thème personnel mis à jour.", "success")
        elif action == "logout_all":
            # Best-effort: bump the secret key would invalidate ALL sessions. We just clear ours.
            session.clear()
            flash("Vous avez été déconnecté.", "success")
            return redirect(url_for("login"))
        return redirect(url_for("settings_page"))

    return render_template("settings.html", student=student,
                           educational_levels=EDUCATIONAL_LEVELS,
                           regions=ALL_REGIONS, governorates=ALL_GOVERNORATES,
                           all_schools=ALL_SCHOOLS,
                           class_sections=CLASS_SECTIONS, sections=SECTIONS)


# ─── Group Chats ─────────────────────────────────────────────────────────────
def _is_member(student: Student, group: Group) -> bool:
    return GroupMember.query.filter_by(group_id=group.id, student_id=student.id).first() is not None


def _user_groups(student: Student) -> list[Group]:
    rows = (db.session.query(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .filter(GroupMember.student_id == student.id)
            .order_by(Group.created_at.desc()).all())
    return rows


@app.route("/groups/new", methods=["GET", "POST"])
def group_new():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        desc = (request.form.get("description") or "").strip() or None
        members = request.form.getlist("members")
        if len(name) < 2:
            flash("Le nom du groupe est trop court.", "error")
            return redirect(url_for("group_new"))
        g = Group(name=name[:120], description=desc, owner_id=student.id)
        db.session.add(g); db.session.flush()
        # owner auto-joins
        db.session.add(GroupMember(group_id=g.id, student_id=student.id, role="owner"))
        for raw in members:
            try:
                mid = int(raw)
            except ValueError:
                continue
            if mid == student.id:
                continue
            if not Student.query.get(mid):
                continue
            if not GroupMember.query.filter_by(group_id=g.id, student_id=mid).first():
                db.session.add(GroupMember(group_id=g.id, student_id=mid, role="member"))
        db.session.commit()
        flash("Groupe créé.", "success")
        return redirect(url_for("group_chat", gid=g.id))
    all_students = (Student.query.filter(Student.id != student.id)
                    .order_by(Student.username).all())
    return render_template("group_new.html", student=student, all_students=all_students)


@app.route("/groups/<int:gid>")
def group_chat(gid: int):
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    g = db.session.get(Group, gid) or abort(404)
    if not _is_member(student, g):
        flash("Vous n'êtes pas membre de ce groupe.", "error")
        return redirect(url_for("messages"))
    thread = (Message.query.filter_by(group_id=g.id)
              .order_by(Message.created_at.asc()).limit(500).all())
    members = [m.student for m in g.members.all()]
    return render_template("group_chat.html", student=student, group=g,
                           thread=thread, members=members)


@app.route("/groups/<int:gid>/invite", methods=["POST"])
def group_invite(gid: int):
    student = current_student()
    if not student:
        return jsonify({"error": "auth"}), 401
    g = db.session.get(Group, gid) or abort(404)
    if not _is_member(student, g):
        return jsonify({"error": "forbidden"}), 403
    payload = request.get_json(silent=True) or {}
    new_ids = payload.get("ids") or []
    added = []
    for raw in new_ids:
        try:
            mid = int(raw)
        except (TypeError, ValueError):
            continue
        if not Student.query.get(mid):
            continue
        if GroupMember.query.filter_by(group_id=g.id, student_id=mid).first():
            continue
        db.session.add(GroupMember(group_id=g.id, student_id=mid))
        added.append(mid)
    db.session.commit()
    return jsonify({"added": added})


@app.route("/groups/<int:gid>/leave", methods=["POST"])
def group_leave(gid: int):
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    gm = GroupMember.query.filter_by(group_id=gid, student_id=student.id).first()
    if gm:
        db.session.delete(gm)
        db.session.commit()
        flash("Vous avez quitté le groupe.", "success")
    return redirect(url_for("messages"))


# ─── Group socket events ─────────────────────────────────────────────────────
def _group_room(gid: int) -> str:
    return f"group_{gid}"


@socketio.on("join_group")
def _sio_join_group(data):
    student = current_student()
    if not student:
        return
    try:
        gid = int(data.get("group_id"))
    except (TypeError, ValueError):
        return
    g = db.session.get(Group, gid)
    if g and _is_member(student, g):
        join_room(_group_room(gid))


@socketio.on("send_group_message")
def _sio_send_group(data):
    student = current_student()
    if not student:
        return
    try:
        gid = int(data.get("group_id"))
    except (TypeError, ValueError):
        return
    body = (data.get("body") or "").strip()
    if not body:
        return
    g = db.session.get(Group, gid)
    if not g or not _is_member(student, g):
        return
    # recipient_id is set to sender_id as a placeholder (group_id holds real target)
    msg = Message(sender_id=student.id, recipient_id=student.id,
                  group_id=gid, body=body)
    db.session.add(msg)
    db.session.commit()
    payload = msg.to_dict() | {
        "sender_username": student.username,
        "sender_level": student.level,
        "sender_badge": student.badge_icon or badge_for_level(student.level or 1),
        "sender_avatar": student.avatar_url,
    }
    emit("new_group_message", payload, room=_group_room(gid))
    award_xp(student, 5, "group_message_sent")


# ─── WebRTC 1-on-1 Call Signaling ────────────────────────────────────────────
@app.route("/call/<int:peer_id>")
def call_page(peer_id: int):
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    peer = db.session.get(Student, peer_id) or abort(404)
    if peer.id == student.id:
        return redirect(url_for("messages"))
    mode = request.args.get("mode", "video")  # video | audio
    role = request.args.get("role", "caller") # caller | callee
    return render_template("call.html", student=student, peer=peer,
                           mode=mode, role=role)


@socketio.on("call_invite")
def _sio_call_invite(data):
    student = current_student()
    if not student:
        return
    try:
        peer_id = int(data.get("peer_id"))
    except (TypeError, ValueError):
        return
    mode = data.get("mode") if data.get("mode") in ("video", "audio") else "video"
    emit("incoming_call", {
        "from_user_id": student.id,
        "from_username": student.username,
        "mode": mode,
    }, room=_user_room(peer_id))


@socketio.on("call_signal")
def _sio_call_signal(data):
    """Relay WebRTC signaling payloads (offer/answer/ICE) to the peer."""
    student = current_student()
    if not student:
        return
    try:
        peer_id = int(data.get("peer_id"))
    except (TypeError, ValueError):
        return
    payload = {
        "from_user_id": student.id,
        "kind": data.get("kind"),       # 'offer' | 'answer' | 'ice' | 'end'
        "data": data.get("data"),
    }
    emit("call_signal", payload, room=_user_room(peer_id))


# ─── Sync Listen (collaborative listening rooms) ─────────────────────────────
# In-memory map  room_id -> {"host_id": int, "track": dict, "playing": bool,
#                            "position": float, "updated_at": ts}
SYNC_ROOMS: dict[str, dict] = {}


def _sync_room(host_id: int) -> str:
    return f"sync:{host_id}"


@app.route("/api/sync/<int:host_id>")
def sync_room_state(host_id: int):
    state = SYNC_ROOMS.get(_sync_room(host_id))
    if not state:
        return jsonify({"exists": False})
    return jsonify({"exists": True, **state})


@socketio.on("sync_join")
def _sync_join(data):
    student = current_student()
    if not student:
        return
    try:
        host_id = int(data.get("host_id"))
    except (TypeError, ValueError):
        return
    room = _sync_room(host_id)
    join_room(room)
    state = SYNC_ROOMS.get(room)
    if state:
        emit("sync_state", state)


@socketio.on("sync_host")
def _sync_host(data):
    """Host announces / updates the current playback state."""
    student = current_student()
    if not student:
        return
    room = _sync_room(student.id)
    join_room(room)
    state = {
        "host_id": student.id,
        "host_username": student.username,
        "track": data.get("track") or {},
        "playing": bool(data.get("playing")),
        "position": float(data.get("position") or 0),
        "updated_at": time.time(),
    }
    SYNC_ROOMS[room] = state
    emit("sync_state", state, room=room, include_self=False)


@socketio.on("sync_leave")
def _sync_leave(data):
    student = current_student()
    if not student:
        return
    try:
        host_id = int(data.get("host_id"))
    except (TypeError, ValueError):
        return
    room = _sync_room(host_id)
    # If the host leaves, dissolve the room.
    if student.id == host_id:
        SYNC_ROOMS.pop(room, None)
        emit("sync_closed", {"host_id": host_id}, room=room)


# ─── PWA: manifest + service worker ──────────────────────────────────────────
@app.route("/manifest.webmanifest")
def pwa_manifest():
    return jsonify({
        "name": "SSAS — Plateforme Académique",
        "short_name": "SSAS",
        "description": "Plateforme académique tunisienne — notes, groupes, IA, musique.",
        "start_url": "/",
        "scope": "/",
        "id": "/",
        "display": "standalone",
        "display_override": ["standalone", "minimal-ui"],
        "orientation": "portrait",
        "background_color": "#0a0a0f",
        "theme_color": "#0a0a0f",
        "lang": get_lang(),
        "dir": "rtl" if get_lang() in RTL_LANGS else "ltr",
        "categories": ["education", "social", "productivity"],
        "icons": [
            {"src": url_for("static", filename="icon.svg"), "sizes": "any",
             "type": "image/svg+xml", "purpose": "any maskable"},
            {"src": url_for("static", filename="icon-512.png"), "sizes": "512x512",
             "type": "image/png", "purpose": "any"},
            {"src": url_for("static", filename="icon-512.png"), "sizes": "512x512",
             "type": "image/png", "purpose": "maskable"},
        ],
        "shortcuts": [
            {"name": "Sami AI", "url": "/ai", "icons": [
                {"src": url_for("static", filename="icon.svg"), "sizes": "any"}]},
            {"name": "Messages", "url": "/messages"},
            {"name": "Lecteur", "url": "/player"},
        ],
    })


@app.route("/sw.js")
def pwa_service_worker():
    """Serve service worker from the root scope so it can control the whole app."""
    from flask import send_from_directory
    resp = send_from_directory(Path(__file__).parent / "static", "sw.js",
                               mimetype="application/javascript")
    resp.headers["Service-Worker-Allowed"] = "/"
    resp.headers["Cache-Control"] = "no-cache"
    return resp


# ─── Gamification (XP, levels, badges, leaderboard) ─────────────────────────
def xp_needed_for_level(level: int) -> int:
    """100 XP for L1→L2, then +50 per level (e.g. L2→L3 = 150)."""
    return 100 + max(0, level - 1) * 50


def badge_for_level(level: int) -> str:
    if level >= 25: return "🏆"
    if level >= 15: return "💎"
    if level >= 8:  return "🥇"
    if level >= 4:  return "🥈"
    if level >= 2:  return "🥉"
    return "🌱"


def award_xp(student: Student, amount: int, reason: str = "") -> dict:
    """Add XP, level-up if needed, persist, and emit a live socket event."""
    if not student or amount <= 0:
        return {"awarded": 0, "level_up": False}
    student.experience = (student.experience or 0) + amount
    student.points = (student.points or 0) + amount
    leveled = False
    while student.experience >= xp_needed_for_level(student.level or 1):
        student.experience -= xp_needed_for_level(student.level or 1)
        student.level = (student.level or 1) + 1
        leveled = True
    student.badge_icon = badge_for_level(student.level)
    db.session.commit()
    payload = {
        "awarded": amount,
        "reason": reason,
        "points": student.points,
        "level": student.level,
        "experience": student.experience,
        "next_level_at": xp_needed_for_level(student.level),
        "badge": student.badge_icon,
        "level_up": leveled,
    }
    try:
        socketio.emit("xp_update", payload, room=_user_room(student.id))
    except Exception:
        pass
    return payload


@app.route("/api/me/xp")
def api_my_xp():
    s = current_student()
    if not s:
        return jsonify({"error": "auth"}), 401
    return jsonify({
        "points": s.points or 0,
        "level": s.level or 1,
        "experience": s.experience or 0,
        "next_level_at": xp_needed_for_level(s.level or 1),
        "badge": s.badge_icon or badge_for_level(s.level or 1),
    })


@app.route("/leaderboard")
def leaderboard():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    top_students = (Student.query
                    .filter(Student.points > 0)
                    .order_by(Student.points.desc())
                    .limit(50).all())
    # Top schools by total student points
    rows = (db.session.query(Student.school_name,
                             db.func.sum(Student.points).label("total"),
                             db.func.count(Student.id).label("members"))
            .filter(Student.school_name.isnot(None), Student.school_name != "")
            .group_by(Student.school_name)
            .order_by(db.func.sum(Student.points).desc())
            .limit(25).all())
    top_schools = [{"name": r[0], "total": int(r[1] or 0), "members": int(r[2] or 0)}
                   for r in rows]
    return render_template("leaderboard.html", student=student,
                           top_students=top_students, top_schools=top_schools,
                           xp_for_next=xp_needed_for_level)


# ─── School Explorer ─────────────────────────────────────────────────────────
@app.route("/school/<path:institution>")
def school_explorer(institution: str):
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    members = (Student.query
               .filter(Student.school_name == institution)
               .order_by(Student.points.desc(), Student.username.asc())
               .all())
    total_points = sum((m.points or 0) for m in members)
    return render_template("school_explorer.html", student=student,
                           institution=institution, members=members,
                           total_points=total_points)


@app.route("/select-school", methods=["GET", "POST"])
def select_school():
    """Lightweight first-time school picker for users coming from Google login."""
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    if request.method == "POST":
        chosen = (request.form.get("school_name") or "").strip()
        if chosen:
            student.school_name = chosen
            db.session.commit()
        return redirect(url_for("complete_profile"))
    return render_template("select_school.html", student=student,
                           all_schools=ALL_SCHOOLS)


# ─── Resources (PDFs / summaries / links) ────────────────────────────────────
@app.route("/resources")
def resources_index():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    q = (request.args.get("q") or "").strip()
    scope = request.args.get("scope", "all")  # 'all' | 'school'
    base = Resource.query.order_by(Resource.created_at.desc())
    if scope == "school" and student.school_name:
        base = base.filter(Resource.institution == student.school_name)
    if q:
        like = f"%{q}%"
        base = base.filter(or_(Resource.title.ilike(like),
                               Resource.description.ilike(like),
                               Resource.subject.ilike(like)))
    rows = base.limit(100).all()
    return render_template("resources.html", student=student, resources=rows,
                           q=q, scope=scope)


@app.route("/resources/new", methods=["GET", "POST"])
def resource_new():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip() or None
        kind = request.form.get("kind", "file")
        subject = (request.form.get("subject") or "").strip() or None
        if len(title) < 2:
            flash("Le titre est trop court.", "error")
            return redirect(url_for("resource_new"))

        file_path = link_url = body = None
        if kind == "file":
            f = request.files.get("file")
            if not f or not f.filename:
                flash("Veuillez choisir un fichier.", "error")
                return redirect(url_for("resource_new"))
            ext = f.filename.rsplit(".", 1)[-1].lower()
            if ext not in RESOURCE_ALLOWED:
                flash("Type de fichier non autorisé.", "error")
                return redirect(url_for("resource_new"))
            safe_name = f"{uuid.uuid4().hex}.{ext}"
            dest = RESOURCE_UPLOAD_DIR / safe_name
            f.save(dest)
            file_path = f"/static/uploads/resources/{safe_name}"
        elif kind == "link":
            link_url = (request.form.get("link_url") or "").strip()
            if not link_url.startswith(("http://", "https://")):
                flash("URL invalide.", "error")
                return redirect(url_for("resource_new"))
        elif kind == "text":
            body = (request.form.get("body") or "").strip()
            if len(body) < 10:
                flash("Le résumé est trop court.", "error")
                return redirect(url_for("resource_new"))
        else:
            flash("Type inconnu.", "error")
            return redirect(url_for("resource_new"))

        r = Resource(student_id=student.id, title=title[:200], description=description,
                     kind=kind, file_path=file_path, link_url=link_url, body=body,
                     subject=subject, educational_level=student.educational_level,
                     institution=student.school_name)
        db.session.add(r)
        db.session.commit()
        award_xp(student, 20, "resource_shared")
        flash("Ressource publiée — +20 XP 🎉", "success")
        return redirect(url_for("resources_index"))
    return render_template("resource_new.html", student=student)


@app.route("/resources/<int:rid>/upvote", methods=["POST"])
def resource_upvote(rid: int):
    student = current_student()
    if not student:
        return jsonify({"error": "auth"}), 401
    r = db.session.get(Resource, rid) or abort(404)
    r.upvotes = (r.upvotes or 0) + 1
    if r.student_id != student.id:
        author = db.session.get(Student, r.student_id)
        if author:
            author.reputation = (author.reputation or 0) + 1
    db.session.commit()
    return jsonify({"upvotes": r.upvotes})


# ─── Profile picture upload ──────────────────────────────────────────────────
@app.route("/api/avatar", methods=["POST"])
def api_avatar_upload():
    student = current_student()
    if not student:
        return jsonify({"error": "auth"}), 401
    f = request.files.get("avatar")
    if not f or not f.filename:
        return jsonify({"error": "no_file"}), 400
    ext = f.filename.rsplit(".", 1)[-1].lower()
    if ext not in AVATAR_ALLOWED:
        return jsonify({"error": "bad_type"}), 400
    safe_name = f"{student.id}_{uuid.uuid4().hex[:8]}.{ext}"
    dest = AVATAR_UPLOAD_DIR / safe_name
    f.save(dest)
    student.avatar_url = f"/static/uploads/avatars/{safe_name}"
    db.session.commit()
    return jsonify({"avatar_url": student.avatar_url})


# ─── Focus Mode (Pomodoro) ───────────────────────────────────────────────────
@app.route("/focus")
def focus_page():
    student = current_student()
    if not student:
        return redirect(url_for("login"))
    return render_template("focus.html", student=student)


@app.route("/api/focus/complete", methods=["POST"])
def api_focus_complete():
    """Called by client when a 25-min pomodoro completes. Awards 50 XP."""
    student = current_student()
    if not student:
        return jsonify({"error": "auth"}), 401
    payload = request.get_json(silent=True) or {}
    minutes = int(payload.get("minutes") or 0)
    if minutes < 20:  # anti-cheat sanity check
        return jsonify({"error": "too_short"}), 400
    info = award_xp(student, 50, "pomodoro_completed")
    return jsonify(info)


# ─── Hugging Face Inference Providers (Sami v3 — IT & Sport in Darija) ──────
# Uses the modern Router endpoint (OpenAI-compatible chat completions).
# https://huggingface.co/docs/inference-providers
HF_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN", "").strip()
# Comma-separated model fallback chain. Stronger multilingual models go first;
# we fall back gracefully if one provider is offline / model is unavailable.
HF_MODEL_CHAIN = [
    m.strip() for m in os.environ.get(
        "HF_MODEL",
        "meta-llama/Llama-3.3-70B-Instruct:novita,"
        "Qwen/Qwen2.5-72B-Instruct:nebius,"
        "meta-llama/Llama-3.1-70B-Instruct:novita,"
        "meta-llama/Llama-3.1-8B-Instruct:novita"
    ).split(",") if m.strip()
]
HF_ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"


def _hf_ready() -> bool:
    return bool(HF_API_TOKEN)


def _hf_system_prompt(student: Student | None) -> str:
    bits = []
    if student:
        if student.username:           bits.append(f"prénom: {student.username}")
        if student.educational_level:  bits.append(f"cycle: {student.educational_level}")
        if student.class_section:      bits.append(f"classe: {student.class_section}")
        if student.school_name:        bits.append(f"école: {student.school_name}")
        if student.region_city:        bits.append(f"délégation: {student.region_city}")
        if student.governorate:        bits.append(f"gouvernorat: {student.governorate}")
    profile = " · ".join(bits) if bits else "profil inconnu"
    return (
        "You are Sami, a Tunisian student coach inside SSAS. You ALWAYS reply in "
        "Tunisian Darija written in LATIN script (Arabizi: 3, 7, 9 for ع ح ق, "
        "with French loanwords mixed in naturally — exactly how Tunisian students "
        "chat on WhatsApp). Example tone: « 3aslema! Hak chnowa lazmek ta3mel: "
        "1) ... 2) ... 3) ... Kifech 7abbeb t3awed t9rralek had el partie? »\n\n"
        "Specialties: IT (programmation, web, mobile, IA, cybersécurité, hardware, "
        "networking, devops) and Sport (musculation, football, fitness, cardio, "
        "nutrition, récupération). Outside these two domains, answer briefly then "
        "redirect to IT or Sport.\n\n"
        f"Student profile: {profile}.\n\n"
        "Rules:\n"
        "• If the user writes in French, English or Arabic, mirror their language "
        "  (still warm and direct, no robotic tone).\n"
        "• Be concrete and concise (3 to 6 short sentences by default). Use bullet "
        "  lists or numbered steps when it helps.\n"
        "• Give real examples: code snippets in markdown ``` blocks for IT, sets x reps "
        "  schemas for sport (ex. « 4x8 squat @ 70% RM »).\n"
        "• NEVER repeat the same phrase twice. NEVER produce filler like « Python "
        "  est un langage… Python est un langage… ». If you don't know, say so honestly.\n"
        "• Don't act like a textbook — talk like a pro friend who already knows the "
        "  Tunisian school system (bac, devoirs, sections, lycées)."
    )


def _build_messages(system: str, history: list[dict], user_msg: str) -> list[dict]:
    """Build OpenAI-compatible messages array for the Router endpoint."""
    msgs: list[dict] = [{"role": "system", "content": system}]
    for h in history[-12:]:
        role = "user" if h.get("role") == "user" else "assistant"
        text = (h.get("text") or "")[:1200]
        if text:
            msgs.append({"role": role, "content": text})
    msgs.append({"role": "user", "content": user_msg})
    return msgs


def _hf_call_one(model: str, messages: list[dict],
                 max_new_tokens: int) -> tuple[str | None, str | None]:
    """Call one HF Router model. Returns (text, error)."""
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}",
               "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_new_tokens,
        "temperature": 0.65,
        "top_p": 0.9,
        "frequency_penalty": 0.6,
        "presence_penalty": 0.3,
        "stream": False,
    }
    for attempt in range(2):
        try:
            r = requests.post(HF_ROUTER_URL, headers=headers, json=payload, timeout=60)
        except requests.RequestException as e:
            return None, f"network: {e}"
        if r.status_code == 503:
            time.sleep(3 + attempt * 3)
            continue
        if r.status_code in (401, 403):
            return None, "huggingface_unauthorized"
        if r.status_code == 429:
            time.sleep(2 + attempt * 2)
            continue
        if r.status_code == 404:
            return None, f"hf_model_not_found: {model}"
        if not r.ok:
            return None, f"hf_http_{r.status_code}: {r.text[:200]}"
        try:
            data = r.json()
        except Exception:
            return None, "hf_bad_json"
        try:
            choice = data["choices"][0]
            msg = choice.get("message") or {}
            content = (msg.get("content") or "").strip()
            if content:
                return content, None
        except Exception:
            pass
        if isinstance(data, dict) and data.get("error"):
            err_obj = data["error"]
            err_str = err_obj if isinstance(err_obj, str) else (err_obj.get("message") if isinstance(err_obj, dict) else str(err_obj))
            return None, str(err_str)[:240]
        return None, "hf_unexpected"
    return None, "hf_loading_timeout"


def _hf_generate(system: str, history: list[dict], user_msg: str,
                 max_new_tokens: int = 500) -> tuple[str | None, str | None]:
    """Walk the HF model fallback chain. Returns (text, error)."""
    if not _hf_ready():
        return None, "huggingface_token_missing"
    messages = _build_messages(system, history, user_msg)
    last_err: str | None = None
    fatal = {"huggingface_unauthorized", "huggingface_token_missing"}
    for model in HF_MODEL_CHAIN:
        text, err = _hf_call_one(model, messages, max_new_tokens)
        if text:
            return text, None
        last_err = err
        # Don't keep trying if the token itself is the problem.
        if err in fatal:
            return None, err
    return None, last_err or "hf_unexpected"


@app.route("/ai/hf", methods=["POST"])
def ai_hf():
    """Non-streaming Hugging Face endpoint (used as primary if token is set)."""
    student = current_student()
    if not student:
        return jsonify({"error": "auth"}), 401
    if not _hf_ready():
        return jsonify({"error": "Hugging Face non configuré (HUGGINGFACE_API_TOKEN manquant)."}), 503
    payload = request.get_json(silent=True) or {}
    user_msg = (payload.get("message") or "").strip()
    if not user_msg:
        return jsonify({"error": "empty"}), 400
    history = session.get(AI_HISTORY_KEY, [])
    text_out, err = _hf_generate(_hf_system_prompt(student), history, user_msg)
    if err:
        friendly = {
            "huggingface_token_missing":  "Sami n'est pas encore connecté à Hugging Face.",
            "huggingface_unauthorized":   "Jeton Hugging Face invalide ou modèle non autorisé.",
            "hf_loading_timeout":         "Le modèle se réveille, réessaie dans quelques secondes ⏳",
        }.get(err, f"Erreur Sami : {err}")
        return jsonify({"error": friendly}), 503
    new_hist = history + [
        {"role": "user", "text": user_msg},
        {"role": "model", "text": text_out},
    ]
    session[AI_HISTORY_KEY] = new_hist[-(AI_MAX_TURNS * 2):]
    return jsonify({"reply": text_out})


# ─── Cloud Upload API ─────────────────────────────────────────────────────────
@app.route("/api/upload", methods=["POST"])
def api_upload():
    """Upload an image or video; route to the correct cloud provider."""
    student = current_student()
    if not student:
        return jsonify({"error": "auth"}), 401
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify({"error": "no file"}), 400
    file_bytes = f.read()
    mime = f.mimetype or ""
    result = sm.route_upload(file_bytes, f.filename, mime)
    uf = UserFile(
        student_id=student.id,
        file_url=result["url"],
        provider_name=result["provider"],
        public_id=result.get("public_id"),
        file_type=result["file_type"],
        original_name=f.filename,
        size_bytes=len(file_bytes),
    )
    db.session.add(uf)
    db.session.commit()
    return jsonify({
        "url": result["url"],
        "provider": result["provider"],
        "file_type": result["file_type"],
        "id": uf.id,
        "warning": result.get("error"),
    })


# ─── Admin Master Dashboard ────────────────────────────────────────────────────
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "").strip().lower()


def _is_admin(student: Student | None) -> bool:
    if not student:
        return False
    if student.is_admin:
        return True
    if ADMIN_EMAIL and (student.email or "").strip().lower() == ADMIN_EMAIL:
        return True
    return False


@app.route("/admin-master")
def admin_master():
    student = current_student()
    if not _is_admin(student):
        abort(404)
    lang = get_lang()
    theme = get_theme()

    total_users = Student.query.count()
    total_files = UserFile.query.count()

    users = Student.query.order_by(Student.created_at.desc()).limit(50).all()

    cl_usage = sm.cloudinary_usage()
    cl_configured = sm._cloudinary_configured()
    fb_configured = sm._firebase_configured()

    neon_setting = db.session.get(SystemSetting, "global_neon_mode")
    neon_on = (neon_setting.value == "1") if neon_setting else False

    google_ok = google_is_configured()
    gemini_keys = [os.environ.get(k, "").strip() for k in ["GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"]]
    gemini_ok = any(gemini_keys)
    hf_ok = bool(os.environ.get("HUGGINGFACE_API_TOKEN", "").strip())
    smtp_ok = _smtp_configured()

    secrets_audit = [
        {"name": "SESSION_SECRET",            "ok": bool(os.environ.get("SESSION_SECRET")),      "purpose": "Flask session encryption"},
        {"name": "ADMIN_EMAIL",               "ok": bool(ADMIN_EMAIL),                             "purpose": "Your private admin email"},
        {"name": "GOOGLE_OAUTH_CLIENT_ID",    "ok": bool(os.environ.get("GOOGLE_OAUTH_CLIENT_ID")), "purpose": "Google login (OAuth)"},
        {"name": "GOOGLE_OAUTH_CLIENT_SECRET","ok": bool(os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")), "purpose": "Google login (OAuth)"},
        {"name": "GEMINI_API_KEY",            "ok": gemini_ok,                                    "purpose": "AI Mentor (Sami) — primary key"},
        {"name": "GEMINI_API_KEY_2",          "ok": bool(gemini_keys[1]),                         "purpose": "AI Mentor — backup key #2"},
        {"name": "GEMINI_API_KEY_3",          "ok": bool(gemini_keys[2]),                         "purpose": "AI Mentor — backup key #3"},
        {"name": "HUGGINGFACE_API_TOKEN",     "ok": hf_ok,                                        "purpose": "HuggingFace AI fallback"},
        {"name": "SMTP_HOST",                 "ok": smtp_ok,                                       "purpose": "Email verification & password reset"},
        {"name": "SMTP_USER",                 "ok": smtp_ok,                                       "purpose": "Email sender address"},
        {"name": "SMTP_PASSWORD",             "ok": smtp_ok,                                       "purpose": "Email SMTP password"},
        {"name": "CLOUDINARY_CLOUD_NAME",     "ok": cl_configured,                                "purpose": "Image cloud storage (Cloudinary)"},
        {"name": "CLOUDINARY_API_KEY",        "ok": cl_configured,                                "purpose": "Image cloud storage (Cloudinary)"},
        {"name": "CLOUDINARY_API_SECRET",     "ok": cl_configured,                                "purpose": "Image cloud storage (Cloudinary)"},
        {"name": "FIREBASE_STORAGE_BUCKET",   "ok": fb_configured,                                "purpose": "Video cloud storage (Firebase)"},
        {"name": "FIREBASE_SERVICE_ACCOUNT_JSON", "ok": fb_configured,                           "purpose": "Video cloud storage (Firebase)"},
    ]

    unread_count = Message.query.filter_by(recipient_id=student.id, is_read=0, group_id=None).count() if student else 0

    return render_template(
        "admin_master.html",
        current_student=student,
        lang=lang, theme=theme,
        is_rtl=lang in RTL_LANGS,
        unread_count=unread_count,
        total_users=total_users,
        total_files=total_files,
        users=users,
        cl_usage=cl_usage,
        cl_configured=cl_configured,
        fb_configured=fb_configured,
        neon_on=neon_on,
        secrets_audit=secrets_audit,
        google_ok=google_ok,
        gemini_ok=gemini_ok,
        hf_ok=hf_ok,
        smtp_ok=smtp_ok,
    )


@app.route("/admin-master/toggle-neon", methods=["POST"])
def admin_toggle_neon():
    student = current_student()
    if not _is_admin(student):
        abort(404)
    neon_setting = db.session.get(SystemSetting, "global_neon_mode")
    if neon_setting:
        neon_setting.value = "0" if neon_setting.value == "1" else "1"
    else:
        neon_setting = SystemSetting(key="global_neon_mode", value="1")
        db.session.add(neon_setting)
    db.session.commit()
    new_val = neon_setting.value == "1"
    socketio.emit("global_neon", {"on": new_val}, broadcast=True)
    return jsonify({"neon": new_val})


@app.route("/admin-master/broadcast", methods=["POST"])
def admin_broadcast():
    student = current_student()
    if not _is_admin(student):
        abort(404)
    payload = request.get_json(silent=True) or {}
    msg = (payload.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "empty"}), 400
    socketio.emit("system_broadcast", {
        "message": msg,
        "from": "Admin",
        "timestamp": datetime.utcnow().isoformat(),
    }, broadcast=True)
    return jsonify({"ok": True, "sent_to": "all rooms"})


@app.route("/admin-master/grant-admin", methods=["POST"])
def admin_grant():
    student = current_student()
    if not _is_admin(student):
        abort(404)
    payload = request.get_json(silent=True) or {}
    uid = payload.get("user_id")
    target = db.session.get(Student, uid) if uid else None
    if not target:
        return jsonify({"error": "user not found"}), 404
    target.is_admin = 1 if not target.is_admin else 0
    db.session.commit()
    return jsonify({"ok": True, "is_admin": bool(target.is_admin), "username": target.username})


# ─── Logout ───────────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    flash(t("success_logout"), "success")
    return redirect(url_for("index"))


# ─── Global error handlers (graceful "Setup Required" instead of crashes) ────
def _audit_missing_secrets() -> list[str]:
    """Return a friendly list of secrets that look unset, for the error page."""
    candidates = {
        "SESSION_SECRET":              "Flask session encryption",
        "GOOGLE_OAUTH_CLIENT_ID":      "Google login",
        "GOOGLE_OAUTH_CLIENT_SECRET":  "Google login",
        "GEMINI_API_KEY":              "AI Mentor (Gemini)",
        "HUGGINGFACE_API_TOKEN":       "AI fallback",
        "SMTP_HOST":                   "Email verification",
        "SMTP_USER":                   "Email verification",
        "SMTP_PASSWORD":               "Email verification",
        "CLOUDINARY_CLOUD_NAME":       "Avatar storage",
        "CLOUDINARY_API_KEY":          "Avatar storage",
        "CLOUDINARY_API_SECRET":       "Avatar storage",
        "FIREBASE_STORAGE_BUCKET":     "Video storage",
        "FIREBASE_SERVICE_ACCOUNT_JSON": "Video storage",
    }
    return [k for k in candidates if not os.environ.get(k, "").strip()]


@app.errorhandler(404)
def _err_404(_e):
    return render_template(
        "error.html",
        badge="404",
        title="Page not found",
        message="The page you’re looking for doesn’t exist or has been moved.",
        show_retry=False,
    ), 404


@app.errorhandler(500)
@app.errorhandler(Exception)
def _err_500(e):
    # Let Werkzeug handle HTTP errors that already have a status code (e.g. 401, 403)
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException) and e.code and e.code != 500:
        return e
    print(f"[error-handler] Unhandled exception: {e}", flush=True)
    missing = _audit_missing_secrets()
    return render_template(
        "error.html",
        badge="Setup Required" if missing else "Service Unavailable",
        title="Something went wrong on the server",
        message=("This feature needs a secret that isn’t set yet. "
                 "Add the missing keys below in Replit → Tools → Secrets, "
                 "then refresh."),
        missing_keys=missing,
        show_retry=True,
    ), 500


# ─── Startup secrets audit (prints a clear status report on boot) ─────────────
def _print_startup_audit() -> None:
    """Print a friendly checklist of every secret the app looks at."""
    checks = [
        ("SESSION_SECRET",                 "Session encryption",       True),
        ("GOOGLE_OAUTH_CLIENT_ID",         "Google login",             False),
        ("GOOGLE_OAUTH_CLIENT_SECRET",     "Google login",             False),
        ("GEMINI_API_KEY",                 "AI Mentor (Gemini)",       False),
        ("GEMINI_API_KEY_2",               "AI Mentor backup #2",      False),
        ("GEMINI_API_KEY_3",               "AI Mentor backup #3",      False),
        ("HUGGINGFACE_API_TOKEN",          "AI fallback (HuggingFace)", False),
        ("SMTP_HOST",                      "Email (SMTP host)",        False),
        ("SMTP_USER",                      "Email (SMTP user)",        False),
        ("SMTP_PASSWORD",                  "Email (SMTP password)",    False),
        ("CLOUDINARY_CLOUD_NAME",          "Avatar storage",           False),
        ("CLOUDINARY_API_KEY",             "Avatar storage",           False),
        ("CLOUDINARY_API_SECRET",          "Avatar storage",           False),
        ("FIREBASE_STORAGE_BUCKET",        "Video storage",            False),
        ("FIREBASE_SERVICE_ACCOUNT_JSON",  "Video storage",            False),
        ("YOUTUBE_API_KEY",                "YouTube search (optional)", False),
        ("ADMIN_EMAIL",                    "Admin panel access",       False),
    ]
    print("\n" + "═" * 60, flush=True)
    print("  SSAS — Startup Secrets Audit", flush=True)
    print("═" * 60, flush=True)
    for key, purpose, required in checks:
        present = bool(os.environ.get(key, "").strip())
        if present:
            mark = "✅"
            status = "Detected"
        else:
            mark = "❌" if required else "⚠️ "
            status = "MISSING (required)" if required else "not set (feature disabled)"
        print(f"  {mark}  {key:<32} {status:<28} — {purpose}", flush=True)
    print("═" * 60, flush=True)
    # Friendly grouped summaries
    google_ok = all(os.environ.get(k) for k in ("GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET"))
    smtp_ok   = all(os.environ.get(k) for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"))
    gemini_ok = any(os.environ.get(k) for k in ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"))
    cloud_ok  = all(os.environ.get(k) for k in ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"))
    fire_ok   = all(os.environ.get(k) for k in ("FIREBASE_STORAGE_BUCKET", "FIREBASE_SERVICE_ACCOUNT_JSON"))
    hf_ok     = bool(os.environ.get("HUGGINGFACE_API_TOKEN"))
    print(f"  {'✅' if google_ok else '⚠️ '} System Ready: Google OAuth      {'Detected' if google_ok else 'not configured'}", flush=True)
    print(f"  {'✅' if smtp_ok   else '⚠️ '} System Ready: SMTP Email        {'Detected' if smtp_ok   else 'not configured'}", flush=True)
    print(f"  {'✅' if gemini_ok else '⚠️ '} System Ready: Gemini AI         {'Detected' if gemini_ok else 'not configured'}", flush=True)
    print(f"  {'✅' if hf_ok     else '⚠️ '} System Ready: HF Token          {'Detected' if hf_ok     else 'not configured'}", flush=True)
    print(f"  {'✅' if cloud_ok  else '⚠️ '} System Ready: Cloudinary        {'Detected' if cloud_ok  else 'not configured (using local storage)'}", flush=True)
    print(f"  {'✅' if fire_ok   else '⚠️ '} System Ready: Firebase Storage  {'Detected' if fire_ok   else 'not configured (using local storage)'}", flush=True)
    print("═" * 60 + "\n", flush=True)


# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    with app.app_context():
        _ensure_schema()
    _print_startup_audit()
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "5000")),
                 debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
