from django.core.management import call_command
from pytest import fixture


@fixture(scope="session")
def django_db_setup(django_db_setup: fixture, django_db_blocker: fixture) -> None:
    with django_db_blocker.unblock():
        call_command("loaddata", "sample.yaml")
