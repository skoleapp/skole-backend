import pytest
from django.contrib.auth import get_user_model
from pytest import fixture

from core.models import Course, Resource, Star


def test_str(db: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    course = Course.objects.get(pk=1)
    resource = Resource.objects.get(pk=1)

    star1 = Star.objects.perform_star(user=user, target=course)
    star2 = Star.objects.perform_star(user=user, target=resource)

    assert str(star1) == "testuser2 - Test Engineering Course 1 TEST0001"
    assert str(star2) == "testuser2 - Sample exam 1"


def test_manager_create_ok(db: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    course = Course.objects.get(pk=1)
    resource = Resource.objects.get(pk=1)

    star1 = Star.objects.perform_star(user=user, target=course)
    star2 = Star.objects.perform_star(user=user, target=resource)

    assert star1 is not None
    assert star1.course == course
    assert star2 is not None
    assert star2.resource == resource


def test_manager_create_existing(db: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    course = Course.objects.get(pk=1)
    resource = Resource.objects.get(pk=1)

    star1 = Star.objects.perform_star(user=user, target=course)
    star2 = Star.objects.perform_star(user=user, target=resource)

    assert star1 is not None
    assert star2 is not None

    star1 = Star.objects.perform_star(user=user, target=course)
    star2 = Star.objects.perform_star(user=user, target=resource)

    assert star1 is None
    assert star2 is None


def test_manager_create_bad_target(db: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    bad_target = user
    with pytest.raises(TypeError):
        star = Star.objects.perform_star(user=user, target=bad_target)  # type: ignore[arg-type]
