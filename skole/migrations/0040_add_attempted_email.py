# Generated by Django 3.1.7 on 2021-03-27 10:42

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0039_comment_is_anonymous"),
    ]

    operations = [
        migrations.CreateModel(
            name="AttemptedEmail",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("is_whitelisted", models.BooleanField(default=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
