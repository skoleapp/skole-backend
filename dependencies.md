# Skole Backend Dependencies

This document explains the need for every top level dependency the project has.

## PyPi

### Prod requirements

| Dependency                                                           | Reason                                            |
| :------------------------------------------------------------------- | :------------------------------------------------ |
| [Django](https://pypi.org/project/Django/)                           | Duh.                                              |
| [Pillow](https://pypi.org/project/Pillow/)                           | Use Django's `ImageField`                         |
| [PyYAML](https://pypi.org/project/PyYAML/)                           | Load Django YAML fixtures                         |
| [dj-database-url](https://pypi.org/project/dj-database-url/)         | Pass the database credentials as one env variable |
| [django-amazon-ses](https://pypi.org/project/django-amazon-ses/)     | Use AWS SES as Django's email backend             |
| [django-autoslug](https://pypi.org/project/django-autoslug/)         | Automatic URL slugs for models                    |
| [django-cors-headers](https://pypi.org/project/django-cors-headers/) | CORS middleware                                   |
| [django-graphql-jwt](https://pypi.org/project/django-graphql-jwt/)   | GraphQL JWT authentication                        |
| [django-imagekit](https://pypi.org/project/django-imagekit/)         | `ImageSpecField` for user avatars                 |
| [django-parler](https://pypi.org/project/django-parler/)             | Translatable models                               |
| [django-s3-storage](https://pypi.org/project/django-s3-storage/)     | Use AWS S3 as Django's storage backend            |
| [graphene-django](https://pypi.org/project/graphene-django/)         | Use GraphQL with Django                           |
| [gunicorn](https://pypi.org/project/gunicorn/)                       | Production webserver                              |
| [mat2](https://pypi.org/project/mat2/)                               | Clean metadata from files                         |
| [psycopg2](https://pypi.org/project/psycopg2/)                       | Connect to PostgreSQL                             |
| [python-magic](https://pypi.org/project/python-magic/)               | Detect file types for validation                  |
| [requests](https://pypi.org/project/requests/)                       | Better HTTP requests for calling external APIs    |

### Dev requirements

| Dependency                                               | Reason                                         |
| :------------------------------------------------------- | :--------------------------------------------- |
| [autoflake](https://pypi.org/project/autoflake/)         | Removing unused imports                        |
| [black](https://pypi.org/project/black/)                 | Formatting code                                |
| [django-stubs](https://pypi.org/project/django-stubs/)   | Type hint stubs for Django which Mypy uses     |
| [docformatter](https://pypi.org/project/docformatter/)   | Formatting docstrings                          |
| [flake8](https://pypi.org/project/flake8/)               | Linting                                        |
| [isort](https://pypi.org/project/isort/)                 | Linting and sorting imports                    |
| [mypy](https://pypi.org/project/mypy/)                   | Type checking                                  |
| [pytest-cov](https://pypi.org/project/pytest-cov/)       | Calculating test coverage with pytest          |
| [pytest-django](https://pypi.org/project/pytest-django/) | Django specific pytest fixtures and a lot more |
| [pytest](https://pypi.org/project/pytest/)               | Unit testing                                   |

## Debian Packages

| Dependency                                                                             | Reason                                        |
| :------------------------------------------------------------------------------------- | :-------------------------------------------- |
| [gcc](https://packages.debian.org/buster/gcc)                                          | Build the wheels for Pillow and psycopg2      |
| [gettext](https://packages.debian.org/buster/gettext)                                  | Run Django's makemessages and compilemessages |
| [gir1.2-gdkpixbuf-2.0](https://packages.debian.org/buster/gir1.2-gdkpixbuf-2.0)        | Use mat2 to clean file metadata               |
| [gir1.2-poppler-0.18](https://packages.debian.org/buster/gir1.2-poppler-0.18)          | Use mat2 to clean file metadata               |
| [gir1.2-rsvg-2.0](https://packages.debian.org/buster/gir1.2-rsvg-2.0)                  | Use mat2 to clean file metadata               |
| [libcairo2-dev](https://packages.debian.org/buster/libcairo2-dev)                      | Build and use mat2 to clean file metadata     |
| [libgirepository1.0-dev](https://packages.debian.org/buster/libgirepository1.0-dev)    | Use mat2 to clean file metadata               |
| [libmagic-dev](https://packages.debian.org/buster/libmagic-dev)                        | Guess file types with python-magic            |
| [libimage-exiftool-perl](https://packages.debian.org/buster/libimage-exiftool-perl)    | Use mat2 to clean file metadata               |
| [libpq-dev](https://packages.debian.org/buster/libpq-dev)                              | Connect to PostgreSQL with psycopg2           |
| [postgresql-client](https://packages.debian.org/buster/postgresql-client)              | Use Django's dbshell / psql in production     |
| [python3-gi-cairo](https://packages.debian.org/buster/python3-gi-cairo)                | Use mat2 to clean file metadata               |
| [python3-mutagen](https://packages.debian.org/buster/python3-mutagen)                  | Use mat2 to clean file metadata               |
