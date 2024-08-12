from django.db import models

from UserAccounts.models import User

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False)
    house_name = models.CharField(max_length=100, null=False)
    street_name = models.CharField(max_length=100, null=False)
    pin_number = models.IntegerField(null=False)
    district = models.CharField(max_length=100, null=False)
    state = models.CharField(max_length=100, null=False)
    phone_number = models.CharField(max_length=50, null=False)
    
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}, {self.house_name}, {self.street_name}, {self.district}, {self.state}, {self.country}'

    class Meta:
        verbose_name = "User Address"
        verbose_name_plural = "User Addresses"