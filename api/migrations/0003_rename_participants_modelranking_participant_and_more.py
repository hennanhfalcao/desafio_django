# Generated by Django 5.1.3 on 2024-11-30 07:14

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_modelranking'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='modelranking',
            old_name='participants',
            new_name='participant',
        ),
        migrations.AlterUniqueTogether(
            name='modelranking',
            unique_together={('exam', 'participant')},
        ),
    ]
