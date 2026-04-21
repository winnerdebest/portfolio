from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        
        try:
            # Try to fetch the user by email or username
            user = UserModel.objects.filter(Q(email__iexact=username) | Q(username__iexact=username)).distinct()
        except UserModel.DoesNotExist:
            return None
        
        if user.exists():
            user_obj = user.first()
            if user_obj.check_password(password):
                return user_obj
        return None
