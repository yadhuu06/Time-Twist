
from django.db import models
from UserAccounts.models import User
from products.models import Products, ProductVariant
from django.utils import timezone


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"Cart of {self.user}"
    

class CartItem(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def sub_total(self):
        return self.variant.offer_price * self.quantity

    def __str__(self):
        return f"{self.quantity} of {self.product} in {self.cart}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateField(default=timezone.now)

    
    def __str__(self):
        return f"{self.user.first_name}'s Wallet"


class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=500)
    timestamp = models.DateTimeField(default=timezone.now)
    transaction_type=models.CharField(max_length=500)    

    def __str__(self):
        return f"Transaction of {self.amount} on {self.timestamp}"