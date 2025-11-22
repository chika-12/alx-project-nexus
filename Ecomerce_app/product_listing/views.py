from django.shortcuts import render
from . import models
from . import serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .utility import OnlyAdminCanPost, NoUpdateForFavourite
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.

class ProductViewset(ModelViewSet):
  queryset = models.ProductModel.objects.all()
  serializer_class = serializers.ProductSerializers
  permission_classes = [IsAuthenticated, OnlyAdminCanPost]
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


class FavourViewSet(ModelViewSet):
  queryset = models.Favourite.objects.all()
  serializer_class = serializers.FavouriteSerializers
  permission_class = [IsAuthenticated, AllowAny,NoUpdateForFavourite]

  def get_queryset(self):
    user = User.objects.get(email=self.request.user)
    user_id = user.id
    return models.Favourite.objects.filter(user_id=user_id)

class RatingsViews(ModelViewSet):
  queryset = models.Ratings.objects.all()
  serializer_class = serializers.RatingSerializer
  permission_classes = [IsAuthenticatedOrReadOnly]
