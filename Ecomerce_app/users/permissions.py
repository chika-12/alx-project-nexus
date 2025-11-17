from rest_framework.permissions import BasePermission

# class AdminPermissions(BasePermission):
#   def has_permission(self, request, view):
#     allowed_roles = getattr(view, 'allowed_roles', None)
#     if not request.user.is_authenticated:
#       return False
#     print(allowed_roles)
#     if allowed_roles is not None:
      
#       return request.user.role in allowed_roles

#      # Default fallback
#     #return request.user.role in ["admin", "manager"]



# Permission class that accepts allowed roles
class RolePermission(BasePermission):
  def __init__(self, allowed_roles=None):
    #if allowed_roles is None:
      #allowed_roles = ['admin']  # default
    self.allowed_roles = allowed_roles

  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    return request.user.role in self.allowed_roles


# Helper to make DRF happy (because permission_classes expects a class, not an instance)
def RolePermissionFactory(allowed_roles):
  class _RolePermission(RolePermission):
    def __init__(self):
      super().__init__(allowed_roles=allowed_roles)
  return _RolePermission
