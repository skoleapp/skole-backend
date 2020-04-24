import os
import urllib.error
import urllib.request
from datetime import timedelta

import dj_database_url

# We use this instead of the real gettext to avoid a circular import
# https://django-book.readthedocs.io/en/latest/chapter19.html
_ = lambda s: s

# Django settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = int(os.environ.get("DEBUG", default=0))
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", default="").split()
SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASES = {"default": dj_database_url.config()}
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
AUTH_USER_MODEL = "core.User"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
MEDIA_ROOT = "media"
STATIC_ROOT = "static"
MEDIA_URL = "media/"
STATIC_URL = "/static/"
SITE_ID = 1

# This is used to allow AWS ELB health checks access the backend.
# https://gist.github.com/dryan/8271687
try:
    ALLOWED_HOSTS.append(
        urllib.request.urlopen(
            "http://169.254.169.254/latest/meta-data/local-ipv4", timeout=0.01
        )
        .read()
        .decode("utf-8")
    )
except urllib.error.URLError:
    # We were not in an EC2 instance.
    pass

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "corsheaders",
    "graphene_django",
    "imagekit",
    "django_s3_storage",
    "parler",
    "graphql_auth",
    "django_filters",
    "core",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

AUTHENTICATION_BACKENDS = [
    "graphql_auth.backends.GraphQLAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"level": "INFO", "class": "logging.StreamHandler"}},
    "loggers": {"django": {"level": "INFO", "handlers": ["console"]}},
}

# Localization settings

TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGE_CODE = "en"
LANGUAGES = (("en", _("English")), ("fi", _("Finnish")), ("sv", _("Swedish")))
LOCALE_PATHS = (os.path.join(BASE_DIR, "core/locale"),)

# CORS settings

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = os.environ.get("CORS_ORIGIN_WHITELIST", default="").split()
CORS_ORIGIN_ALLOW_ALL = bool(DEBUG)

# GraphQL settings

GRAPHENE = {
    "SCHEMA": "api.schemas.schema.schema",
    "SCHEMA_OUTPUT": "schema.graphql",
    "MIDDLEWARE": ["graphql_jwt.middleware.JSONWebTokenMiddleware",],
}

GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": not DEBUG,
    "JWT_EXPIRATION_DELTA": timedelta(days=7),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=60),
}

GRAPHQL_AUTH = {
    "EXPIRATION_ACTIVATION_TOKEN": timedelta(days=7),
    "EXPIRATION_PASSWORD_RESET_TOKEN": timedelta(hours=1),
    "EXPIRATION_SECONDARY_EMAIL_ACTIVATION_TOKEN": timedelta(hours=1),
    "EMAIL_FROM": os.environ.get(
        "DEFAULT_FROM_EMAIL", ""
    ),  # FIXME: This is not working for some reason.
    "ACTIVATION_PATH_ON_EMAIL": "account/verify",
    "PASSWORD_RESET_PATH_ON_EMAIL": "account/reset-password",
    "EMAIL_SUBJECT_ACTIVATION": "email/verify-account-subject.txt",
    "EMAIL_SUBJECT_ACTIVATION_RESEND": "email/verify-account-subject.txt",
    "EMAIL_SUBJECT_PASSWORD_RESET": "email/reset-password-subject.txt",
    "EMAIL_TEMPLATE_ACTIVATION": "email/verify-account-email.html",
    "EMAIL_TEMPLATE_ACTIVATION_RESEND": "email/verify-account-email.html",
    "EMAIL_TEMPLATE_PASSWORD_RESET": "email/reset-password-email.html",
}

# Templates

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
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

# S3 storage settings

if not DEBUG:
    AWS_S3_KEY_PREFIX = "media"
    AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")
    AWS_S3_BUCKET_AUTH = True

    AWS_S3_KEY_PREFIX_STATIC = "static"
    AWS_S3_BUCKET_NAME_STATIC = os.environ.get("AWS_S3_BUCKET_NAME_STATIC")
    AWS_S3_BUCKET_AUTH_STATIC = True

    AWS_S3_MAX_AGE_SECONDS = 1800

    AWS_REGION = os.environ.get("AWS_REGION")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

    DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"
    STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"

# Email settings

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", default="")

# Custom settings

PASSWORD_MIN_LENGTH = 6
USERNAME_MIN_LENGTH = 3
