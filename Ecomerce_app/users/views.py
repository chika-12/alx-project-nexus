from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import UsersSerializer, EmailLookupSerializer, LoggingData, ProfileSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.exceptions import ValidationError
from . import models
from .permissions import  RolePermissionFactory # AdminPermissions
from utilities import uuid_verification
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core import signing
from .emailServices import emailService
from .messages import get_upgrade_email_content
from .utilities import selectRequiredFields
from .helper_functions import HelperClass
from rest_framework.parsers import MultiPartParser, FormParser
helper = HelperClass()

#Sign up
@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
  """
    Register a new user.
    Accepts: first_name, last_name, email, password, role
    Returns: user info (without password)
  """
  return helper.serialize_data(UsersSerializer, request)
  

#Login
@api_view(["POST"])
@permission_classes([AllowAny])
def loging(request):
  """
  Authenticate a user and return JWT tokens
  """
  email = request.data.get('email')
  password = request.data.get('password')
  if not password or not email:
    return helper.response("password required and email", status_data=status.HTTP_400_BAD_REQUEST)
    
  user = authenticate(request, password=password, email=email)
  if user is None:
    return helper.response("Invalid email or password", status_data=status.HTTP_401_UNAUTHORIZED)
  
  token = RefreshToken.for_user(user)
  serialized = UsersSerializer(user)

  return helper.response("Login successful", status_data=status.HTTP_200_OK, data=serialized.data, access_token=str(token.access_token), refresh_token=str(token))

#Get all users
@api_view(["GET"])
@permission_classes([IsAuthenticated, RolePermissionFactory(['admin', 'manager'])])
def get_allUsers(request):
  """
  Gets all registered users
  """
  return helper.getAll_Users_and_byId(models.Users, UsersSerializer)
 
#Get user by Id
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_by_id(request, user_id):
  """
   Get a single user by ID
  """
  if not uuid_verification(user_id):
    return helper.response("Invalid Id", status_data=status.HTTP_400_BAD_REQUEST)
  
  return helper.getAll_Users_and_byId(models.Users, UsersSerializer, queryData=user_id, field_name='id')

  
#Get user by email(admin)
@api_view(["POST"])
@permission_classes([IsAuthenticated, RolePermissionFactory(['admin', 'manager'])])
def get_user_by_email(request):
  
  email = request.data.get('email')
  if  not email:
    return helper.response("Email required", status_data=status.HTTP_400_BAD_REQUEST)    
  return helper.getAll_Users_and_byId(models.Users, UsersSerializer, queryData=email, field_name="email")


#For admins only
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, RolePermissionFactory(['admin', 'manager'])])
def delete_user_byId(request, user_id):
  if not uuid_verification(user_id):
    return helper.response("Invalid Id", status_data=status.HTTP_400_BAD_REQUEST)
  
  return helper.getAll_Users_and_byId(models.Users, UsersSerializer, deleteAction="delete", queryData=user_id, field_name="id")
  

#Deactivate users
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deactivate_users(request, user_id):
  if not uuid_verification(user_id):
    return helper.response("Invalid Id", status_data=status.HTTP_400_BAD_REQUEST)
  
  return helper.getAll_Users_and_byId(models.Users, UsersSerializer, deleteAction="deactivate", queryData=user_id, field_name="id")
  

#deactivate users by email(admin)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, RolePermissionFactory(['admin', 'manager'])])
def deactivate_by_email(request):
  email = request.data.get('email')

  return helper.getAll_Users_and_byId(models.Users, UsersSerializer, deleteAction="deactivate", queryData=email, field_name="email")

@api_view(["POST"])
@permission_classes([IsAuthenticated, RolePermissionFactory(['admin', 'manager'])]) 
def reactivate_users_byEmail(request):
  email = request.data.get("email")
  if email is None:
    return helper.response("Email required", status_data=status.HTTP_400_BAD_REQUEST)
  
  user = models.Users._default_manager.filter(email__iexact=email).first()  
  if user is None:
    return helper.response("User not found", status_data=status.HTTP_404_NOT_FOUND)
  
  user.is_active=True
  user.save()
  serialize = UsersSerializer(user)
  return helper.response("User reactivated", status_data=status.HTTP_200_OK, data=serialize.data)

#UserProfile
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def userProfile(request):
  user = request.user
  try:
    userProfile = models.Profile.objects.get(user_id=user)
    profileuser = models.Users.active.get(email=user)
  except models.Users.DoesNotExist:
    return helper.response("No user found", status_data=status.HTTP_404_NOT_FOUND)
  except models.Profile.DoesNotExist:
    return helper.response("User profile not found", status_data=status.HTTP_404_NOT_FOUND)
  
  # if not user.is_verified:
  #   return Response({
  #     "message": "You have not been verified"
  #   }, status=status.HTTP_401_UNAUTHORIZED)
  
  serialize = ProfileSerializer(userProfile)
  data = UsersSerializer(profileuser)
  return Response({
    "message": "successful",
    "data":{
      "userData": data.data,
      "profile":{
        "profileData": serialize.data
      }
    },
  })

@api_view(["GET"])
@permission_classes([AllowAny])
def verify_user(request):
  email = request.GET.get('email')
  token = request.GET.get('token')
  if token is None or email is None:
    return helper.response("Invalid request", status_data=status.HTTP_400_BAD_REQUEST)

  data = signing.loads(token, salt='email-verification', max_age=3600)  
  try:
    user = models.Users.objects.get(email=email)
    user.is_verified = True
    user.save()
    return helper.response("Email verification successfull", status_data=status.HTTP_200_OK)
  except signing.SignatureExpired:
    return helper.response("Verification link expired.", status_data=status.HTTP_400_BAD_REQUEST)
  except signing.BadSignature:
    return helper.response("Invalid Token", status_data=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated, RolePermissionFactory(["admin"])])
def upgrade_user(request):
  userRole = request.data.get("role")
  email = request.data.get('email')

  try:
    user = models.Users.objects.get(email=email)
  except models.Users.DoesNotExist:
    return helper.response("User not found")
  
  if user.is_staff:
    if user.role!= userRole:
      user.role = userRole
      user.save()
      email_data = get_upgrade_email_content(user)
      emailService(**email_data)
      return helper.response(f"User has been upgraded to {userRole}", status_data=status.HTTP_200_OK)
    else:
      return helper.response(f"User is already an/a {userRole}", status_data=status.HTTP_304_NOT_MODIFIED)
  else:
    return helper.response("Only staff users can be upgraded. Please assign staff status to the user first.", status_data=status.HTTP_304_NOT_MODIFIED)
  
@api_view(["POST"])
@permission_classes([IsAuthenticated, RolePermissionFactory(["admin"])])
def upgrade_to_staff(request):
  email = request.data.get("email")
  if not email:
    return helper.response("Email requiered", status_data=status.HTTP_400_BAD_REQUEST)
  
  try:
    user = models.Users.active.get("email")
  except models.Users.DoesNotExist:
    return helper.response("User not found", status_data=status.HTTP_404_NOT_FOUND)
  user.is_staff = True
  user.is_verified = True
  user.save()
  return helper.response("User has been upgraded to staff status", status_data=status.HTTP_200_OK)

@api_view(["PATCH"])
@parser_classes([MultiPartParser, FormParser])
def profile_update(request):
    profile = request.user.profile
    print("FILES:", request.FILES)
    print("DATA:", request.data)


    if "profile_photo" in request.FILES:
        profile.profile_photo = request.FILES["profile_photo"]

    serializer = ProfileSerializer(profile, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Profile updated", "data": serializer.data})

    return Response(serializer.errors, status=400)
