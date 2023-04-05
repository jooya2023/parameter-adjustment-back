from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView

from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

from accounts.api.serializers import (
    UserListSerializer,
    UserSerializer,
    LoginSerializer,
    RegisterSerializer,
    GroupSerializer,
    GroupDetailUpdateSerializer,
    PermissionsTreeForGroupSerializer,
    GroupDetailSerializer,
    GroupUpdateSerializer,
    CustomTokenRefreshSerializer,
    MyUserSerializer,
    MyUserUpdateSerializer
)
from accounts.models import User

from core.helper.redis import Redis
from core.helper.global_permissions import CustomDjangoModelPermissions


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]


class MyUserAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)


class MyUserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = MyUserUpdateSerializer

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)


class UserUpdateDetailDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserListSerializer
        return UserSerializer


class LoginGenericView(generics.GenericAPIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.redis = Redis()

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get("username")
        refresh_token = serializer.data["tokens"]["refresh"]
        self.redis.redis_add_refresh_token(username, refresh_token)
        return Response(serializer.data, status=200)


class CustomRefreshTokenAPIView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class RegisterGenericView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)


class GroupListCreateAPIView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]


class GroupDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """detail update delete Group"""

    queryset = Group.objects.all()
    serializer_class = GroupDetailUpdateSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_class(self):
        category = self.request.GET.get("category")
        if self.request.method == "GET" and category == 'true':
            return PermissionsTreeForGroupSerializer
        if self.request.method == "GET" and category is None:
            return GroupSerializer
        else:
            return self.serializer_class

    def get_object(self):
        return get_object_or_404(Group, id=self.kwargs.get('id'))

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(group)
        return Response(serializer.data, status=200)


class UsersGroupUpdateAPIView(generics.ListAPIView, generics.UpdateAPIView):
    """It specifies which groups the target user is a member of"""
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    serializer_class = GroupDetailSerializer

    def get_queryset(self):
        return User.objects.filter(groups__id=self.kwargs['id'])

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return self.serializer_class
        if self.request.method == 'PATCH':
            return GroupUpdateSerializer

    def get_object(self):
        return get_object_or_404(Group, id=self.kwargs['id'])

    def patch(self, request, *args, **kwargs):
        group = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={'id': id})
        serializer.is_valid(raise_exception=True)
        if "users" in serializer.data:
            users = serializer.data['users']
            group.user_set.set(users)
        group.save()
        return Response(serializer.data, status=200)
