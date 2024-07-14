# from django.db import models

# # Create your models here.
# #from django.db import models
# from django.utils.text import slugify


# class Category(models.Model):
#     category_name = models.CharField(max_length=40, unique=True)
#     slug = models.SlugField(max_length=100, unique=True)
  
#     is_available = models.BooleanField(default=True)

#     class Meta:
#         verbose_name = "Category"
#         verbose_name_plural = "categories"


#     # Capitalize first letters and slugify the product_name field
#     def save(self, *args, **kwargs):
#         self.category_name = self.category_name.title()   
#         if not self.slug:
#             self.slug = slugify(self.category_name)
#         super(Category, self).save(*args, **kwargs)
    

#     # def __str__(self) -> str:
#         return self.category_name