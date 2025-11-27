from django.urls import path
from . import views
urlpatterns = [
  path("signUp/", views.register_user, name="signUp"),
  path("login/", views.loging, name="logging"),
  path("getAllUsers/",views.get_allUsers, name="allusers"),
  path("getUser/<str:user_id>/", views.user_by_id, name="users"),
  path("userByEmail/", views.get_user_by_email, name="userEmail"),
  path("delete/<str:user_id>/", views.delete_user_byId, name="delete"),
  path("userProfile/", views.userProfile, name="profile"),
  path("userDelete/<str:user_id>/", views.deactivate_users, name="deactivate"),
  path("deleteByEmail/", views.deactivate_by_email, name='emailDeactivation'),
  path("reactivate/", views.reactivate_users_byEmail, name="reactivate"),
  path("verify/", views.verify_user,name="verify_user"),
  path("upgradeUser/", views.upgrade_user, name="upgrade"),
  path("makeUserStaff", views.upgrade_to_staff, name="makeStaff"),
  path("update/me/", views.profile_update, name='profile_update'),
]