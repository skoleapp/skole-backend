# Generated by Django 3.1.5 on 2021-02-23 12:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skole', '0011_add_email_subscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketingEmailSender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_email', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MarketingEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=150)),
                ('email_type', models.CharField(choices=[('product-update', 'Product Update'), ('blog-post', 'Blog Post')], max_length=50)),
                ('contents', models.FileField(upload_to='marketing_emails')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('sent', models.BooleanField(default=False)),
                ('from_email', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='skole.marketingemailsender')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
