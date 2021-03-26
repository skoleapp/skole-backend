import pytest
from django.contrib.auth import get_user_model

from skole.models import Resource, Star, Thread


@pytest.mark.django_db
def test_str() -> None:
    star1 = Star.objects.get(pk=1)
    star3 = Star.objects.get(pk=3)
    assert str(star1) == "testuser2 - Test Thread 1"
    assert str(star3) == "testuser2 - Sample Exam 1 2012-12-12"


@pytest.mark.django_db
def test_manager_perform_star_ok() -> None:
    user = get_user_model().objects.get(pk=2)
    thread3 = Thread.objects.get(pk=3)
    resource3 = Resource.objects.get(pk=3)

    star1 = Star.objects.create_or_delete_star(user=user, target=thread3)
    star2 = Star.objects.create_or_delete_star(user=user, target=resource3)

    assert star1 is not None
    assert star1.thread == thread3
    assert star2 is not None
    assert star2.resource == resource3


@pytest.mark.django_db
def test_manager_perform_star_existing() -> None:
    user = get_user_model().objects.get(pk=2)
    thread3 = Thread.objects.get(pk=3)
    resource3 = Resource.objects.get(pk=3)

    star1 = Star.objects.create_or_delete_star(user=user, target=thread3)
    star2 = Star.objects.create_or_delete_star(user=user, target=resource3)

    assert star1 is not None
    assert star2 is not None

    star1 = Star.objects.create_or_delete_star(user=user, target=thread3)
    star2 = Star.objects.create_or_delete_star(user=user, target=resource3)

    assert star1 is None
    assert star2 is None


@pytest.mark.django_db
def test_manager_perform_star_bad_target() -> None:
    user = get_user_model().objects.get(pk=2)
    bad_target = user
    with pytest.raises(TypeError):
        # Ignore: `User` is obviously invalid and invalid type for the `target`
        #   argument, but that's exactly what we're testing here.
        Star.objects.create_or_delete_star(user=user, target=bad_target)  # type: ignore[arg-type]
