from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
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


def allowed_roles(roles):
  def decorator(view_func):
    view_func.allowed_roles = roles
    return view_func
  return decorator


#Sign up
@swagger_auto_schema(
  method='post',
  operation_description="Register a new user",
  request_body=UsersSerializer,

  responses={
    201: openapi.Response(
      description="User registered successfully",
      schema=UsersSerializer
    ),
    400: "Validation error"
  }
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
  """
    Register a new user.
    Accepts: first_name, last_name, email, password, role
    Returns: user info (without password)
  """
  serialized = UsersSerializer(data=request.data)
  if serialized.is_valid():
    user = serialized.save()
    return Response({
      "message": "User registered successfully. Please check your email and verify your account",
      "user": {
        "id": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role,
      }
    }, status=status.HTTP_201_CREATED)
  else:
    return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST) 


#Login
@swagger_auto_schema(
  method='post',
  operation_description="Log in a user",
  request_body=LoggingData,   
)
@api_view(["POST"])
@permission_classes([AllowAny])
def loging(request):
  """
  Authenticate a user and return JWT tokens
  """
  email = request.data.get('email')
  password = request.data.get('password')

  if not password or not email:
    return Response({
      "message": "password required and email"
    }, status=status.HTTP_400_BAD_REQUEST)
  
  
  user = authenticate(request, password=password, email=email)
  if user is None:
    return Response({
      "message": "Invalid email or password"
    }, status=status.HTTP_401_UNAUTHORIZED)
  
  token = RefreshToken.for_user(user)
  serialized = UsersSerializer(user)

  return Response({
    "message": "Login successful",
    "user": serialized.data,
    "access_token": str(token.access_token),
    "refresh_token": str(token),
  }, status=status.HTTP_200_OK)


#Get all users
@swagger_auto_schema(
  method='get',
  security=[{'Bearer': []}],  # this tells Swagger the endpoint requires Bearer token
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, RolePermissionFactory(['admin', 'manager'])])
@allowed_roles(['admin'])
def get_allUsers(request):
  """
  Gets all registered users
  """
  #get_allUsers.allowed_roles = ["admin"]

  data = models.Users.active.all()
  serialized = UsersSerializer(data, many=True)
  return Response({
    "messege": "data retrived successfully",
    "data": serialized.data,
  }, status=status.HTTP_200_OK)




#Get user by Id
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_by_id(request, user_id):
  """
   Get a single user by ID
  """
  if not uuid_verification(user_id):
    return Response({
      "message": "Invalid Id"
    }, status=status.HTTP_400_BAD_REQUEST)

  try:
    user = models.Users.active.get(id=user_id)
  except models.Users.DoesNotExist:
    return Response({
      "message": "User not found",
    }, status=status.HTTP_404_NOT_FOUND)
  except ValidationError:
    return Response({
      "message": "Invalid Id"
    }, status=status.HTTP_400_BAD_REQUEST)
  serialize = UsersSerializer(user)
  return Response({
    "message": "User retrived successfully",
    "data": serialize.data,
  }, status=status.HTTP_200_OK)
  

#Get user by email(admin)
@swagger_auto_schema(
  method='post',
  operation_description="Get user by email",
  request_body=EmailLookupSerializer
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, RolePermissionFactory(['admin', 'manager'])])
@allowed_roles(['admin'])
def get_user_by_email(request):
  
  email = request.data.get('email')
  if  not email:
    return Response({
      "message": "Email required"
    }, status=status.HTTP_400_BAD_REQUEST)    
  try:
    user = models.Users.active.get(email=email)
  except models.Users.DoesNotExist:
    return Response({
      "message": "No user with such email"
    }, status=status.HTTP_404_NOT_FOUND)
  
  serialize = UsersSerializer(user)
  return Response({
    "data": serialize.data
  }, status=status.HTTP_200_OK)
#get_user_by_email.allowed_roles = ["admin"]


#For admins only
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, RolePermissionFactory(['admin', 'manager'])])
@allowed_roles(['admin'])
def delete_user_byId(request, user_id):
  if not uuid_verification(user_id):
    return Response({
      "message": "Invalid Id"
    }, status=status.HTTP_400_BAD_REQUEST)
  
  try:
    user = models.Users.objects.get(id=user_id)
  except models.Users.DoesNotExist:
    return Response({
      "message": "User does not exist"
    }, status=status.HTTP_404_NOT_FOUND)
  user.delete()
  return Response({
    "message": "Account deleted"
  }, status=status.HTTP_204_NO_CONTENT)
