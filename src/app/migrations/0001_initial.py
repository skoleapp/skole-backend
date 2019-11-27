# Generated by Django 2.2.7 on 2019-11-27 20:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('bio', models.TextField(blank=True, max_length=2000, null=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='uploads/avatars')),
                ('is_staff', models.BooleanField(default=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CommentThread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('code', models.CharField(blank=True, max_length=30, null=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('comment_thread', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.CommentThread')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_courses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='uploads/resources')),
                ('date', models.DateField()),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='app.Course')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_resources', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='schools', to='app.City')),
            ],
        ),
        migrations.CreateModel(
            name='SchoolType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='VoteHolder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('schools', models.ManyToManyField(related_name='subjects', to='app.School')),
            ],
        ),
        migrations.AddField(
            model_name='school',
            name='school_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='schools', to='app.SchoolType'),
        ),
        migrations.CreateModel(
            name='ResourcePart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_thread', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.CommentThread')),
                ('resource', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resource_parts', to='app.Resource')),
            ],
        ),
        migrations.AddField(
            model_name='resource',
            name='resource_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.ResourceType'),
        ),
        migrations.AddField(
            model_name='resource',
            name='vote_holder',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='resource', to='app.VoteHolder'),
        ),
        migrations.AddField(
            model_name='course',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='app.School'),
        ),
        migrations.AddField(
            model_name='course',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='app.Subject'),
        ),
        migrations.AddField(
            model_name='course',
            name='vote_holder',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='course', to='app.VoteHolder'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=10000)),
                ('attachment', models.FileField(null=True, upload_to='uploads/comment_attachments')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('comment_thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_replies', to='app.CommentThread')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to=settings.AUTH_USER_MODEL)),
                ('vote_holder', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='comment', to='app.VoteHolder')),
            ],
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cities', to='app.Country'),
        ),
        migrations.AddField(
            model_name='user',
            name='schools',
            field=models.ManyToManyField(to='app.School'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'upvote'), (-1, 'downvote')])),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to=settings.AUTH_USER_MODEL)),
                ('vote_holder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='app.VoteHolder')),
            ],
            options={
                'unique_together': {('vote_holder', 'creator')},
            },
        ),
    ]
