# Generated by Django 3.1.5 on 2021-02-13 11:41

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skole', '0005_add_slug_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='codes',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=30), blank=True, default=list, error_messages={'item_invalid': 'One of the course codes is invalid.'}, size=10),
        ),
    ]