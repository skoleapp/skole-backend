import datetime
import os

import dj_database_url  # type: ignore [import]

# Django settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = int(os.environ.get("DEBUG", default=0))
SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", default="").split()
DATABASES = {"default": dj_database_url.config()}
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
AUTH_USER_MODEL = "core.User"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

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

AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"level": "DEBUG", "class": "logging.StreamHandler"}},
    "loggers": {"django": {"level": "DEBUG", "handlers": ["console"]}},
}

# Localization settings

TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [("en", "English"), ("fi", "Finnish"), ("sv", "Swedish")]
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

# CORS settings

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = os.environ.get("CORS_ORIGIN_WHITELIST", default="").split()

# GraphQL settings

GRAPHENE = {
    "SCHEMA": "api.schemas.schema.schema",
    "MIDDLEWARE": ["graphql_jwt.middleware.JSONWebTokenMiddleware",],
}

GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": False,
    "JWT_EXPIRATION_DELTA": datetime.timedelta(hours=24),
}

# Static file settings

if DEBUG:
    MEDIA_ROOT = "media"
    STATIC_ROOT = "static"
    MEDIA_URL = "/media/"
    STATIC_URL = "/static/"

else:
    AWS_S3_KEY_PREFIX_STATIC = "static"
    AWS_S3_KEY_PREFIX = "media"
    AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")
    AWS_S3_BUCKET_NAME_STATIC = AWS_S3_BUCKET_NAME

    STATIC_URL = f"{AWS_S3_BUCKET_NAME}.s3.amazonaws.com/{AWS_S3_KEY_PREFIX_STATIC}/"
    MEDIA_URL = f"{AWS_S3_BUCKET_NAME}.s3.amazonaws.com/{AWS_S3_KEY_PREFIX}/"

    AWS_REGION = os.environ.get("AWS_REGION")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

    DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"
    STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"

# Custom settings

PASSWORD_MIN_LENGTH = 6
EMAIL_URL = os.environ.get("EMAIL_URL", default="")
