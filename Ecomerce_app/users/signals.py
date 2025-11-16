from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Users, Profile

@receiver(post_save, sender=Users)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user_id=instance, name=f"{instance.first_name} {instance.last_name}")
    print("Profile created")


@receiver(post_save, sender=Users)
def save_user_profile(sender, instance, **kwargs):
  try:
    instance.profile.save()
  except Profile.DoesNotExist:
    # If profile doesn't exist (just in case), create it
    Profile.objects.create(user_id=instance, name=f"{instance.first_name} {instance.last_name}")