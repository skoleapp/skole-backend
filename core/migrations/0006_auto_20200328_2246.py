# Generated by Django 2.2.7 on 2020-03-28 22:46

import core.utils.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20200327_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='attachment',
            field=models.ImageField(blank=True, upload_to='uploads/attachments', validators=[core.utils.validators.ValidateFileSizeAndType(3, ['image/jpeg', 'image/png'])]),
        ),
    ]
