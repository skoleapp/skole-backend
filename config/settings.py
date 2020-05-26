import os
import urllib.error
import urllib.request
from datetime import timedelta

import dj_database_url

from skole.utils.constants import Languages

# General Django settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = int(os.environ.get("DEBUG", default=0))
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", default="").split()
SECRET_KEY = os.environ.get("SECRET_KEY")
SITE_ID = os.environ.get("SITE_ID", default=1)
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
AUTH_USER_MODEL = "skole.User"

# This is used to allow AWS ELB health checks access the backend.
# Source: https://gist.github.com/dryan/8271687
try:
    ALLOWED_HOSTS.append(
        urllib.request.urlopen(
            "http://169.254.169.254/latest/meta-data/local-ipv4", timeout=0.01
        )
        .read()
        .decode("utf-8")
    )
except urllib.error.URLError:
    # We were not in an EC2 instance, no need to do anything.
    pass


# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = os.environ.get("CORS_ORIGIN_WHITELIST", default="").split()
CORS_ORIGIN_ALLOW_ALL = bool(DEBUG)

# Static and media settings
MEDIA_ROOT = "media"
STATIC_ROOT = "static"
MEDIA_URL = "media/"  # On purpose no prefix slash.
STATIC_URL = "/static/"  # On purpose prefix slash.

# Database settings
DATABASES = {"default": dj_database_url.config()}

# Installed app settings
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
    "graphql_jwt.refresh_token",
    "imagekit",
    "django_s3_storage",
    "parler",
    "skole",
]

# Middleware settings
MIDDLEWARE = [
    "skole.middleware.SkoleSessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

# Password validator settings
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Custom validation settings
PASSWORD_MIN_LENGTH = 6
USERNAME_MIN_LENGTH = 3

# Authentication backend settings
AUTHENTICATION_BACKENDS = [
    "skole.backends.SkoleAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Logging settings
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
LANGUAGES = (
    ("en", Languages.ENGLISH),
    ("fi", Languages.FINNISH),
    ("sv", Languages.SWEDISH),
)
LOCALE_PATHS = [os.path.join(BASE_DIR, "skole", "locale")]

# Parler settings
PARLER_LANGUAGES = {SITE_ID: ({"code": "en"}, {"code": "fi"}, {"code": "sv"})}

# Graphene settings
GRAPHENE = {
    "SCHEMA": "skole.schema.schema",
    "SCHEMA_OUTPUT": "schema.graphql",
    "MIDDLEWARE": ["graphql_jwt.middleware.JSONWebTokenMiddleware"],
}

# GraphQL JWT settings
GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": not DEBUG,
    "JWT_EXPIRATION_DELTA": timedelta(days=7),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=60),
}

# Custom GraphQL JWT settings
EXPIRATION_VERIFICATION_TOKEN = timedelta(days=7)
EXPIRATION_PASSWORD_RESET_TOKEN = timedelta(hours=1)

# Template settings
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "skole", "templates")],
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

if not DEBUG:
    # AWS credential settings
    AWS_REGION = os.environ.get("AWS_REGION")  # django-s3-storage uses this value.
    AWS_DEFAULT_REGION = AWS_REGION  # django-amazon-ses uses this value.
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

    # S3 storage settings
    AWS_S3_KEY_PREFIX = "media"
    AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")
    AWS_S3_BUCKET_AUTH = True
    AWS_S3_KEY_PREFIX_STATIC = "static"
    AWS_S3_BUCKET_NAME_STATIC = os.environ.get("AWS_S3_BUCKET_NAME_STATIC")
    AWS_S3_BUCKET_AUTH_STATIC = True
    AWS_S3_MAX_AGE_SECONDS = 1800
    DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"
    STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"

# Email settings
if not DEBUG:
    EMAIL_BACKEND = "django_amazon_ses.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", default="")

# Custom email settings
EMAIL_AUTH_FROM = os.environ.get("EMAIL_AUTH_FROM", default="")
EMAIL_CONTACT_FROM = os.environ.get("EMAIL_CONTACT_FROM", default="")
EMAIL_CONTACT_TO = os.environ.get("EMAIL_CONTACT_TO", default="")
VERIFICATION_PATH_ON_EMAIL = "account/verify-account"
PASSWORD_RESET_PATH_ON_EMAIL = "account/reset-password"
EMAIL_SUBJECT_VERIFICATION = "email/verify-account-subject.txt"
EMAIL_SUBJECT_PASSWORD_RESET = "email/reset-password-subject.txt"
EMAIL_SUBJECT_CONTACT = "email/contact-email-subject.txt"
EMAIL_TEMPLATE_PASSWORD_RESET = "email/reset-password-email.html"
EMAIL_TEMPLATE_VERIFICATION = "email/verify-account-email.html"
EMAIL_TEMPLATE_CONTACT = "email/contact-email.html"
