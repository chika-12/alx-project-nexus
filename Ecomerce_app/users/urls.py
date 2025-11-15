from django.urls import path
from . import views
urlpatterns = [
  path("signUp/", views.register_user, name="signUp"),
]