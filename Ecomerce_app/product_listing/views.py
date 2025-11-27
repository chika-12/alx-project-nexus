from django.shortcuts import render
from . import models
from . import serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .utility import OnlyAdminCanPost, NoUpdateForFavourite
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django.conf import settings
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from django.core.cache import cache
User = get_user_model()

# Create your views here.

class ProductViewset(ModelViewSet):
  queryset = models.ProductModel.objects.all()
  serializer_class = serializers.ProductSerializers
  permission_classes = [IsAuthenticated]
  parser_classes = [MultiPartParser, FormParser]
  filter_backends = [
    DjangoFilterBackend,
    filters.SearchFilter,
    filters.OrderingFilter
  ]
  # Search fields
  search_fields = ['name', 'sku', 'description']
  # Filtering fields
  filterset_fields = ['category', 'status']
  # Sorting fields
  ordering_fields = ['price', 'date_added', 'name']

  def list(self, request, *args, **kwargs):
    cache_key = f"products-list:{request.get_full_path()}"
    cached_response = cache.get(cache_key)
    if cached_response:
      return Response({
        "message": "from cache",
        "data": cached_response
      })
    queryset = self.filter_queryset(self.get_queryset())
    serializer = self.get_serializer(queryset, many=True)
    cache.set(cache_key, serializer.data, timeout=300)
    return Response(serializer.data)
  
  def clear_products_cache(self):
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys("products-list:*")
    if keys:
      redis_conn.delete(*keys)

  def create(self, request, *args, **kwargs):
    print("FILES:", request.FILES)
    print("DATA:", request.data)
    response = super().create(request, *args, **kwargs)
    cache.clear()
    return response

  def update(self, request, *args, **kwargs):
    response = super().update(request, *args, **kwargs)
    cache.clear()
    return response

  def destroy(self, request, *args, **kwargs):
    response = super().destroy(request, *args, **kwargs)
    cache.clear()
    return response




class FavourViewSet(ModelViewSet):
  queryset = models.Favourite.objects.all()
  serializer_class = serializers.FavouriteSerializers
  permission_classes = [IsAuthenticated, AllowAny,NoUpdateForFavourite]

  def get_queryset(self):
    user = User.objects.get(email=self.request.user)
    user_id = user.id
    return models.Favourite.objects.filter(user_id=user_id)

class RatingsViews(ModelViewSet):
  queryset = models.Ratings.objects.all()
  serializer_class = serializers.RatingSerializer
  permission_classes = [IsAuthenticatedOrReadOnly]
