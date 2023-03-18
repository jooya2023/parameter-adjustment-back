from django.contrib import admin
from accounts.models import User

from django.contrib.auth.admin import UserAdmin

# Register your models here.

UserAdmin.fieldsets[0][1]["fields"] = ("username", "password", "user_type")

admin.site.register(User, UserAdmin)
