from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid

USER_ROLES = [
  ('admin', 'Admin'),
  ('customer', 'Customer'),
  ('vendor', 'Vendor'),
  ('delivery', 'Delivery')
]

class UserManager(BaseUserManager):
  def create_user(self, email, password=None, **extra_fields):
    if not email:
      raise ValueError("User must have an email. Please add an email address")
    
    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user
  
  def create_superuser(self,email, password=None, **extra_fields):

    extra_fields.setdefault('is_staff', True),
    extra_fields.setdefault('is_superuser', True)

    if extra_fields.get('is_staff') is not True:
      raise ValueError("Superuser must be a staff")
    if extra_fields.get('is_superuser') is not True:
      raise ValueError("Superuser must be an admin. Must have is_superuser set to True")
    
    return self.create_user(email, password, extra_fields)

class Users(AbstractBaseUser, PermissionsMixin):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  first_name = models.CharField(max_length=230, blank=False, null=False)
  last_name = models.CharField(max_length=230, blank=False, null=False)
  email = models.EmailField(unique=True)
  is_verified = models.BooleanField(default=False)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)
  date_created = models.DateTimeField(auto_now=True)
  role = models.CharField(max_length=39, choices=USER_ROLES, default='customer')
  date_updated = models.DateTimeField(auto_now=True)

  objects = UserManager()
  
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['first_name', 'last_name']
    