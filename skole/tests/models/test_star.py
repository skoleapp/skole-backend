import pytest
from django.contrib.auth import get_user_model

from skole.models import Star, Thread


@pytest.mark.django_db
def test_str() -> None:
    star1 = Star.objects.get(pk=1)
    star2 = Star.objects.get(pk=2)
    assert str(star1) == "testuser2 - Test Thread 1"
    assert str(star2) == "testuser2 - Test Thread 2"


@pytest.mark.django_db
def test_manager_perform_star_ok() -> None:
    user = get_user_model().objects.get(pk=2)
    thread3 = Thread.objects.get(pk=3)

    star = Star.objects.create_or_delete_star(user=user, thread=thread3)
    assert star is not None
    assert star.thread == thread3


@pytest.mark.django_db
def test_manager_perform_star_existing() -> None:
    user = get_user_model().objects.get(pk=2)
    thread3 = Thread.objects.get(pk=3)

    star = Star.objects.create_or_delete_star(user=user, thread=thread3)
    assert star is not None

    star = Star.objects.create_or_delete_star(user=user, thread=thread3)
    assert star is None


@pytest.mark.django_db
def test_manager_perform_star_bad_target() -> None:
    user = get_user_model().objects.get(pk=2)
    bad_target = user
    with pytest.raises(ValueError):
        # Ignore: `User` is obviously invalid and invalid type for the `target`
        #   argument, but that's exactly what we're testing here.
        Star.objects.create_or_delete_star(user=user, thread=bad_target)  # type: ignore[arg-type]
