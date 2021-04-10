from django.conf import settings
from django.db import models
from django.db.models import F
from django.utils import timezone

from skole.models.base import SkoleManager, SkoleModel
from skole.models.user import User


class DailyVisitManager(SkoleManager["DailyVisit"]):
    def update_daily_visits(self, user: User) -> None:
        visit, __ = self.get_or_create(user=user, date=timezone.now().date())
        visit.visits = F("visits") + 1
        visit.save(update_fields=("visits", "last_visit"))


class DailyVisit(SkoleModel):
    date = models.DateField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="daily_visits",
        null=True,
        blank=True,
        # Don't cascade since we don't want to ever lose visitor data.
        on_delete=models.SET_NULL,
    )
    visits = models.PositiveIntegerField(default=0)
    last_visit = models.DateTimeField(auto_now=True)

    objects = DailyVisitManager()

    class Meta:
        unique_together = ("date", "user")

    def __str__(self) -> str:
        return f"{self.date} - {self.user} - Visits: {self.visits}"
