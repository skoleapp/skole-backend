# Generated by Django 2.2.7 on 2020-03-15 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='betacode',
            name='user',
        ),
        migrations.AddField(
            model_name='betacode',
            name='usages',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]