# Generated by Django 2.2.6 on 2019-11-02 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_user_avatar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='faculty',
            name='university',
        ),
        migrations.RemoveField(
            model_name='subject',
            name='faculty',
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/avatars'),
        ),
        migrations.DeleteModel(
            name='Facility',
        ),
        migrations.DeleteModel(
            name='Faculty',
        ),
    ]
