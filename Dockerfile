FROM python:3.9.1-slim-buster AS dev

RUN groupadd --gid=10001 user \
    && useradd --gid=user --uid=10000 --create-home user
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

RUN apt-get update \
    && apt-get install --no-install-recommends --assume-yes \
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
        python3-gi-cairo \
        python3-mutagen \
    && su user --command='pip install --user --no-cache-dir --disable-pip-version-check pip==20.3.1' \
    && su user --command="pip install --user --no-cache-dir -r requirements.txt $([ -f requirements-dev.txt ] && echo '-r requirements-dev.txt')"

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
    && pylint *.py config/ skole/ \
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
