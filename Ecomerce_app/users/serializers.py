from rest_framework import serializers 
from .models import Users, Profile 
from django.contrib.auth.password_validation import validate_password

class UsersSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

  class Meta:
    model = Users
    fields = ['id', 'first_name', 'last_name', 'email', 'password', 'role', 'last_login', 'date_created', 'date_updated']
  
  def create(self, validated_data):
    password = validated_data.pop('password')
    validated_data['role'] = 'admin'
    validated_data['is_staff'] = True
    validated_data['is_verified'] = True
    user = Users.objects.create_user(password=password, **validated_data)
    return user

class EmailLookupSerializer(serializers.Serializer):
  email = serializers.EmailField()
    
class LoggingData(serializers.Serializer):
  email = serializers.EmailField()
  password = serializers.CharField()

class ProfileSerializer(serializers.ModelSerializer):
  #profile_photo = serializers.SerializerMethodField()
  #profile_photo = serializers.FileField(required=False)

  class Meta:
    model = Profile
    fields = "__all__"
    extra_kwargs = {
      "profile_photo": {"required": False}
    }
  
  def to_representation(self, instance):
    data = super().to_representation(instance)

    # Convert Cloudinary field to full URL
    if instance.profile_photo and hasattr(instance.profile_photo, 'url'):
      data["profile_photo"] = instance.profile_photo.url
    else:
      data["profile_photo"] = None

    return data
