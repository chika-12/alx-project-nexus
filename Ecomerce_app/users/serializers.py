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
    validated_data['role'] = 'customer'
    user = Users.objects.create_user(password=password, **validated_data)
    return user

class EmailLookupSerializer(serializers.Serializer):
  email = serializers.EmailField()
class LoggingData(serializers.Serializer):
  email = serializers.EmailField()
  password = serializers.CharField()

class ProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = Profile
    fields = "__all__"
