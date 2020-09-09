FROM python:3.8.5-alpine3.12 AS dev

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
    && apk add gettext jpeg-dev libmagic postgresql-client \
    && apk add --virtual=/tmp/build_deps gcc musl-dev postgresql-dev zlib-dev \
    && su user -c 'pip install --user --no-cache-dir --upgrade --disable-pip-version-check pip' \
    && su user -c 'pip install --user --no-cache-dir -r requirements.txt -r requirements-dev.txt' \
    && apk del /tmp/build_deps && rm -rf /var/cache/apk/*

USER user

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM dev AS circleci

COPY --chown=user:user . .

CMD { python manage.py graphql_schema --out=compare.graphql \
        && diff schema.graphql compare.graphql \
        && rm compare.graphql; } \
    && python manage.py makemigrations --check \
    && isort --check-only --diff . \
    && docformatter --check --recursive --wrap-summaries=88 --wrap-descriptions=88 . \
    && black --check --diff . \
    && flake8 . \
    && mypy . \
    && pytest --verbose --cov-report=html --cov=. . \
    && python manage.py compilemessages \
    && python manage.py migrate \
    && python manage.py loaddata \
        initial-activity-types.yaml \
        initial-badges.yaml \
        initial-beta-codes.yaml \
        initial-cities.yaml \
        initial-countries.yaml \
        initial-courses.yaml \
        initial-resource-types.yaml \
        initial-resources.yaml \
        initial-school-types.yaml \
        initial-schools.yaml \
        initial-subjects.yaml
