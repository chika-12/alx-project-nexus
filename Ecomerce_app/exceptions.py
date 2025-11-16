from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
  response = exception_handler(exc, context)

  if response is None and getattr(exc, 'status_code', None) == 404:
    return Response(
      {"message": "API endpoint not found"}, 
      status=status.HTTP_404_NOT_FOUND
    )
  
  return response