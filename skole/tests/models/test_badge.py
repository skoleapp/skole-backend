from pytest import fixture

from skole.models import Badge


def test_str(db: fixture) -> None:
    badge = Badge.objects.create(name="test_badge", description="test_description")
    assert str(badge) == badge.name
