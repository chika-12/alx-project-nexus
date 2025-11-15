from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UsersSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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
