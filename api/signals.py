from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ModelUserProfile

@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        ModelUserProfile.objects.get_or_create(
            user=instance, defaults={"is_participant": True}
        )
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()