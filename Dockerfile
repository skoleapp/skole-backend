FROM python:3.8.5-alpine3.12 AS dev

RUN adduser --disabled-password user
WORKDIR /home/user/app
RUN chown --recursive user:user /home/user/app

ENV PATH="/home/user/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apk add --update-cache --no-cache postgresql-client gettext jpeg-dev libmagic

COPY --chown=user:user requirements.txt .
COPY --chown=user:user requirements-dev.txt .

RUN apk add --update-cache --no-cache --virtual=.tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev \
    && su user -c 'pip install --user --no-cache-dir --upgrade pip' \
    && su user -c 'pip install --user --no-cache-dir -r requirements.txt -r requirements-dev.txt' \
    && apk del .tmp-build-deps

USER user

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM dev AS circleci

COPY --chown=user:user . .

CMD { python manage.py graphql_schema --out=compare.graphql \
        && diff schema.graphql compare.graphql \
        && rm compare.graphql; } \
    && isort --check-only --diff . \
    && docformatter --check --recursive --wrap-summaries=88 --wrap-descriptions=88 . \
    && black --check --diff . \
    && flake8 . \
    && mypy . \
    && pytest --verbose --cov-report=html --cov=. . \
    && python manage.py migrate \
    && python manage.py loaddata \
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
