from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password,verify_password

import logging

logger = logging.getLogger(__name__)

class EmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(email=username)
             
            logger.debug("Hashed password from the database: %s", user.password)
            logger.debug("Password from the form: %s", password)
            
            password_correct = verify_password(password, user.password)
            logger.debug("Password correct: %s", password_correct)
            
            # Testing set_password function
            # password_test_hash = set_password(password)
            # if user.password == password_test_hash:
            #     logger.debug("Hashed password matches the result of set_password")
            
            if password_correct and user.is_active and not user.is_blocked:
                return user
        except User.DoesNotExist:
            logger.debug("User with email %s does not exist", username)
            return None
        except Exception as e:
            logger.error("Exception occurred during authentication: %s", str(e))
            return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
