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
    featured = models.BooleanField(default=False)
   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    
    
    def offer_price_percentage(self):
        return ((self.price-self.offer_price)/self.price)*100
    
    def __str__(self):
        return f"{self.product_brand.brand_name}-{self.product_name}"
    
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='variants')
    variant_name = models.CharField(max_length=100, null=False)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    variant_stock = models.PositiveIntegerField(null=False,default=0)
    colour_code = models.CharField(null=False,default='default_color')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        
        return f"{self.variant_name} - {self.product.product_name}"
    
class ProductVariantImages(models.Model):
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to="product_images", default="static/UserSide/img/No_Images_available.png"
    )

    def __str__(self):
        return f"Image for {self.product_variant.product.product_name} - {self.product_variant.variant_name}"


