from django.db import models
from catogory.models import Category
from brand.models import Brand
from UserAccounts.models import User

class Products(models.Model):
    product_name = models.CharField(max_length=100, null=False)
    product_description = models.TextField(max_length=3000, null=False)
    product_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    product_brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    offer_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

