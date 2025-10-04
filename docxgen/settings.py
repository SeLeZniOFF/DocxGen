from pathlib import Path
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# Вспомогательные функции
# -------------------------
def env_bool(*names: str, default: bool = False) -> bool:
    for n in names:
        v = os.getenv(n)
        if v is not None:
            return str(v).lower() in ("1", "true", "yes", "on")
    return default

def env_list(*names: str, default: str = "") -> list[str]:
    raw = None
    for n in names:
        v = os.getenv(n)
        if v:
            raw = v
            break
    if raw is None:
        raw = default
    return [x.strip() for x in raw.split(",") if x.strip()]

def parse_sqlite_url(url_str: str) -> str:
    """Поддержка sqlite:///relative.db и sqlite:////absolute/path.db"""
    u = urlparse(url_str)
    path = u.path or ""
    if os.path.isabs(path):
        return path
    return str((BASE_DIR / path.lstrip("/")).resolve())

# -------------------------
# Базовые настройки
# -------------------------
SECRET_KEY = (
    os.getenv("DJANGO_SECRET_KEY")
    or os.getenv("SECRET_KEY")
    or "dev-secret-key"
)

DEBUG = env_bool("DJANGO_DEBUG", "DEBUG", default=True)

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "ALLOWED_HOSTS", default="*")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "CSRF_TRUSTED_ORIGINS", default="")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "docxgen.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "docxgen.wsgi.application"

# -------------------------
# БД: SQLite по умолчанию.
# Можно задать:
#  1) DATABASE_URL=sqlite:///db.sqlite3 или sqlite:////abs/path.db
#  2) DB_ENGINE=sqlite + SQLITE_NAME=/путь/к/db.sqlite3
#  3) DATABASE_URL=postgres://...
# -------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
DB_ENGINE = os.getenv("DB_ENGINE", "").lower()

if DATABASE_URL:
    url = urlparse(DATABASE_URL)
    if url.scheme in ("sqlite", "sqlite3"):
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": parse_sqlite_url(DATABASE_URL),
            }
        }
    else:
        # postgres://user:pass@host:port/name
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": (url.path or "/")[1:],
                "USER": url.username,
                "PASSWORD": url.password,
                "HOST": url.hostname,
                "PORT": url.port or 5432,
            }
        }
elif DB_ENGINE == "sqlite":
    sqlite_name = os.getenv("SQLITE_NAME", str(BASE_DIR / "db.sqlite3"))
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": sqlite_name,
        }
    }
elif DB_ENGINE in ("postgres", "postgresql", "psql"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "docxgen"),
            "USER": os.getenv("DB_USER", "docxuser"),
            "PASSWORD": os.getenv("DB_PASS", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
else:
    # дефолт — локальный SQLite рядом с проектом
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }

# -------------------------
# Локаль/время
# -------------------------
LANGUAGE_CODE = "ru"
TIME_ZONE = os.getenv("TIME_ZONE", "Europe/Helsinki")
USE_I18N = True
USE_TZ = True

# -------------------------
# Статические и медиа
# (в Docker передаём через переменные, чтобы маппить на тома)
# -------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.getenv("STATIC_ROOT", str(BASE_DIR / "staticfiles"))

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", str(BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------
# DRF
# -------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# -------------------------
# За прокси (Nginx)
# -------------------------
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Включай при реальном HTTPS:
if env_bool("DJANGO_USE_HTTPS", "USE_HTTPS", default=False):
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
