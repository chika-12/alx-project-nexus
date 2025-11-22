from rest_framework.permissions import BasePermission

class OnlyAdminCanPost(BasePermission):
  def has_permission(self, request, view):
    if request.method == "POST" or request.method == "PATCH":
      return request.user and request.user.role == 'admin'
    return True

class NoUpdateForFavourite(BasePermission):
  def has_permission(self, request, view):
    if request.method == "PATCH" or request.method== "PUT":
      return False
    return True