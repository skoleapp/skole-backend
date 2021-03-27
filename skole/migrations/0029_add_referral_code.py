# Generated by Django 3.1.7 on 2021-03-26 11:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skole', '0028_remove_marketing_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferralCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=8, unique=True)),
                ('usages', models.PositiveIntegerField(default=settings.REFERRAL_CODE_INITIAL_USAGES)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referral_codes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='user',
            name='used_referral_code',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='referred_users', to='skole.referralcode'),
        ),
    ]