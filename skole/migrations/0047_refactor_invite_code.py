from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0046_nullable_fields_to_blank"),
    ]

    operations = [
        migrations.RemoveField(model_name="ReferralCode", name="user"),
        migrations.RenameModel(
            old_name="ReferralCode",
            new_name="InviteCode",
        ),
        migrations.AddField(
            model_name="InviteCode",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=models.SET_NULL,
                related_name="invite_code",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RenameField(
            model_name="user",
            old_name="used_referral_code",
            new_name="used_invite_code",
        ),
        migrations.AlterField(
            model_name="user",
            name="used_invite_code",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.PROTECT,
                related_name="invited_users",
                to="skole.invitecode",
            ),
        ),
    ]
