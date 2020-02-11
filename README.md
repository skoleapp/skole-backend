# Skole Backend :mortar_board:

### Useful Backend Commands

- To make migrations, run `yarn make-migrations`.
- To clear migrations, run `yarn clear-migrations`.
- To migrate db, run: `yarn migrate`.
- To create superuser, run `yarn create-superuser`.
- To import test data, run `yarn import-test-data`.
- To run tests and type checks, run `yarn test`.
- To run linting, run `yarn lint`.

### To enable pre-commit hooks locally

```
$ cd skole/backend
$ git config --local core.hooksPath .githooks/
```
