import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from skole.models import Badge, Resource


@pytest.mark.django_db
def test_award_badges() -> None:
    # No badges have been made available yet.
    assert Badge.objects.filter(made_available=True).count() == 0

    user2 = get_user_model().objects.get(pk=2)
    user10 = get_user_model().objects.get(pk=10)
    assert user2.get_acquired_badges().count() == 1  # Only 'Staff' badge.
    assert user10.get_acquired_badges().count() == 0  # No badges.
    call_command("award_badges")
    badges = user2.get_acquired_badges()
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
    badges = user10.get_acquired_badges()
    assert badges.count() == 1
    assert badges.all().get(identifier="first_resource")

    # All badges have been made available (except Staff and Moderator).
    assert Badge.objects.filter(made_available=False).count() == 2
