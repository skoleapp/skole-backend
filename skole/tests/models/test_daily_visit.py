import re

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from skole.models.daily_visit import DailyVisit


@pytest.mark.django_db
def test_update_daily_visits() -> None:
    user = get_user_model().objects.get(pk=2)
    before_date = timezone.now().date()

    assert DailyVisit.objects.count() == 0
    DailyVisit.objects.update_daily_visits(user=user)
    assert DailyVisit.objects.count() == 1
    visit = DailyVisit.objects.get(user=user)

    after_date = timezone.now().date()

    # In theory the date could've changed between setting `before_date` and calling the
    # `update_daily_visits` method. This is why we test that the date is either or.
    assert visit.date == before_date or visit.date == after_date
    assert visit.user == user
    assert visit.visits == 1

    DailyVisit.objects.update_daily_visits(user=user)
    assert DailyVisit.objects.count() == 1
    visit = DailyVisit.objects.get(user=user)
    assert visit.visits == 2


@pytest.mark.django_db
def test_str() -> None:
    user = get_user_model().objects.get(pk=2)
    DailyVisit.objects.update_daily_visits(user=user)
    visit = DailyVisit.objects.get(user=user)
    assert re.match(r"^\d\d\d\d-\d\d-\d\d - testuser2 - Visits: 1", str(visit))

    DailyVisit.objects.update_daily_visits(user=user)
    visit = DailyVisit.objects.get(user=user)
    assert re.match(r"^\d\d\d\d-\d\d-\d\d - testuser2 - Visits: 2", str(visit))
