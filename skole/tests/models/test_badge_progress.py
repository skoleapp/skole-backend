from __future__ import annotations

import datetime

import pytest
from django.contrib.auth import get_user_model

from skole.models import Badge, BadgeProgress, Comment


@pytest.mark.django_db
def test_str() -> None:
    progress1 = BadgeProgress.objects.get(pk=1)
    assert str(progress1) == "Staff (acquired) - testuser2"
    progress1.acquired = None
    progress1.save()
    assert str(progress1) == "Staff (not acquired) - testuser2"

    progresses = get_user_model().objects.get(pk=2).get_or_create_badge_progresses()
    progress2 = progresses.get(badge__pk=3)
    assert str(progress2) == "First Comment (0/1) - testuser2"
    progress2.progress += 1
    progress2.save()
    assert str(progress2) == "First Comment (1/1) - testuser2"


@pytest.mark.django_db
def test_acquired_on_save() -> None:
    progresses = get_user_model().objects.get(pk=2).get_or_create_badge_progresses()
    progress = progresses.get(badge__pk=3)
    assert str(progress) == "First Comment (0/1) - testuser2"
    progress.progress += 1
    progress.save()
    progress.refresh_from_db()
    assert isinstance(progress.acquired, datetime.datetime)


@pytest.mark.django_db
def test_user_gets_score_when_acquired() -> None:
    badge = Badge.objects.get(identifier="first_comment")
    badge.completion_score = 10
    badge.save()

    user = get_user_model().objects.get(pk=2)
    old_score = user.score
    progresses = user.get_or_create_badge_progresses()
    progress = progresses.get(badge__pk=3)
    progress.progress += 1
    progress.save()
    user.refresh_from_db()
    assert user.score == old_score + 10


@pytest.mark.django_db
def test_create_first_comment_badge_signal_handler() -> None:
    user = get_user_model().objects.get(pk=10)
    assert BadgeProgress.objects.filter(user=user).count() == 0

    Comment.objects.create(user=user, text="A comment.")

    assert BadgeProgress.objects.filter(user=user).count() == 1

    progress = BadgeProgress.objects.get(user=user)
    assert progress.badge.identifier == "first_comment"
    assert progress.badge.steps == progress.progress == 1
    assert isinstance(progress.acquired, datetime.datetime)
