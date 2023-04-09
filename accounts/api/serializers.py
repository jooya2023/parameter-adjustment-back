from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from accounts.models import User, UserType
from accounts.helper.permissions_tree import create_permissions_tree_group

from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings

from core.helper.redis import Redis


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ["id", "name"]


class UserListSerializer(serializers.ModelSerializer):
    user_type = UserTypeSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "user_type", "first_name", "last_name", "email"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "user_type", "first_name", "last_name", "email"]


class MyUserSerializer(serializers.ModelSerializer):
    user_type = UserTypeSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "user_type", "email", "first_name", "last_name"]


class MyUserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "user_type", "email", "first_name", "last_name"]

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.user_type = validated_data.get("user_type", instance.user_type)
        instance.save()
        return instance


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
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'user_type',
            'email',
            'first_name',
            'last_name',
            'password',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        username = attrs.get('username', '')

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(_('This username already exists.'))

        elif not username.isalnum():
            raise serializers.ValidationError(_('the username should only contain alphanumeric characters.'))

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        if password is not None:
            try:
                user.set_password(password)
                user.save()
                return user
            except ValidationError as val_err:
                raise serializers.ValidationError(val_err.messages)


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


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    user_id = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)

    def validate(self, attrs):
        old_refresh = attrs['refresh']
        refresh = self.token_class(attrs["refresh"])

        user_id = refresh.payload['user_id']
        user = User.objects.get(id=user_id)
        data = {'user_id': user.id, 'username': user.username, 'access': str(refresh.access_token),
                'refresh': str(refresh)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)
        new_refresh = data['refresh']
        username = data['username']
        redis_object = Redis()
        redis_object.redis_set_new_refresh_token(new_refresh_token=new_refresh, old_refresh_token=old_refresh,
                                                 username=username)
        return data
