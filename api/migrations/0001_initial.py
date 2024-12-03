# Generated by Django 5.1.3 on 2024-12-03 21:11

import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_participant', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='api_customuser_set', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='api_customuser_permissions_set', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ModelExam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_exams', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ModelParticipation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('score', models.FloatField(default=0.0)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participations', to='api.modelexam')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='modelexam',
            name='participants',
            field=models.ManyToManyField(related_name='exams', through='api.ModelParticipation', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='modelexam',
            name='questions',
            field=models.ManyToManyField(related_name='exams', to='api.modelquestion'),
        ),
        migrations.CreateModel(
            name='ModelChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='api.modelquestion')),
            ],
        ),
        migrations.CreateModel(
            name='ModelAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answered_at', models.DateTimeField(auto_now_add=True)),
                ('choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='api.modelchoice')),
                ('participation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='api.modelparticipation')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='api.modelquestion')),
            ],
        ),
        migrations.CreateModel(
            name='ModelRanking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('position', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rankings', to='api.modelexam')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rankings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['exam', 'position'],
                'unique_together': {('exam', 'participant')},
            },
        ),
    ]
