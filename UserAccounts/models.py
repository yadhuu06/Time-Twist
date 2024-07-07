from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, phone_number=phone_number)
        user.set_password(password)
        user.is_active = False  # User is not active until they verify their OTP
        user.is_blocked = False
        user.date_joined = timezone.now()  # Set the date_joined field
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, phone_number, password=None):
        user = self.create_user(email, first_name, last_name, phone_number, password)
        user.is_admin = True
        user.is_active = True  # Superuser should be active by default
        user.date_joined = timezone.now()  # Set the date_joined field
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=False)  # New field for activation status
    is_admin = models.BooleanField(default=False)  # Existing field for admin status
    is_blocked = models.BooleanField(default=False)  # New field for blocked status
    date_joined = models.DateTimeField(default=timezone.now)  # New field for date joined

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    def __str__(self):
        return self.email

