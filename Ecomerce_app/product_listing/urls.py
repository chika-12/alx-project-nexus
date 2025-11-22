from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

route = DefaultRouter()
route.register("product_list", views.ProductViewset, basename="product_list")
route.register('favourite', views.FavourViewSet, basename="favourite")
route.register(r'rating', views.RatingsViews, basename='rating')

urlpatterns = [
  path("", include(route.urls))
]