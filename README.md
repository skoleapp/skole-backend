# Skole Backend 🎓

This is the GraphQL backend for the Skole app.

Also check out the [README from `skole` repo](https://github.com/ruohola/skole/blob/develop/README.md).

See detailed description for all top-level dependencies in [`dependencies.md`](dependencies.md) file.

## What's inside? 🧐

A quick look at the top-level files and directories excluding Git ignored locations.

    .
    ├── .circleci
    ├── .github
    ├── .idea
    ├── .vscode
    ├── config
    ├── media
    ├── skole
    ├── .dockerignore
    ├── .flake8
    ├── .gitignore
    ├── .graphqlconfig
    ├── dependencies.md
    ├── docker-compose-circleci.yml
    ├── Dockerfile
    ├── Dockerfile.prod
    ├── mypy.ini
    ├── pyproject.toml
    ├── README.md
    ├── requirements-dev.txt
    ├── requirements.txt
    └── schema.graphql

1.  **`/.circleci`**: Configuration for [CircleCI](https://circleci.com/).

2.  **`/.github`**: Configuration for [Github Actions](https://github.com/features/actions).

3.  **`/.idea`**: [Jetbrains](https://www.jetbrains.com/) editor configuration.

4.  **`/.vscode`**: [VSCode](https://code.visualstudio.com/) configuration.

5.  **`/config`**: Configuration for [Django](https://www.djangoproject.com/) project.

6.  **`/media`**: Static assets and media.

7.  **`/skole`**: Source code.

8.  **`.dockerignore`**: List of files ignored by [Docker](https://www.docker.com/).

9.  **`.flake8`**: Configuration for [Flake8](https://flake8.pycqa.org/en/latest/).

10. **`.gitignore`**: List of files ignored by [Git](https://git-scm.com/).

11. **`.graphqlconfig`**: GraphQL configuration file, used by e.g. Jetbrains editors.

12. **`dependencies`**: Documentation for top-level dependencies.

13. **`docker-compose-circleci.yml`**: Docker configuration for CircleCI pipelines.

14. **`Dockerfile`**: Docker configuration for development.

15. **`Dockerfile.prod`**: Docker configuration for production.

16. **`manage.py`**: Auto-generated for Django project, see [docs](https://docs.djangoproject.com/en/3.1/ref/django-admin/).

17. **`mypy.ini`**: Configuration for [Mypy](http://mypy-lang.org/).

18. **`pyproject.toml`**: Python project configuration.

19. **`README.md`**: Text file containing useful reference information about this project.

20. **`requirements-dev.txt`**: List of development requirements.

21. **`requirements.txt`**: List of production requirements.

22. **`schema.graphql`**: GraphQL schema for [Introspection](https://graphql.org/learn/introspection/).

## Development Tips 🚀

- No pull requests can be merged without CircleCI first building and running [`Dockerfile`](Dockerfile) against it.
  See the bottommost `CMD` in it for the full list of stuff it runs and validates.
  CircleCI also verifies the code style, so there is no need to argue about formatting.

- Use [Google style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) docstrings.

- All `assert` statements are just for type checking or for generally helping the developer.
  They should not be used for actual program logic since they are stripped away in production
  with the use of the `PYTHONOPTIMIZE=1` env variable.

<!-- -->

- Inherit all models from `SkoleModel` or `TranslatableSkoleModel`.
- Inherit all managers from `SkoleManager` or `TranslatableSkoleManager`.
- Inherit all forms from `SkoleForm`, `SkoleModelForm`, or `SkoleUpdateModelForm`.
- Inherit all mutations from `SkoleCreateUpdateMutationMixin` or `SkoleDeleteMutationMixin`.

<!-- -->

- Try not to access any "private" names starting with an underscore `_`
  outside the class or module where it's defined.

- Do not manually call `Model.save()` outside of model files.
  It's fine to call `save()` on a `ModelForm` to save the instance though.

- Sometimes Mypy doesn't understand a type, and that's completely fine. In these cases ignore
  only the specific error with `# type: ignore[err-name]` AND write a comment starting
  with `# Ignore: ` on top of it, which explains why the ignore was needed.

- All monkey patched code affecting 3rd party modules should go into [`patched.py`](skole/patched.py).
  The compatibility of the patched code should also be verified with a test in [`test_patched.py`](skole/tests/test_patched.py).

- Since `_` is reserved as an alias for Django's translation functions, use a double underscore `__`
  for ignored values, e.g. `foo, __ = Foo.objects.get_or_create(...)` or `[bar() for __ in range(n)]`.
