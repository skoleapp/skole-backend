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

## Alpine Packages

### Build time packages

| Dependency                                                                             | Reason                                   |
| :------------------------------------------------------------------------------------- | :--------------------------------------- |
| [gcc](https://pkgs.alpinelinux.org/package/edge/main/x86_64/gcc)                       | Build the wheels for Pillow and psycopg2 |
| [musl-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/musl-dev)             | Build the wheel for Pillow               |
| [postgresql-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/postgresql-dev) | Build the wheel for psycopg2             |
| [zlib-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/zlib-dev)             | Build the wheel for Pillow               |

### Runtime packages

| Dependency                                                                                                    | Reason                                        |
| :-------------------------------------------------------------------------------------------                  | :----------------------------------           |
| [cairo-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/cairo-dev )                                 | Build and use mat2 to clean file metadata     |
| [exiftool](https://pkgs.alpinelinux.org/package/edge/main/x86_64/exiftool )                                   | Use mat2 to clean file metadata               |
| [gdk-pixbuf-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/gdk-pixbuf-dev )                       | Use mat2 to clean file metadata               |
| [gettext](https://pkgs.alpinelinux.org/package/edge/main/x86_64/gettext)                                      | Run Django compilemessages                    |
| [gobject-introspection-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/gobject-introspection-dev ) | Build and use mat2 to clean file metadata     |
| [jpeg-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/jpeg-dev)                                    | Build and use Pillow                          |
| [libmagic](https://pkgs.alpinelinux.org/package/edge/main/x86_64/libmagic)                                    | Guess file types with python-magic            |
| [librsvg-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/librsvg-dev )                             | Use mat2 to clean file metadata               |
| [poppler-dev](https://pkgs.alpinelinux.org/package/edge/main/x86_64/poppler-dev)                              | Use mat2 to clean file metadata               |
| [postgresql-client](https://pkgs.alpinelinux.org/package/edge/main/x86_64/postgresql-client)                  | Connect to PostgreSQL with psycopg2           |
