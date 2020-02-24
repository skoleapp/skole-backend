import datetime
import os

import dj_database_url  # type: ignore [import]
from django.utils.translation import gettext_lazy as _

DEBUG = os.environ.get("DEBUG")
SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASES = {"default": dj_database_url.config()}
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
AUTH_USER_MODEL = "core.User"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
PASSWORD_MIN_LENGTH = 6
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", default="*").split()
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = ("http://localhost:3001",)
AWS_S3_BUCKET_NAME_STATIC = os.environ.get("AWS_S3_BUCKET_NAME_STATIC")
MEDIA_URL = os.environ.get("MEDIA_URL", default="/media/")
STATIC_URL = os.environ.get("STATIC_URL", default="/static/")
MEDIA_ROOT = "media"
STATIC_ROOT = "static"
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

if DEBUG is False:
    STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"

LANGUAGES = [("en", _("English")), ("fi", _("Finnish")), ("sv", _("Swedish"))]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "corsheaders",
    "graphene_django",
    "imagekit",
    "django_s3_storage",
    "core",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
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

GRAPHENE = {
    "SCHEMA": "api.schemas.schema.schema",
    "MIDDLEWARE": ["graphql_jwt.middleware.JSONWebTokenMiddleware",],
}

AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": False,
    "JWT_EXPIRATION_DELTA": datetime.timedelta(hours=24),
}
