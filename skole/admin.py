from __future__ import annotations

from django.contrib import admin
from django.contrib.auth import get_user_model
from parler.admin import TranslatableAdmin

from skole.models import (
    Activity,
    ActivityType,
    AttemptedEmail,
    Badge,
    BadgeProgress,
    Comment,
    DailyVisit,
    InviteCode,
    Star,
    Thread,
    Vote,
)
from skole.utils.constants import Admin

admin.site.site_header = Admin.SITE_HEADER


# Untranslated models.
admin.site.register(get_user_model())
admin.site.register(Activity)
admin.site.register(AttemptedEmail)
admin.site.register(BadgeProgress)
admin.site.register(Comment)
admin.site.register(DailyVisit)
admin.site.register(InviteCode)
admin.site.register(Star)
admin.site.register(Thread)
admin.site.register(Vote)

# Translated models.
admin.site.register(Badge, TranslatableAdmin)
admin.site.register(ActivityType, TranslatableAdmin)
