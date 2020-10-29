FROM python:3.9.0-alpine3.12 AS dev

RUN adduser --disabled-password user
WORKDIR /home/user/app
RUN chown user:user /home/user/app

ENV PATH="/home/user/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONTRACEMALLOC=1

COPY --chown=user:user requirements.txt .
COPY --chown=user:user requirements-dev.txt .

RUN apk update \
    && apk add cairo-dev exiftool gettext gdk-pixbuf-dev gobject-introspection-dev jpeg-dev libmagic librsvg-dev poppler-dev postgresql-client \
    && apk add --virtual=/tmp/build_deps gcc musl-dev postgresql-dev zlib-dev \
    && su user -c 'pip install --user --no-cache-dir --disable-pip-version-check pip==20.2.4' \
    && su user -c 'pip install --user --no-cache-dir -r requirements.txt -r requirements-dev.txt' \
    && apk del /tmp/build_deps && rm -rf /var/cache/apk/*

USER user

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM dev AS circleci

COPY --chown=user:user . .

CMD python manage.py graphql_schema --out=/tmp/compare.graphql && diff schema.graphql /tmp/compare.graphql \
    && ./.circleci/check_makemessages.sh \
    && python manage.py makemigrations --check \
    && isort --check-only --diff . \
    && docformatter --check --recursive --wrap-summaries=88 --wrap-descriptions=88 --pre-summary-newline . \
    && black --check --diff . \
    && flake8 . \
    && mypy . \
    && pytest --verbose --cov-report=xml --cov=. . \
    && python manage.py compilemessages \
    && python manage.py collectstatic --noinput \
    && python manage.py migrate \
    && python manage.py loaddata skole/fixtures/initial*yaml \
    && gunicorn --check-config --config=config/gunicorn_conf.py config.wsgi
