# from django.db import models
# from UserAccounts.models import User


# class Products(models.Model):
#     product_name = models.CharField(max_length=100, null=False)
#     product_description = models.TextField(max_length=5000, null=False)
#     product_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
#     product_brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
#     price = models.DecimalField(max_digits=8, decimal_places=2)
#     offer_price = models.DecimalField(max_digits=8, decimal_places=2)
#     is_active = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now_add=True)

#     def percentage_discount(self):
#         return int(((self.price - self.offer_price) / self.price) * 100)
    
#     def average_rating(self):
#         reviews = self.reviews.all()
#         if reviews:
#             return sum(review.rating for review in reviews) / reviews.count()
#         return 0

#     def __str__(self):
#         return f"{self.product_brand.brand_name}-{self.product_name}"



# class Product_Variant(models.Model):
#     product = models.ForeignKey(Products, on_delete=models.CASCADE)
#     colour_name = models.CharField(null=False)
#     variant_stock = models.PositiveIntegerField(null=False,default=0)
#     variant_status = models.BooleanField(default=True)
#     colour_code = models.CharField(null=False)

# class Product_images(models.Model):
#     product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
#     images = models.ImageField(upload_to="product_images", default="product/no_img.png")

#     def __str__(self):
#         return f"Image for {self.product.product_name}"

#     def __str__(self):
#         return self.category_name


# class Product_variant_images(models.Model):
#     product_variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
#     images = models.ImageField(
#         upload_to="product_images", default=r"product/no_img.png"
#     )

#     def __str__(self):
#         return f"Image for {self.product_variant.product.product_name} - {self.product_variant.colour_name}"
    


    

    
    
    

