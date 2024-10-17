from django.db import models
from UserAccounts.models import User
from user_pannel.models import UserAddress
from products.models import ProductVariant
from django.utils import timezone
import uuid

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('creditCard', 'Credit Card'),
        ('Razopay ', 'Razopay'),
        ('cashOnDelivery', 'Cash on Delivery'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, default='Pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user.first_name} - {self.method}"

class Order(models.Model):  
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned')
        
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(UserAddress, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    order_id = models.CharField(max_length=36, unique=True, default=uuid.uuid4, editable=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2,null=True,default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='Pending') 
    order_payment_id = models.CharField(max_length=100, null=True, blank=True)
    delivered_date = models.DateField(null=True, blank=True)
    

    def __str__(self):
        return f"Order {self.id} by {self.user.first_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    coupon_offer = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    

    def __str__(self):
        return f"{self.product_variant.product_name} ({self.quantity})"

class OrderAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False)
    house_name = models.CharField(max_length=100, null=False)
    street_name = models.CharField(max_length=100, null=False)
    pin_number = models.IntegerField(null=False)
    district = models.CharField(max_length=100, null=False)
    state = models.CharField(max_length=100, null=False)
    phone_number = models.CharField(max_length=50, null=False)


class Return(models.Model):
    RETURN_REASONS = [
        ('Low Quality', 'Low Quality'),
        ('Not as Described', 'Not as Described'),
        ('Wrong Item Received', 'Wrong Item Received'),
        ('Size Issue', 'Size Issue'),
        ('Others', 'Others'),
    ]
    
    RETURN_STATUS = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
        ('rejected', 'Rejected'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50, choices=RETURN_REASONS)
    status = models.CharField(max_length=10, choices=RETURN_STATUS, default='pending')
    return_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Return for Order {self.order.order_id} by {self.user.username}"