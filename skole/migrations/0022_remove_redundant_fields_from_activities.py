# Generated by Django 3.1.5 on 2021-03-16 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('skole', '0021_add_push_notifications'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='course',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='resource',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='school',
        ),
    ]