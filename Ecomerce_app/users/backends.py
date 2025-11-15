from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

Users = get_user_model()
class EmailBackend(ModelBackend):
  def aauthenticate(self, request, email = None, password = None, **kwargs):
    if email is None:
      raise ValueError("Please input your email address")
    
    try:
      user = Users.objects.get(email=email)
    except Users.DoesNotExist:
      return None
    if user.check_password(password):
      return user
    return None
    