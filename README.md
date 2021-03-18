# Skole Backend 🎓

[![ci](https://github.com/skoleapp/skole-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/skoleapp/skole-backend/actions)
[![codecov](https://codecov.io/gh/skoleapp/skole-backend/branch/develop/graph/badge.svg?token=EHHHpM9EJO)](https://codecov.io/gh/skoleapp/skole-backend)
[![mypy checked](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This is the GraphQL backend for the Skole app.

Also check out the [README from `skole` repo](https://github.com/skoleapp/skole/blob/develop/README.md).

See detailed description for all top-level dependencies in [`dependencies.md`](dependencies.md) file.

## What's inside? 🧐

A quick look at the top-level files and directories excluding Git ignored locations.

1.  [**`.github/`**](.github/): Configuration for [Github Actions](https://github.com/features/actions).
2.  [**`.idea/`**](.idea/): [Jetbrains](https://www.jetbrains.com/) editor configuration.
3.  [**`config/`**](config/): Configuration for [Django](https://www.djangoproject.com/) project.
4.  [**`media/`**](media/): Few media files for testing.
5.  [**`skole/`**](skole/): Source code.
6.  [**`.dockerignore`**](.dockerignore): List of files ignored by [Docker](https://www.docker.com/).
7.  [**`.flake8`**](.flake8): Configuration for [Flake8](https://flake8.pycqa.org/en/latest/).
8.  [**`.gitignore`**](.gitignore): List of files ignored by [Git](https://git-scm.com/).
9.  [**`.graphqlconfig`**](.graphqlconfig): GraphQL configuration file, used by [JS GraphQL](https://plugins.jetbrains.com/plugin/8097-js-graphql)  JetBrains IDE plugin.
10. [**`Dockerfile`**](Dockerfile): Formal instructions for Docker how to build the image for the app.
11. [**`README.md`**](README.md): The file you're reading.
12. [**`dependencies.md`**](dependencies.md): Documentation about the project's top-level dependencies.
13. [**`manage.py`**](manage.py): Auto-generated for a Django project, see [docs](https://docs.djangoproject.com/en/stable/ref/django-admin/).
14. [**`mypy.ini`**](mypy.ini): Configuration for [Mypy](http://mypy-lang.org/).
15. [**`pyproject.toml`**](pyproject.toml): Configuration for various Python tools.
16. [**`requirements-dev.txt`**](requirements-dev.txt): List of top-level development requirements.
17. [**`requirements.lock`**](requirements.lock): Exact pinned versions of production requirements and all peer dependencies.
18. [**`requirements.txt`**](requirements.txt): List of top-level production requirements.
19. [**`schema.graphql`**](schema.graphql): GraphQL schema for noticing schema changes quickly from PRs.

## Development Tips 🚀

- No pull requests can be merged without CI pipeline first building and running [`Dockerfile`](Dockerfile) against it.
  See the `CMD` of the `ci` stage for the full list of stuff it runs and validates.
  The CI pipeline also verifies the code style, so there is no need to argue about formatting.

- Use [Google style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) docstrings.

- All `assert` statements are just for type checking or for generally helping the developer.
  They should not be used for actual program logic since they are stripped away in production
  with the use of the `PYTHONOPTIMIZE=1` env variable.

<!-- -->

- Inherit all models from `SkoleModel` or `TranslatableSkoleModel`.
- Inherit all managers from `SkoleManager` or `TranslatableSkoleManager`.
- Inherit all forms from `SkoleForm`, `SkoleModelForm`, or `SkoleUpdateModelForm`.
- Inherit all mutations from `SkoleCreateUpdateMutationMixin` or `SkoleDeleteMutationMixin`.
- Inherit all GraphQL object types from `SkoleObjectType`.
- Inherit all graphene-django object types from `SkoleDjangoObjectType`.

<!-- -->

- Do not access any "private" names starting with an underscore `_`
  outside the class or module where it's defined, without a very good reason.

- Do not manually call `Model.save()` outside of model files.
  It's fine to call `save()` on a `ModelForm` to save the instance though.

- Sometimes Mypy doesn't understand a type, and that's completely fine. In these cases ignore
  only the specific error with `# type: ignore[err-name]` AND write a comment starting
  with `# Ignore: ` on top of it, which explains why the ignore was needed.

- All monkey patched code affecting 3rd party modules should go into [`patched.py`](skole/patched.py).
  The compatibility of the patched code should also be verified with a test in [`test_patched.py`](skole/tests/test_patched.py).

- Since `_` is reserved as an alias for Django's translation functions, use a double underscore `__`
  for ignored values, e.g. `foo, __ = Foo.objects.get_or_create(...)` or `[bar() for __ in range(n)]`.

- All GraphQL queries should be documented in their resolver docstring. All mutations should be documented in their class docstring.
  This info is shown in GraphiQL docs, together with information automatically taken from the actual code (see `SkoleObjectTypeMeta` for details).

- Use the `@login_required` decorator defined in [`skole.overridden`](skole/overridden.py) instead of the
  one in `graphql_jwt.decorators`. The former automatically adds authorization required information to the API docs.

- Whenever you add fields to `User` model, or relations to `settings.AUTH_USER_MODEL`, make sure
  to add those to `MyDataMutation` in [`skole.schemas.gdpr`](skole/schemas/gdpr.py).

- It's fine to use [PostgreSQL specific Django utilities](https://docs.djangoproject.com/en/stable/ref/contrib/postgres),
  such as `ArrayAgg`. They can make life a lot easier, and we can assume that the application is always run on Postgres.
