# Generated by Django 3.1.5 on 2021-02-23 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skole', '0012_add_marketing_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='comment_reply_email_permission',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='course_comment_email_permission',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='resource_comment_email_permission',
            field=models.BooleanField(default=True),
        ),
    ]