from __future__ import annotations

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    """
    Make sure that all existing users have 'used' an invite code.

    This allows them to fully use the app and allows their profiles to be queried from
    the user detail query.
    """

    User = apps.get_model("skole", "User")
    InviteCode = apps.get_model("skole", "InviteCode")

    code, __ = InviteCode.objects.update_or_create(
        code="BETAUSER", defaults=dict(usages=0)
    )
    User.objects.filter(used_invite_code=None, verified=True).update(
        used_invite_code=code
    )


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0050_invite_code_user_blank"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]
