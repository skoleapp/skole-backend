FROM python:3.9.2-slim-buster@sha256:539ecc873369f39fca6edaf57c75a053d3533a01f837bfaee37de1b99545ecce AS dev

RUN groupadd --gid=10001 user \
    && useradd --gid=user --uid=10000 --create-home user
WORKDIR /home/user/app
RUN chown user:user /home/user/app

ENV PATH="/home/user/.poetry/bin:/home/user/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=0
ENV POETRY_VERSION=1.1.5

ARG install_dev_dependencies=0
ARG _poetry_url=https://raw.githubusercontent.com/python-poetry/poetry/7360b09e4ba3c01e1d5dc6eaaf34cb3ff57bc16e/get-poetry.py 

# Use the character class for conditional copying https://stackoverflow.com/a/46801962/9835872
COPY --chown=user:user poetry.loc[k] .
COPY --chown=user:user pyproject.toml .

RUN apt-get update \
    && apt-get install --no-install-recommends --assume-yes \
        curl \
        gcc \
        gettext \
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
    && su user --command="curl --silent --show-error \"${_poetry_url}\" | python - --no-modify-path" \
    && su user --command="poetry install --no-root "$([ "${install_dev_dependencies}" -eq 0 ] && printf -- '--no-dev')"" \
    && apt-get purge --auto-remove --assume-yes curl \
    && find /home/user/.poetry/lib/poetry/_vendor/ -mindepth 1 -maxdepth 1 -not -name py3.9 -type d | xargs rm -rf \
    && rm -rf /home/user/.cache/ /var/lib/apt/lists/ /var/cache/apt/

USER user

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


FROM ci as prod

ENV PYTHONOPTIMIZE=1

CMD python manage.py compilemessages \
    && python manage.py collectstatic --noinput \
    && python manage.py migrate \
    && python manage.py loaddata skole/fixtures/initial*yaml \
    && python manage.py award_badges \
    && gunicorn --config=config/gunicorn_conf.py config.wsgi
