FROM python:3.8.3-alpine3.11 AS dev

RUN adduser --disabled-password user
WORKDIR /home/user/app
RUN chown -R user:user /home/user/app

ENV PATH="/home/user/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apk add --update-cache --no-cache postgresql-client gettext jpeg-dev libmagic

COPY --chown=user:user requirements.txt .
COPY --chown=user:user requirements-dev.txt .

RUN apk add --update-cache --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev \
    && su user -c 'pip install --user --no-cache-dir --upgrade pip' \
    && su user -c 'pip install --user --no-cache-dir -r requirements.txt -r requirements-dev.txt' \
    && apk del .tmp-build-deps

USER user

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM dev AS circleci

COPY --chown=user:user . .

CMD autoflake --check --recursive --remove-all-unused-imports --ignore-init-module-imports . > /dev/null \
        || { echo 'autoflake found unused imports!'; exit 1; } \
    && isort --check --recursive . \
    && black --check --diff --exclude migrations/.* . \
    && docformatter --check --recursive --wrap-summaries 88 --wrap-descriptions 88 . \
    && mypy . \
    && pytest --verbose --cov-report=html --cov=. skole/tests
