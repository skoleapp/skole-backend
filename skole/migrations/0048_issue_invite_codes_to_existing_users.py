from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    """Give all existing verifier users their invite codes if they don't have them
    yet."""

    User = apps.get_model("skole", "User")
    InviteCode = apps.get_model("skole", "InviteCode")

    for user in User.objects.filter(invite_code=None, verified=True):
        InviteCode.objects.create_invite_code(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0047_refactor_invite_code"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]
