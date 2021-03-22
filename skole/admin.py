from django.contrib import admin
from django.contrib.auth import get_user_model
from parler.admin import TranslatableAdmin

from skole.models import (
    Activity,
    ActivityType,
    Badge,
    BadgeProgress,
    City,
    Comment,
    Country,
    Course,
    Resource,
    ResourceType,
    School,
    SchoolType,
    Star,
    Subject,
    Vote,
)
from skole.utils.constants import Admin

admin.site.site_header = Admin.SITE_HEADER


# Untranslated models.
admin.site.register(get_user_model())
admin.site.register(BadgeProgress)
admin.site.register(Comment)
admin.site.register(Course)
admin.site.register(Resource)
admin.site.register(Star)
admin.site.register(Vote)
admin.site.register(Activity)

# Translated models.
admin.site.register(Badge, TranslatableAdmin)
admin.site.register(City, TranslatableAdmin)
admin.site.register(Country, TranslatableAdmin)
admin.site.register(ResourceType, TranslatableAdmin)
admin.site.register(SchoolType, TranslatableAdmin)
admin.site.register(School, TranslatableAdmin)
admin.site.register(Subject, TranslatableAdmin)
admin.site.register(ActivityType, TranslatableAdmin)
