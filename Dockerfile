FROM python:3.9.4-slim-buster@sha256:de9482638c1354f5178efc90431de2a42e863a12bf3df41d7fa30d5c10fe543d as base

RUN apt-get update \
    && apt-get install --no-install-recommends --assume-yes \
        gir1.2-gdkpixbuf-2.0 \
        gir1.2-poppler-0.18 \
        gir1.2-rsvg-2.0 \
        libcairo2-dev \
        libgirepository1.0-dev \
        libmagic-dev \
        libimage-exiftool-perl \
        libpq-dev \
        postgresql-client \
        python3-gi-cairo \
        python3-mutagen \
    && rm -rf /var/lib/apt/lists/ /var/cache/apt/

RUN groupadd --gid=10001 user \
    && useradd --gid=user --uid=10000 --create-home user
WORKDIR /home/user/app
RUN chown user:user /home/user/app

ENV PATH="/home/user/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1


FROM base as dev

# The size of this layer doesn't really matter since it won't exist in production.

RUN apt-get update \
    && apt-get install --no-install-recommends --assume-yes \
        curl \
        gcc \
        gettext

USER user

ENV PATH="/home/user/.poetry/bin:${PATH}"
ENV POETRY_VIRTUALENVS_CREATE=0
ENV POETRY_VERSION=1.1.6

RUN curl --silent --show-error \
    https://raw.githubusercontent.com/python-poetry/poetry/7360b09e4ba3c01e1d5dc6eaaf34cb3ff57bc16e/get-poetry.py \
    | python - --no-modify-path

COPY --chown=user:user poetry.lock .
COPY --chown=user:user pyproject.toml .

ARG install_dev_dependencies=0

RUN sh -c "poetry install --no-root "$([ "$install_dev_dependencies" -eq 0 ] && printf -- '--no-dev')""

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM dev AS ci

COPY --chown=user:user . .

CMD python manage.py graphql_schema --out=/tmp/compare.graphql && diff schema.graphql /tmp/compare.graphql \
    && ./.github/check_makemessages.sh \
    && python manage.py makemigrations --check \
    && isort --check-only --diff . \
    && docformatter --check --recursive --wrap-summaries=88 --wrap-descriptions=88 --pre-summary-newline . \
    && black --check --diff . \
    && flake8 . \
    && pylint *.py config/ skole/ \
    && mypy . \
    && pytest --verbose --cov-report=xml --cov=. . \
    && python manage.py compilemessages \
    && python manage.py collectstatic --noinput \
    && python manage.py migrate \
    && python manage.py loaddata skole/fixtures/initial*yaml \
    && gunicorn --check-config --config=config/gunicorn_conf.py config.wsgi


FROM ci as build

RUN django-admin compilemessages
RUN poetry build --format=wheel
RUN pip install --disable-pip-version-check dist/*.whl


FROM base as prod

USER user

ENV PYTHONOPTIMIZE=1

# We only need these and nothing more.
COPY --chown=user:user --from=build /home/user/.local /home/user/.local/
COPY --chown=user:user config config/
COPY --chown=user:user manage.py .

CMD python manage.py collectstatic --noinput \
    && python manage.py migrate \
    && python manage.py loaddata /home/user/.local/lib/python*/site-packages/skole/fixtures/initial*yaml \
    && python manage.py award_badges \
    && gunicorn --config=config/gunicorn_conf.py config.wsgi
