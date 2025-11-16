from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import UsersSerializer, EmailLookupSerializer, LoggingData
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.exceptions import ValidationError
from . import models
from utilities import uuid_verification
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.
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
      "message": "User registered successfully",
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

@swagger_auto_schema(
  method='post',
  operation_description="Log in a user",
  request_body=LoggingData,   
)
@api_view(["POST"])
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


@swagger_auto_schema(
  method='get',
  security=[{'Bearer': []}],  # this tells Swagger the endpoint requires Bearer token
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_allUsers(request):
  """
  Gets all registered users
  """

  data = models.Users.objects.all()
  serialized = UsersSerializer(data, many=True)
  return Response({
    "messege": "data retrived successfully",
    "data": serialized.data,
  }, status=status.HTTP_200_OK)

@api_view(["GET"])
def user_by_id(request, user_id):
  """
   Get a single user by ID
  """
  if not uuid_verification(user_id):
    return Response({
      "message": "Invalid Id"
    }, status=status.HTTP_400_BAD_REQUEST)

  try:
    user = models.Users.objects.get(id=user_id)
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
  

@swagger_auto_schema(
  method='post',
  operation_description="Register a new user",
  request_body=EmailLookupSerializer
)
@api_view(["POST"])
def get_user_by_email(request):

  
  email = request.data.get('email')
  if  not email:
    return Response({
      "message": "Email required"
    }, status=status.HTTP_400_BAD_REQUEST)    
  try:
    user = models.Users.objects.get(email=email)
  except models.Users.DoesNotExist:
    return Response({
      "message": "No user with such email"
    }, status=status.HTTP_404_NOT_FOUND)
  
  serialize = UsersSerializer(user)
  return Response({
    "data": serialize.data
  }, status=status.HTTP_200_OK)

@api_view(["DELETE"])
def delete_user_byId(request, user_id):
  try:
    user = models.Users.objects.get(id=user_id)
  except models.Users.DoesNotExist:
    return Response

