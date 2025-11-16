from django.urls import path
from . import views
urlpatterns = [
  path("signUp/", views.register_user, name="signUp"),
  path("login/", views.loging, name="logging"),
  path("getAllUsers/",views.get_allUsers, name="allusers"),
  path("getUser/<str:user_id>/", views.user_by_id, name="users"),
  path("userByEmail/", views.get_user_by_email, name="userEmail"),
]