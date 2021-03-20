from typing import Any

from admin_confirm import AdminConfirmMixin
from admin_confirm.admin import confirm_action
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.template.loader import render_to_string
from parler.admin import TranslatableAdmin

import skole.utils.email
from skole.models import (
    Activity,
    ActivityType,
    Badge,
    City,
    Comment,
    Country,
    Course,
    EmailSubscription,
    MarketingEmail,
    MarketingEmailSender,
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


# Ignore: Mypy gives error: `Missing type parameters for generic type "ModelAdmin"`.
class MarketingEmailAdmin(AdminConfirmMixin, ModelAdmin):  # type: ignore[type-arg]
    actions = ("send_marketing_email",)
    exclude = ("sent",)
    readonly_fields = ("preview",)

    @staticmethod
    def preview(obj: MarketingEmail) -> str:
        if obj.contents:
            contents = obj.contents.read().decode("utf-8")
            context = {"contents": contents, "update_email_subscription_url": "#"}
            return render_to_string(
                template_name="email/marketing_email.html", context=context
            )

        return "Visible after saving"

    @staticmethod
    @confirm_action
    def send_marketing_email(
        modeladmin: Any, request: Any, queryset: QuerySet[MarketingEmail]
    ) -> None:
        for marketing_email in queryset:
            if marketing_email.sent:
                messages.error(
                    request=request,
                    message=f"The following email has already been sent: {marketing_email.subject}.",
                )
            else:
                skole.utils.email.send_marketing_email(
                    request=request, instance=marketing_email
                )
                marketing_email.sent = True
                marketing_email.save(update_fields=["sent"])
                messages.success(
                    request=request,
                    message=f"Successfully sent email: {marketing_email.subject}",
                )


# Untranslated models.
admin.site.register(get_user_model())
admin.site.register(Comment)
admin.site.register(Course)
admin.site.register(EmailSubscription)
admin.site.register(MarketingEmailSender)
admin.site.register(MarketingEmail, MarketingEmailAdmin)
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
