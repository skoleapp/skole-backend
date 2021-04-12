from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    """
    Make sure that the invite code that our 1.0 users used has no initial usages.

    This makes it so that we don't end up calculating k-factor so that it would
    incorrectly seem that any of those users got *invited* to the platform.
    """

    InviteCode = apps.get_model("skole", "InviteCode")

    code = InviteCode.objects.filter(code="BETAUSER").first()
    if code:
        code.initial_usages = 0
        code.save(update_fields=("initial_usages",))


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0055_invite_code_initial_usages"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]
