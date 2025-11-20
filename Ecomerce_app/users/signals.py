from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Users, Profile
from .emailServices import emailService
from django.core import signing
@receiver(post_save, sender=Users)
def create_user_profile(sender, instance, created, **kwargs):

  # if getattr(settings, "DISABLE_SIGNALS", False):
  #   return 

  if created:
    Profile.objects.create(user_id=instance, name=f"{instance.first_name} {instance.last_name}", phone_number=0)
    print("Profile created")
    # token = signing.dumps(
    #   {'user_id': str(instance.id)},
    #   salt='email-verification'
    # )
    # subject = "Welcome to ALXEcommerce! Verify Your Email"
    # verification_link = f"http://127.0.0.1:8000/users/verify?email={instance.email}&token={token}"

    # message = f"""
    #   Hi {instance.first_name},

    #   Welcome to ALXEcommerce! We're thrilled to have you on board.

    #   Please verify your email address by clicking the link below:

    #   {verification_link}
    #   This link will expire in 1 hour.

    #   If you did not sign up for ALXEcommerce, please ignore this email.

    #   Happy shopping!

    #   Best regards,
    #   The ALXEcommerce Team
    # """
    # emailService(
    #   subject=subject,
    #   message=message,
    #   from_email="noreply@alxecommerce.com",
    #   recipient_list=[instance.email],
    #   fail_silently=False
    # )    



# @receiver(post_save, sender=Users)
# def save_user_profile(sender, instance, **kwargs):
#   try:
#     instance.profile.save()
#   except Profile.DoesNotExist:
#     # If profile doesn't exist (just in case), create it
#     Profile.objects.create(user_id=instance, name=f"{instance.first_name} {instance.last_name}")