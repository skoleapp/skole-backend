import os
import re
import sys
from datetime import timedelta
from pathlib import Path

import dj_database_url
import requests

from skole.utils.constants import Languages

# General Django settings
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
DEBUG = bool(int(os.environ.get("DEBUG", default=0)))
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", default="").split()
SECRET_KEY = os.environ.get("SECRET_KEY")
SITE_ID = int(os.environ.get("SITE_ID", default=1))
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
AUTH_USER_MODEL = "skole.User"

# This is used to allow AWS ELB health checks access the backend.
# Source: https://gist.github.com/dryan/8271687
try:
    ALLOWED_HOSTS.append(
        requests.get(
            "http://169.254.169.254/latest/meta-data/local-ipv4", timeout=0.01
        ).text
    )
except requests.exceptions.RequestException:
    # We were not in an EC2 instance, no need to do anything.
    pass


# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGIN_REGEXES = os.environ.get(
    "CORS_ALLOWED_ORIGIN_REGEXES", default=""
).split()
CORS_ALLOW_ALL_ORIGINS = DEBUG

# Static and media settings
MEDIA_ROOT = "media"
STATIC_ROOT = "static"
MEDIA_URL = "/media/"
STATIC_URL = "/static/"

# Database settings
DATABASES = {"default": dj_database_url.config()}

# Installed app settings
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "corsheaders",
    "graphene_django",
    "graphql_jwt.refresh_token",
    "imagekit",
    "django_s3_storage",
    "parler",
    "fcm_django",
    "skole",
]

# Middleware settings
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "skole.middleware.SkoleSessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Password validator settings
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {
            "user_attributes": ("username", "email"),
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 10,
        },
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Custom validation settings
USERNAME_MIN_LENGTH = 3
# Make sure to edit `constants.ValidationErrors.INVALID_USERNAME` if you change this.
USERNAME_REGEX = re.compile(r"^[A-Za-z0-9ÅÄÖåäö_]+$")

# Authentication backend settings
AUTHENTICATION_BACKENDS = [
    "skole.backends.SkoleJSONWebTokenBackend",
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
LOCALE_PATHS = [BASE_DIR / "skole/locale"]

# Parler settings
PARLER_LANGUAGES = {SITE_ID: ({"code": "en"}, {"code": "fi"}, {"code": "sv"})}

# Autoslug
AUTOSLUG_SLUGIFY_FUNCTION = "skole.utils.misc.slugify"

# Graphene settings
GRAPHENE = {
    "SCHEMA": "skole.schema.schema",
    "SCHEMA_OUTPUT": "schema.graphql",
    "MIDDLEWARE": [
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
        *(["skole.middleware.DisableIntrospectionMiddleware"] if not DEBUG else []),
    ],
}

# GraphQL JWT settings
GRAPHQL_JWT = {
    "JWT_COOKIE_SAMESITE": "Lax",  # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite
    "JWT_COOKIE_SECURE": not DEBUG,
    "JWT_VERIFY_EXPIRATION": not DEBUG,
    # FIXME: change this to e.g. minutes=15 when the token refreshing works.
    "JWT_EXPIRATION_DELTA": timedelta(days=60),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=60),
}

# Custom GraphQL JWT settings
EXPIRATION_VERIFICATION_TOKEN = timedelta(days=7)
EXPIRATION_PASSWORD_RESET_TOKEN = timedelta(hours=1)

# Cloudmersive settings
CLOUDMERSIVE_API_KEY = os.environ.get("CLOUDMERSIVE_API_KEY")

# Template settings
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "skole/templates"],
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

if not DEBUG:  # pragma: no cover
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
if not DEBUG:  # pragma: no cover
    EMAIL_BACKEND = "django_amazon_ses.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# FCM settings
FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": os.environ.get("FCM_SERVER_KEY"),
    "DELETE_INACTIVE_USERS": True,
}

# Custom email settings
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", default="hello@test.com")
EMAIL_CONTACT_FORM_SENDER = os.environ.get(
    "EMAIL_CONTACT_FORM_SENDER", default="Contact Form <contact-form@test.com>"
)

# Have to match with frontend.
VERIFICATION_PATH_ON_EMAIL = "verify-account"
PASSWORD_RESET_PATH_ON_EMAIL = "reset-password"
ACCOUNT_SETTINGS_PATH_ON_EMAIL = "account-settings"
COURSE_COMMENT_PATH_ON_EMAIL = "courses/{}?comment={}"
RESOURCE_COMMENT_PATH_ON_EMAIL = "resources/{}?comment={}"
SCHOOL_COMMENT_PATH_ON_EMAIL = "schools/{}?comment={}"
USER_PROFILE_PATH_ON_EMAIL = "users/{}"

# Maximum amount of results for autocomplete queries.
AUTOCOMPLETE_MAX_RESULTS = 50

# Amount of results that are returned for paginated queries by default.
DEFAULT_PAGE_SIZE = 10

# Amount of results shown in the activity preview menu.
ACTIVITY_PREVIEW_COUNT = 10

# Maximum file sizes for uploaded files in megabytes (MB).
RESOURCE_FILE_MAX_SIZE = 10
COMMENT_ATTACHMENT_MAX_SIZE = 3.5
USER_AVATAR_MAX_SIZE = 3.5

# Allowed filetypes for all media fields as (mimetype, human_friendly_name) pairs.
RESOURCE_FILE_ALLOWED_FILETYPES = [("application/pdf", "PDF")]
COMMENT_ATTACHMENT_ALLOWED_FILETYPES = [("image/jpeg", "JPEG"), ("image/png", "PNG")]
USER_AVATAR_ALLOWED_FILETYPES = [("image/jpeg", "JPEG"), ("image/png", "PNG")]

# How often the GDPR `myData` query is allowed for each user.
# Shorter rate limiting in dev env for increased convenience.
MY_DATA_RATE_LIMIT = timedelta(seconds=5) if DEBUG else timedelta(minutes=10)

# How long the `myData` file is available for download.
# TODO: add a management command that runs in the background
#   and deletes all generated `myData` files older than 7 days.
MY_DATA_FILE_AVAILABLE_FOR = timedelta(days=7)

# Both values below are divisible by three so we can include the same amount of courses, resources and comments in the suggestions.

# Amount of results returned by the trending comments query.
TRENDING_COMMENTS_COUNT = 6

# Amount of results returned by discussion suggestions.
DISCUSSION_SUGGESTIONS_COUNT = 6

# Detect if running tests.
TESTING = sys.argv[1:2] == ["test"]

REFERRAL_CODE_LENGTH = 7
REFERRAL_CODE_INITIAL_USAGES = 2
