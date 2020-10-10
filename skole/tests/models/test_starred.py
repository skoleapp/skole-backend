import pytest
from django.contrib.auth import get_user_model

from skole.models import Course, Resource, Starred
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    course = Course.objects.get(pk=1)
    resource = Resource.objects.get(pk=1)

    starred1 = Starred.objects.perform_star(user=user, target=course)
    starred2 = Starred.objects.perform_star(user=user, target=resource)

    assert str(starred1) == "testuser2 - Test Engineering Course 1 TEST0001"
    assert str(starred2) == "testuser2 - Sample exam 1"


def test_manager_perform_star_ok(db: Fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    course = Course.objects.get(pk=1)
    resource = Resource.objects.get(pk=1)

    starred1 = Starred.objects.perform_star(user=user, target=course)
    starred2 = Starred.objects.perform_star(user=user, target=resource)

    assert starred1 is not None
    assert starred1.course == course
    assert starred2 is not None
    assert starred2.resource == resource


def test_manager_perform_star_existing(db: Fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    course = Course.objects.get(pk=1)
    resource = Resource.objects.get(pk=1)

    starred1 = Starred.objects.perform_star(user=user, target=course)
    starred2 = Starred.objects.perform_star(user=user, target=resource)

    assert starred1 is not None
    assert starred2 is not None

    starred1 = Starred.objects.perform_star(user=user, target=course)
    starred2 = Starred.objects.perform_star(user=user, target=resource)

    assert starred1 is None
    assert starred2 is None


def test_manager_perform_star_bad_target(db: Fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    bad_target = user
    with pytest.raises(TypeError):
        # Ignore: `User` is obviously invalid and invalid type for the `target`
        #   argument, but that's exactly what we're testing here.
        Starred.objects.perform_star(user=user, target=bad_target)  # type: ignore[arg-type]
