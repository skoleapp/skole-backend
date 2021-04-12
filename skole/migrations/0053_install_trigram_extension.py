from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    """Install the Postgres extension that allows to use `TrigramSimilarity` func."""

    dependencies = [
        ("skole", "0052_whitelist_existing_user_emails"),
    ]

    operations = [
        TrigramExtension(),
    ]
