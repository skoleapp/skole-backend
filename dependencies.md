# Skole backend dependencies

This document explains the need for every top level dependency the project has.

## PyPi

### Prod requirements

| Dependency                                                           | Reason
| :---------                                                           | :-----
| [Django](https://pypi.org/project/Django/)                           | Duh.
| [Pillow](https://pypi.org/project/Pillow/)                           | Use Django ImageField
| [PyYAML](https://pypi.org/project/PyYAML/)                           | Load Django YAML fixtures
| [dj-database-url](https://pypi.org/project/dj-database-url/)         | Pass the database credentials as one env variable
| [django-amazon-ses](https://pypi.org/project/django-amazon-ses/)     | Use AWS SES as the email backend for Django
| [django-cors-headers](https://pypi.org/project/django-cors-headers/) | CORS middleware
| [django-graphql-jwt](https://pypi.org/project/django-graphql-jwt/)   | GraphQL JWT authentication
| [django-imagekit](https://pypi.org/project/django-imagekit/)         | ImageSpecField for use avatars
| [django-parler](https://pypi.org/project/django-parler/)             | Translations
| [django-s3-storage](https://pypi.org/project/django-s3-storage/)     | Use AWS S3 as the storage backend for Django
| [graphene-django](https://pypi.org/project/graphene-django/)         | Use GraphQL with Django
| [gunicorn](https://pypi.org/project/gunicorn/)                       | Production webserver
| [psycopg2](https://pypi.org/project/psycopg2/)                       | Connect to PostgreSQL
| [python-magic](https://pypi.org/project/python-magic/)               | Detect file types for validation
| [requests](https://pypi.org/project/requests/)                       | Better HTTP requests for calling external APIs

### Dev requirements

| Dependency                                               | Reason
| :---------                                               | :-----
| [autoflake](https://pypi.org/project/autoflake/)         | Removing unused imports
| [black](https://pypi.org/project/black/)                 | Formatting code
| [django-stubs](https://pypi.org/project/django-stubs/)   | Type hint stubs for Django which Mypy uses
| [docformatter](https://pypi.org/project/docformatter/)   | Formatting docstrings
| [flake8](https://pypi.org/project/flake8/)               | Linting
| [isort](https://pypi.org/project/isort/)                 | Linting and sorting imports
| [mypy](https://pypi.org/project/mypy/)                   | Type checking
| [pytest-cov](https://pypi.org/project/pytest-cov/)       | Calulating test coverage with pytest
| [pytest-django](https://pypi.org/project/pytest-django/) | Django specific pytest fixtures and a lot more
| [pytest](https://pypi.org/project/pytest/)               | Unit testing

## Alpine Packages

### Build time packages

| Dependency                                                                             | Reason
| :---------                                                                             | :-----
| [gcc](https://pkgs.alpinelinux.org/package/edge/main/x86_64/gcc)                       | Build the wheels for Pillow and psycopg2
| [musl-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/musl-dev)             | Build the wheel for Pillow
| [postgresql-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/postgresql-dev) | Build the wheel for psycopg2
| [zlib-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/zlib-dev)             | Build the wheel for Pillow

### Runtime packages

| Dependency                                                                                   | Reason
| :---------                                                                                   | :-----
| [gettext](https://pkgs.alpinelinux.org/package/edge/main/x86_64/gettext)                     | Run Django compilemessages
| [jpeg-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/jpeg-dev)                   | Build and use Pillow
| [libmagic](https://pkgs.alpinelinux.org/package/edge/main/x86_64/libmagic)                   | Guess file types with python-magic
| [postgresql-client](https://pkgs.alpinelinux.org/package/edge/main/x86_64/postgresql-client) | Connect to PostgreSQL with psycopg2
