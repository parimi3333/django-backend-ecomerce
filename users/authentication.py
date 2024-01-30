from django.db.models import Q
from django.contrib.auth.backends import ModelBackend
from .models import MyUser

class EmailAuthBackend(ModelBackend):
    """
    Custom authentication backend.

    Allows users to log in using their email address or phone number.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Overrides the authenticate method to allow users to log in using their email address or phone number.
        """
        try:
            # Using get() here assumes that there should be only one user with the given email/phone.
            # If multiple users exist, it will raise MyUser.MultipleObjectsReturned.
            # In such cases, you may want to handle it more gracefully, e.g., by logging an error.
            user = MyUser.objects.get(Q(email=username) | Q(phone=username))
        except MyUser.DoesNotExist:
            return None
        except MyUser.MultipleObjectsReturned:
            # Log an error or handle the case as needed
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        """
        Overrides the get_user method to allow users to log in using their email address or phone number.
        """
        try:
            return MyUser.objects.get(pk=user_id)
        except MyUser.DoesNotExist:
            return None
