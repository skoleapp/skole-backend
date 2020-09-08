from skole.models import Course, Resource
from skole.types import Fixture


def test_repr(db: Fixture) -> None:
    """This tests _SkoleModelMixin's __repr__"""
    assert repr(Course.objects.get(pk=1)) == "<Course:1-Test Engineering Course 1>"
    assert repr(Resource.objects.get(pk=1)) == "<Resource:1>"
