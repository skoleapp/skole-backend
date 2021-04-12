from django.apps.registry import Apps
from django.conf import settings
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    """
    Make sure that all existing users' emails are whitelisted.

    This allows them to keep on using their existing emails, even if they wouldn't be
    allowed school emails.
    """

    User = apps.get_model("skole", "User")
    AttemptedEmail = apps.get_model("skole", "AttemptedEmail")

    allowed_domains = (f"@{domain}" for domain in settings.ALLOWED_EMAIL_DOMAINS)

    users = User.objects.filter(verified=True)
    for domain in allowed_domains:
        users = users.exclude(email__endswith=domain)

    for user in users.iterator():
        AttemptedEmail.objects.update_or_create(
            email=user.email, defaults=dict(is_whitelisted=True)
        )


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0051_add_used_invite_code_for_existing_users"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]
