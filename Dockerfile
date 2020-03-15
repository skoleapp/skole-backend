FROM python:3.8.2-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /app

RUN mkdir /app
WORKDIR /app

RUN apk add --update --no-cache postgresql-client gettext jpeg-dev libmagic
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

COPY requirements.txt .
COPY requirements-dev.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt -r requirements-dev.txt
RUN apk del .tmp-build-deps