#delete_user_byId.allowed_roles = ["admin"]


#Deactivate users
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deactivate_users(request, user_id):
  if not uuid_verification(user_id):
    return Response({
      "message": "Invalid Id"
    }, status=status.HTTP_400_BAD_REQUEST)
  
  try:
    user = models.Users.objects.get(id=user_id)
  except models.Users.DoesNotExist:
    return Response({
      "message": "User not found"
    }, status=status.HTTP_404_NOT_FOUND)
  user.is_active = False
  user.save()
  return Response({
    "message": "Account deleted"
  }, status=status.HTTP_204_NO_CONTENT)


#deactivate users by email(admin)
@swagger_auto_schema(
  method = 'delete',
  operation_description = "delete user by email",
  request_body= EmailLookupSerializer
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, RolePermissionFactory(['admin', 'manager'])])
@allowed_roles(['admin'])
def deactivate_by_email(request):
  email = request.data.get('email')
  try:
    user = models.Users.objects.get(email=email)
  except models.Users.DoesNotExist:
    return Response({
      "message": "user not found"
    }, status=status.HTTP_404_NOT_FOUND)
  user.is_active = False
  user.save()
  return Response({
    "message": "user deleted successfully"
  }, status=status.HTTP_204_NO_CONTENT)
#deactivate_by_email.allowed_roles = ["admin"]


@api_view(["POST"])
@permission_classes([IsAuthenticated, RolePermissionFactory(['admin', 'manager'])]) 
@allowed_roles(['admin']) # To be changed to admin
def reactivate_users_byEmail(request):
  email = request.data.get("email")
  if email is None:
    return Response({
      "message": "Email required"
    }, status=status.HTTP_400_BAD_REQUEST)
  
  user = models.Users._default_manager.filter(email__iexact=email).first()  
  if user is None:
    return Response({
      "message":"User not found"
    }, status=status.HTTP_404_NOT_FOUND)
  
  user.is_active=True
  user.save()
  serialize = UsersSerializer(user)
  return Response({
    "message": "User reactivated",
    "data": serialize.data
  }, status=status.HTTP_200_OK)
#reactivate_users_byEmail.allowed_roles = ["admin"]


#UserProfile
@swagger_auto_schema(
  method = "get",
  security=[{'Token': []}],
  operation_description="Get user profile",
  #request_body= "None"
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def userProfile(request):
  user = request.user
  try:
    userProfile = models.Profile.objects.get(user_id=user)
    profileuser = models.Users.active.get(email=user)
  except models.Users.DoesNotExist:
    return Response({
      "message": "No user found"
    }, status=status.HTTP_404_NOT_FOUND)
  except models.Profile.DoesNotExist:
    return Response({
      "message": "User profile not found"
    }, status=status.HTTP_404_NOT_FOUND)
  
  if not user.is_verified:
    return Response({
      "message": "You have not been verified"
    }, status=status.HTTP_401_UNAUTHORIZED)
  
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
    return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

  data = signing.loads(token, salt='email-verification', max_age=3600)
  print(data)
  # if data != :
  #   return Response({"message": "Invalid token for this email", })
  
  try:
    user = models.Users.objects.get(email=email)
    user.is_verified = True
    user.save()
    return Response({"message": "Email verification successfull"})
  except signing.SignatureExpired:
    return Response({"message": "Verification link expired."})
  except signing.BadSignature:
    return Response({"message": "Invalid Token"})

@api_view(["POST"])
@permission_classes([IsAuthenticated, RolePermissionFactory(["admin"])])
def upgrade_user(request):

  userRole = request.data.get("role")
  email = request.data.get('email')

  try:
    user = models.Users.objects.get(email=email)
  except models.Users.DoesNotExist:
    return Response({"message": "User not found"})
  
  if user.is_staff:
    if user.role!= userRole:
      user.role = userRole
      user.save()
      email_data = get_upgrade_email_content(user)
      emailService(**email_data)
      return Response({"message": f"User has been upgraded to {userRole}"})
    else:
      return Response({"message": f"User is already an/a {userRole}"})
  else:
    return Response({"message": "Only staff users can be upgraded. Please assign staff status to the user first."})
  

