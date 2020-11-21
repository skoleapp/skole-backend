FROM python:3.9.0-alpine3.12 AS dev

RUN adduser --disabled-password user
WORKDIR /home/user/app
RUN chown user:user /home/user/app

ENV PATH="/home/user/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

# This helps debug misbehaving async code.
# It's unset in the prod layer.
ENV PYTHONTRACEMALLOC=1

# When building the non-production image this will specified to be `requirements-dev.txt`,
# so that that file gets copied also. When the value is not specified for the prod image
# the default value of it just copies the normal requirements file again.
ARG dev_requirements=requirements.txt

COPY --chown=user:user requirements.txt .
COPY --chown=user:user ${dev_requirements} .

RUN apk update \
    && apk add \
        cairo-dev \
        exiftool \
        gettext \
        gdk-pixbuf-dev \
        gobject-introspection-dev \
        jpeg-dev \
        libmagic \
        librsvg-dev \
        poppler-dev \
        postgresql-client \
    && apk add --virtual=/tmp/build_deps \
        gcc \
        musl-dev \
        postgresql-dev \
        zlib-dev \
    && su user -c 'pip install --user --no-cache-dir --disable-pip-version-check pip==20.2.4' \
    && su user -c "pip install --user --no-cache-dir -r requirements.txt $([ -f requirements-dev.txt ] && echo '-r requirements-dev.txt')" \
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
    && pylint --jobs=0 *.py config/ skole/ \
    && mypy . \
    && pytest --verbose --cov-report=xml --cov=. . \
    && python manage.py compilemessages \
    && python manage.py collectstatic --noinput \
    && python manage.py migrate \
    && python manage.py loaddata skole/fixtures/initial*yaml \
    && gunicorn --check-config --config=config/gunicorn_conf.py config.wsgi


FROM circleci as prod

# Has to be set to an empty string for it to have no effect.
ENV PYTHONTRACEMALLOC=

ENV PYTHONOPTIMIZE=1

CMD python manage.py compilemessages \
    && python manage.py collectstatic --noinput \
    && python manage.py migrate \
    && gunicorn --config=config/gunicorn_conf.py config.wsgi
