FROM python:3.9.4-slim-buster@sha256:6fd99c1c6bac8abf9952cb797dc409ac92e8fbedd4d080211381a69c213b509b as base

RUN apt-get update \
    && apt-get install --no-install-recommends --assume-yes \
        ghostscript \
        gir1.2-gdkpixbuf-2.0 \
        gir1.2-poppler-0.18 \
        gir1.2-rsvg-2.0 \
        imagemagick \
        libcairo2-dev \
        libgirepository1.0-dev \
        libmagic-dev \
        libimage-exiftool-perl \
        libpq-dev \
        postgresql-client \
        python3-gi-cairo \
        python3-mutagen \
    && rm -rf /var/lib/apt/lists/ /var/cache/apt/

# Allow ImageMagick to convert PDFs: https://stackoverflow.com/q/52998331/9835872
RUN sed --in-place '/rights="none" pattern="PDF"/d' /etc/ImageMagick-6/policy.xml

RUN groupadd --gid=10001 user \
    && useradd --gid=user --uid=10000 --create-home user
WORKDIR /home/user/app
RUN chown user:user /home/user/app

ENV PATH="/home/user/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1


FROM base as build-deps

RUN apt-get update \
    && apt-get install --no-install-recommends --assume-yes \
        curl \
        gcc \
        gettext \
    && rm -rf /var/lib/apt/lists/ /var/cache/apt/

ENV POETRY_VIRTUALENVS_CREATE=0
ENV POETRY_VERSION=1.1.6


FROM build-deps as dev

WORKDIR /app

ENV PATH="/root/.poetry/bin:${PATH}"

RUN curl --silent --show-error \
        https://raw.githubusercontent.com/python-poetry/poetry/7360b09e4ba3c01e1d5dc6eaaf34cb3ff57bc16e/get-poetry.py \
        | python - --no-modify-path \
    && find /root/.poetry/lib/poetry/_vendor/ -mindepth 1 -maxdepth 1 -not -name py3.9 -type d | xargs rm -rf

COPY poetry.lock .
COPY pyproject.toml .

RUN poetry install --no-root \
    && rm -rf /root/.cache/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM dev AS ci

COPY . .

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


FROM build-deps as build

USER user

ENV PATH="/home/user/.poetry/bin:${PATH}"

RUN curl --silent --show-error \
        https://raw.githubusercontent.com/python-poetry/poetry/7360b09e4ba3c01e1d5dc6eaaf34cb3ff57bc16e/get-poetry.py \
        | python - --no-modify-path \
    && find /home/user/.poetry/lib/poetry/_vendor/ -mindepth 1 -maxdepth 1 -not -name py3.9 -type d | xargs rm -rf

COPY --chown=user:user poetry.lock .
COPY --chown=user:user pyproject.toml .

RUN poetry install --no-root --no-dev \
    && rm -rf /home/user/.cache/

COPY --chown=user:user . .

RUN django-admin compilemessages
RUN poetry build --format=wheel
RUN pip install --disable-pip-version-check dist/*.whl


FROM base as prod

USER user

ENV PYTHONOPTIMIZE=1

# The production app needs exactly these and nothing more.
COPY --from=build --chown=user:user /home/user/.local /home/user/.local/
COPY --from=build --chown=user:user /home/user/app/config config/
COPY --from=build --chown=user:user /home/user/app/manage.py manage.py

CMD python manage.py collectstatic --noinput \
    && python manage.py migrate \
    && python manage.py loaddata /home/user/.local/lib/python*/site-packages/skole/fixtures/initial*yaml \
    && python manage.py award_badges \
    && gunicorn --config=config/gunicorn_conf.py config.wsgi
