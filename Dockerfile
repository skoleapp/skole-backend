FROM nikolaik/python-nodejs:python3.8-nodejs13-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /app
WORKDIR /app

RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
  gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

COPY package.json .
COPY requirements.txt .
COPY requirements-dev.txt .

RUN yarn install

RUN apk del .tmp-build-deps

COPY mypy.ini .
COPY pytest.ini .
COPY .coveragerc .
COPY .isort.cfg .

RUN mkdir -p /static
RUN mkdir -p /media

RUN adduser -D user
RUN chown -R user:user /static /media /app
RUN chmod -R 755 /static /media /app
USER user
