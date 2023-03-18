from rest_framework import serializers
from django.contrib.auth import authenticate

from accounts.models import User


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=68, write_only=True)
    permissions = serializers.JSONField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "tokens", "permissions"]

    def validate(self, attrs):
        username = attrs.get("username", None)
        password = attrs.get("password", None)
        if not username:
            raise serializers.ValidationError("username is required.")
        if not password:
            raise serializers.ValidationError("password is required.")

        user = authenticate(username=username, password=password)

        if not user or not user.is_active:
            raise serializers.ValidationError("The username or password is incorrect.")

        data = {
            "id": user.id,
            "username": user.username,
            "tokens": user.tokens,
            "permissions": user.get_group_permissions()
        }

        return data


class RegisterSerializer(serializers.ModelSerializer):
    pass
