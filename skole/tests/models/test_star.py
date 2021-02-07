import pytest
from django.contrib.auth import get_user_model

from skole.models import Course, Resource, Star
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    star1 = Star.objects.get(pk=1)
    star3 = Star.objects.get(pk=3)
    assert str(star1) == "testuser2 - Test Engineering Course 1 TEST0001"
    assert str(star3) == "testuser2 - Sample Exam 1 2012-12-12"


def test_manager_perform_star_ok(db: Fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    course3 = Course.objects.get(pk=3)
    resource3 = Resource.objects.get(pk=3)

    star1 = Star.objects.create_or_delete_star(user=user, target=course3)
    star2 = Star.objects.create_or_delete_star(user=user, target=resource3)

    assert star1 is not None
    assert star1.course == course3
    assert star2 is not None
    assert star2.resource == resource3


def test_manager_perform_star_existing(db: Fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    course3 = Course.objects.get(pk=3)
    resource3 = Resource.objects.get(pk=3)

    star1 = Star.objects.create_or_delete_star(user=user, target=course3)
    star2 = Star.objects.create_or_delete_star(user=user, target=resource3)

    assert star1 is not None
    assert star2 is not None

    star1 = Star.objects.create_or_delete_star(user=user, target=course3)
    star2 = Star.objects.create_or_delete_star(user=user, target=resource3)

    assert star1 is None
    assert star2 is None


def test_manager_perform_star_bad_target(db: Fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    bad_target = user
    with pytest.raises(TypeError):
        # Ignore: `User` is obviously invalid and invalid type for the `target`
        #   argument, but that's exactly what we're testing here.
        Star.objects.create_or_delete_star(user=user, target=bad_target)  # type: ignore[arg-type]
