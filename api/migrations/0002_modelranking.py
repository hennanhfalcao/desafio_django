# Generated by Django 5.1.3 on 2024-11-30 07:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelRanking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('position', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rankings', to='api.modelexam')),
                ('participants', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rankings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['exam', 'position'],
                'unique_together': {('exam', 'participants')},
            },
        ),
    ]
