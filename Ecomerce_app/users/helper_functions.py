from rest_framework.response import Response
from rest_framework import status

class HelperClass:
  def __init__(self):
    pass 

  def serialize_data(self, serializer, request):
    serialized_data = serializer(data=request.data)
    if serialized_data.is_valid():
      serialized_data.save()
      return Response({
        "message": "User created successfully",
        "data" :serialized_data.data
      }, status=status.HTTP_201_CREATED)
    else:
      return Response({
        "errors": serialized_data.errors
      }, status=status.HTTP_400_BAD_REQUEST)
  
  def response(self, message, status_data, data=None, access_token=None ,refresh_token=None):
    response_body = {
      "message": message,
      "data" : data
    }
    if refresh_token:
      response_body['refresh_token'] = refresh_token
    if access_token:
      response_body['access_token'] = access_token
    
    return Response(response_body, status=status_data)
  
  def getAll_Users_and_byId(self, model, serializer, deleteAction=None, queryData=None, field_name=None):
    if queryData is None and field_name is None:
      user = model.active.all()
      serialized_data = serializer(user, many=True)
      return self.response("Users retrived successfully", status_data=status.HTTP_200_OK, data=serialized_data.data)
    else:
      user = model.active.filter(**{field_name: queryData}).first()
      if not user:
        return self.response("User not found", status_data=status.HTTP_404_NOT_FOUND)
      if deleteAction == "delete":
        user.delete()
        return self.response("User deleted", status_data=status.HTTP_204_NO_CONTENT)
      elif deleteAction == "deactivate":
        user.is_active = False
        user.save()
        return self.response("User deleted", status_data=status.HTTP_204_NO_CONTENT)
      serialized_data = serializer(user)
      return self.response("User retrived successfully", status_data=status.HTTP_200_OK, data=serialized_data.data)