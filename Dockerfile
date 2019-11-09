FROM python:3.8.0-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /app
WORKDIR /app

RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
  gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apk del .tmp-build-deps

COPY mypy.ini .
COPY pytest.ini .
COPY .coveragerc .

RUN mkdir -p /static
RUN mkdir -p /media

RUN adduser -D user
RUN chown -R user:user /static/ /media/
RUN chmod -R 755 /static/ /media/
USER user

WORKDIR /app/src
