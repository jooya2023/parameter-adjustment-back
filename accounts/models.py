from django.db import models

from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken


# Create your models here.

class User(AbstractUser):
    user_type = models.ForeignKey("UserType", on_delete=models.SET_NULL, null=True)

    def tokens(self):
        refresh_token = RefreshToken.for_user(self)
        return {"access": str(refresh_token.access_token), "refresh": str(refresh_token)}


class UserType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
