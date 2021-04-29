from __future__ import annotations

import random
import string
from typing import TYPE_CHECKING

from django.apps.registry import Apps
from django.conf import settings
from django.db import IntegrityError, migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

if TYPE_CHECKING:  # pragma: no cover
    from skole.models import InviteCode, User


def create_invite_code(code_model: type[InviteCode], user: User) -> InviteCode:
    invite_code = code_model(user=user)
    while True:
        invite_code.code = _generate_code()
        try:
            invite_code.save()
        except IntegrityError:
            # The created code was miraculously non-unique.
            continue
        return invite_code


def _generate_code() -> str:
    return "".join(
        random.choices(string.ascii_uppercase, k=settings.INVITE_CODE_LENGTH)
    )


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    """Give all existing verifier users their invite codes if they don't have them
    yet."""

    User = apps.get_model("skole", "User")
    InviteCode = apps.get_model("skole", "InviteCode")

    for user in User.objects.filter(invite_code=None, verified=True):
        create_invite_code(code_model=InviteCode, user=user)


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0047_refactor_invite_code"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]
