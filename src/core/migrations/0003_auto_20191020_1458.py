# Generated by Django 2.2.6 on 2019-10-20 14:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_auto_20191012_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.TextField(max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='title',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
