from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from skole.models import Badge


@pytest.mark.django_db
def test_award_badges() -> None:
    # No badges have been made available yet.
    assert Badge.objects.filter(made_available=True).count() == 0

    user2 = get_user_model().objects.get(pk=2)
    user4 = get_user_model().objects.get(pk=4)
    assert user2.get_acquired_badges().count() == 1  # Only 'Staff' badge.
    assert user4.get_acquired_badges().count() == 0  # No badges.
    call_command("award_badges")
    badges = user2.get_acquired_badges()
    assert badges.count() == 4
    assert list(badges.order_by("pk").values_list("identifier", flat=True)) == [
        "staff",
        "first_comment",
        "first_thread",
        "first_upvote",
    ]

    # The user has created few threads and they should have gotten a badge for it.
    badges = user4.get_acquired_badges()
    assert list(badges.order_by("pk").values_list("identifier", flat=True)) == [
        "first_thread",
        "first_downvote",
    ]

    # All badges have been made available (except Staff and Moderator).
    assert Badge.objects.filter(made_available=False).count() == 2
