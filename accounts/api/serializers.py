from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission

from accounts.models import User
from accounts.helper.permissions_tree import create_permissions_tree_group


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


class GroupDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]


class PermissionsTreeForGroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    permissions = serializers.ListField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

    def to_representation(self, instance):
        group = Group.objects.get(pk=instance.pk)
        permissions = Permission.objects.all()
        tree = create_permissions_tree_group(permissions, group.permissions.all())
        data = {
            "id": group.pk,
            "name": group.name,
            "permissions": tree
        }
        return data


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]
        extra_kwargs = {
            "permissions": {"read_only": True}
        }


class GroupDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'is_active', 'groups']


class GroupUpdateSerializer(serializers.Serializer):
    users = serializers.ListField(required=False)

    class Meta:
        fields = ["users"]
