# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth import get_user_model


# class EmailBackend(BaseBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         User = get_user_model()
#         try:
#             user = User.objects.get(email=username)
#             print(f"User found: {user.email}")  # Debug output
            
#             # Check if the provided password matches the hashed password in the database
#             password_correct = user.check_password(password)  # Using the model method
            
#             print(f"Password correct: {password_correct}")  # Debug output
            
#             if password_correct and user.is_active:
#                 print("User is authenticated.")  # Debug output
#                 return user
#             else:
#                 print("User is either inactive or blocked.")  # Debug output
#         except User.DoesNotExist:
#             print("User does not exist.")  # Debug output
#             return None
#         except Exception as e:
#             print(f"Error occurred: {e}")  # Debug output
#             return None

#     def get_user(self, user_id):
#         User = get_user_model()
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None

