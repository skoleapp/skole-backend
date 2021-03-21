import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.models import QuerySet

from skole.models import Badge, Resource, User


@pytest.mark.django_db
def test_award_badges() -> None:
    def get_acquired_badges(user: User) -> QuerySet[Badge]:
        return Badge.objects.filter(
            badge_progresses__user=user, badge_progresses__acquired__isnull=False
        )

    # No badges have been made available yet.
    assert Badge.objects.filter(made_available=True).count() == 0

    user2 = get_user_model().objects.get(pk=2)
    user10 = get_user_model().objects.get(pk=10)
    assert get_acquired_badges(user2).count() == 1  # Only 'Staff' badge.
    assert get_acquired_badges(user10).count() == 0  # No badges.
    call_command("award_badges")
    badges = get_acquired_badges(user2)
    assert badges.count() == 5
    assert list(badges.order_by("pk").values_list("identifier", flat=True)) == [
        "staff",
        "first_comment",
        "first_course",
        "first_resource",
        "first_upvote",
    ]

    # The user has created the Resource ID 2 and they should have gotten a badge for it.
    assert Resource.objects.get(pk=2).user == user10
    badges = get_acquired_badges(user10)
    assert badges.count() == 1
    assert badges.all().get(identifier="first_resource")

    # All badges have been made available (except Staff and Moderator).
    assert Badge.objects.filter(made_available=False).count() == 2
