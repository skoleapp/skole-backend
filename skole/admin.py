from django.contrib import admin
from django.contrib.auth import get_user_model
from parler.admin import TranslatableAdmin

from skole.models import (
    Activity,
    ActivityType,
    Badge,
    BadgeProgress,
    Comment,
    InviteCode,
    Star,
    Thread,
    Vote,
)
from skole.utils.constants import Admin

admin.site.site_header = Admin.SITE_HEADER


# Untranslated models.
admin.site.register(get_user_model())
admin.site.register(BadgeProgress)
admin.site.register(Comment)
admin.site.register(Star)
admin.site.register(Thread)
admin.site.register(Vote)
admin.site.register(Activity)
admin.site.register(InviteCode)

# Translated models.
admin.site.register(Badge, TranslatableAdmin)
admin.site.register(ActivityType, TranslatableAdmin)
