from skole.models import Badge
from skole.utils.types import Fixture


def test_str(db: Fixture) -> None:
    badge = Badge.objects.create(name="test_badge", description="test_description")
    assert str(badge) == badge.name
