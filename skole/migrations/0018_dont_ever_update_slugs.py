# Generated by Django 3.1.5 on 2021-03-14 12:59

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('skole', '0017_force_null_course_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=None, editable=False, null=True, populate_from='__str__', unique=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=None, editable=False, null=True, populate_from='__str__', unique=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=None, editable=False, null=True, populate_from='__str__', unique=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=None, editable=False, null=True, populate_from='__str__', unique=True),
        ),
        migrations.AlterField(
            model_name='resourcetype',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=None, editable=False, null=True, populate_from='__str__', unique=True),
        ),
        migrations.AlterField(
            model_name='school',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=None, editable=False, null=True, populate_from='__str__', unique=True),
        ),
        migrations.AlterField(
            model_name='schooltype',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=None, editable=False, null=True, populate_from='__str__', unique=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=None, editable=False, null=True, populate_from='__str__', unique=True),
        ),
    ]