# Generated by Django 3.1.5 on 2021-03-11 14:05

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0015_add_school_to_activity"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resource",
            name="slug",
            field=autoslug.fields.AutoSlugField(
                always_update=True,
                default=None,
                editable=False,
                null=True,
                populate_from="__str__",
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="slug",
            field=autoslug.fields.AutoSlugField(
                always_update=True,
                default=None,
                editable=False,
                null=True,
                populate_from="username",
                unique=True,
            ),
        ),
    ]
