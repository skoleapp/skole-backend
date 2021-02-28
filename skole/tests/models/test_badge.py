import pytest

from skole.models import Badge


@pytest.mark.django_db
def test_str() -> None:
    # Ignore: Mypy doesn't understand that even though these are inside the
    #   `translations` field they can be passed fine to `create()` like this.
    badge = Badge.objects.create(name="test_badge", description="test_description")  # type: ignore[misc]
    assert str(badge) == badge.name
