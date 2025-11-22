from django.db import models
import uuid
from django.conf import settings
# Create your models here.

STATUS_CHOICES = [
  ("ACTIVE", "Active"),
  ("OUT_OF_STOCK", "Out of Stock"),
  ("DISCONTINUED", "Discontinued"),
  ("INACTIVE", "Inactive"),
]
RATE_CHOICES = [
  (1, 1),
  (2, 2),
  (3, 3),
  (4, 4),
  (5, 5),
]
class ProductModel(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=367, blank=False, null=False)
  sku = models.CharField(max_length=267, blank=False, null=False)
  category = models.CharField(max_length=247, null=False, blank=False)
  manufactured_date = models.DateField()
  expiry_date = models.DateField()
  product_image = models.URLField(max_length=1000, null=True, blank=True)
  description = models.TextField()
  price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
  stock = models.IntegerField()
  status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='ACTIVE')
  date_added = models.DateTimeField(auto_now=True)
  class Meta:
    indexes = [
      models.Index(fields=['category', 'status']),
      models.Index(fields=['price', 'date_added']),
    ]


class Favourite(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favourite')
  product_id = models.ForeignKey('ProductModel', on_delete=models.CASCADE, related_name='favourited_by')
  date_added = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ("user_id", "product_id")
    ordering = ["-date_added"]
  
  def __str__(self):
    return f"{self.user.username} -> {self.product.name}"

class Ratings(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rating')
  product= models.ForeignKey('ProductModel', on_delete=models.CASCADE, related_name='product_rating')
  rate_value = models.IntegerField(choices=RATE_CHOICES) 
  comment = models.TextField()
  date_added = models.DateTimeField(auto_now=True)
  
  class Meta:
    unique_together = ("user", "product")
