# Generated by Django 3.2 on 2021-04-26 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0057_track_thread_and_user_views"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="score",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="thread",
            name="score",
            field=models.IntegerField(default=0),
        ),
    ]
