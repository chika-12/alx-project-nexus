from rest_framework import serializers
from .models import ProductModel, Favourite, Ratings
from rest_framework.validators import UniqueTogetherValidator
import random
from django.contrib.auth import get_user_model
User = get_user_model()


class RatingSerializer(serializers.ModelSerializer):
  class Meta:
    model = Ratings
    fields = "__all__"
    validators = [
      UniqueTogetherValidator(
      queryset=Ratings.objects.all(),
      fields=['user', 'product'],
      message="You have already rated this product"
      )
    ]
  
  def validate_rate_value(self, value):
    if value > 5 or value < 1:
      raise serializers.ValidationError("Rating must be between 1 and 5")
    return value   

class ProductSerializers(serializers.ModelSerializer):
  sku = serializers.CharField(read_only=True)
  ratings = RatingSerializer(source='product_rating', many=True, read_only=True)
  product_image = serializers.SerializerMethodField()

  class Meta:
    model = ProductModel
    fields = "__all__"

  
  def get_product_image(self, obj):
    if obj.product_image:
      return obj.product_image.build_url()  # <-- returns full Cloudinary URL
    return None
  
  def validate_name(self, value):
    if len(value) < 3:
      raise serializers.ValidationError("Product name must be at least 3 characters long.")
    if ProductModel.objects.filter(name=value).exists():
      raise serializers.ValidationError("Product already exist")
    return value
  
  def validate_category(self, value):
    if len(value) < 3:
      raise serializers.ValidationError("Category must be at least 3 characters long.")
    return value

  def validate(self , attrs):
    expiry_date = attrs.get('expiry_date') 
    manufactured_date = attrs.get('manufactured_date')
    if expiry_date and manufactured_date:
      if expiry_date <= manufactured_date:
        raise serializers.ValidationError("Expiry date cannot be earlier than manufactured date.")
    return attrs

  def create(self, validated_data):
    validated_data['sku']= (
      validated_data['name'][:3].upper() + 
      validated_data['category'][:3].upper() + 
      str(random.randint(10000, 99999))
    )
    return super().create(validated_data)

class FavouriteSerializers(serializers.ModelSerializer):
  product = ProductSerializers(read_only=True, source='product_id')
  
  class Meta:
    model = Favourite
    fields = ["id", "product", "product_id", "user_id", 'date_added']

  def validate_product_id(self, value):
    user = self.context['request'].user
    try:
      user = User.objects.get(email=user)
    except User.DoesNotExist:
      raise serializers.ValidationError("Invalid User")
    
    if Favourite.objects.filter(user_id=user, product_id=value).exists():
      raise serializers.ValidationError("Product already exist in your favourite list")
    return value

