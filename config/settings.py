import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# declare *all* env vars you’ll read
env = environ.Env(
    DEBUG                = (bool, False),
    SECRET_KEY           = (str, ""),
    ALLOWED_HOSTS        = (list, []),
    DATABASE_URL         = (str, "sqlite:///db.sqlite3"),

    RABBITMQ_URL         = (str, ""),

    # OIDC
    OIDC_OP_ISSUER       = (str, ""),
    OIDC_RP_CLIENT_ID    = (str, ""),
    OIDC_RP_CLIENT_SECRET= (str, ""),

    # Africa’s Talking
    AFRICAS_TALKING_API_KEY  = (str, ""),
    AFRICAS_TALKING_USERNAME = (str, ""),

    # SMTP / Gmail
    EMAIL_BACKEND        = (str, "django.core.mail.backends.smtp.EmailBackend"),
    EMAIL_HOST           = (str, ""),
    EMAIL_PORT           = (int, 587),
    EMAIL_USE_TLS        = (bool, True),
    EMAIL_HOST_USER      = (str, ""),
    EMAIL_HOST_PASSWORD  = (str, ""),
    DEFAULT_FROM_EMAIL   = (str, ""),
    ADMIN_EMAIL          = (str, ""),
)

# read .env
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Core
SECRET_KEY    = env("SECRET_KEY")
DEBUG         = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INSTALLED_APPS = [
    # django…
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third-party
    "rest_framework",
    "corsheaders",
    "mptt",
    "oidc_auth",

    # local
    "accounts",
    "catalog",
    "orders",
    "notifications",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


TEMPLATES = [
    {
        # This is the built-in Django template engine
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # Add any filesystem dirs you want for project-level templates
        "DIRS": [],

        # Automatically look for templates in each app/templates/ subdir
        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                # debug context processor (optional but recommended in dev)
                "django.template.context_processors.debug",

                # make `request` available in templates (required by admin)
                "django.template.context_processors.request",

                # auth & messages
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Database
DATABASES = {"default": env.db()}

# Auth & OIDC
AUTH_USER_MODEL = "accounts.Customer"
OIDC_OP_ISSUER        = env("OIDC_OP_ISSUER")
OIDC_RP_CLIENT_ID     = env("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = env("OIDC_RP_CLIENT_SECRET")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # will be overridden in DEBUG below
        "accounts.authentication.CustomOIDCBearerAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "EXCEPTION_HANDLER": "config.exceptions.custom_exception_handler",
}

if DEBUG:
    # For tests & local dev: use BasicAuth + SessionAuth
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ]


# CORS
CORS_ALLOW_ALL_ORIGINS = True

# I18n / Timezone
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "UTC"
USE_I18N      = True
USE_TZ        = True

# #----------------------ADDED for openshift-------------------------
# # Tell Django we are behind a TLS-terminating proxy
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# # Only send CSRF & session cookies over HTTPS
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE    = True

# # Your OpenShift Route host must be trusted
# CSRF_TRUSTED_ORIGINS = env(
#     "CSRF_TRUSTED_ORIGINS",
#     cast=list,
#     default=[
#         "https://si-api-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com"
#     ]
# )
#--------------------------------------------------------------------------

# Static
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Use WhiteNoise’s compressed manifest storage so file names change when contents change
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Email via Gmail SMTP
EMAIL_BACKEND       = env("EMAIL_BACKEND")
EMAIL_HOST          = env("EMAIL_HOST")
EMAIL_PORT          = env("EMAIL_PORT")
EMAIL_USE_TLS       = env("EMAIL_USE_TLS")
EMAIL_HOST_USER     = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL  = env("DEFAULT_FROM_EMAIL")
ADMIN_EMAIL         = env("ADMIN_EMAIL")

# RabbitMQ
RABBITMQ_URL = env("RABBITMQ_URL")

# Africa’s Talking
AFRICAS_TALKING_API_KEY   = env("AFRICAS_TALKING_API_KEY")
AFRICAS_TALKING_USERNAME  = env("AFRICAS_TALKING_USERNAME")

# Logging (JSON to console)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"json": {"()": "django.utils.log.ServerFormatter"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"