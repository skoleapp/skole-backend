from skole.models import Badge
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    # Ignore: Mypy doesn't understand even though these are inside the `translations`
    #   field they can be passed fine to `create()` like this.
    badge = Badge.objects.create(name="test_badge", description="test_description")  # type: ignore[misc]
    assert str(badge) == badge.name
