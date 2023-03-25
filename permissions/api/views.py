from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


from accounts.models import User

from permissions.api.filters import PermissionFilterSet
from permissions.api.serializers import PermissionSerializer
from permissions.models import PermissionProxy

from core.helper.global_permissions import CustomDjangoModelPermissions


class ListPermissionUserView(generics.ListAPIView):
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'codename']
    filter_class = PermissionFilterSet
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    serializer_class = PermissionSerializer
    ordering_fields = ["name"]

    def get_serializer_context(self):
        context = super(ListPermissionUserView, self).get_serializer_context()
        context.update({'with_category': True if self.request.query_params.get('category') else False})
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        if user.is_superuser:
            return PermissionProxy.objects.all()
        else:
            return PermissionProxy.objects.filter(user=user)


class PermissionsDetailView(generics.RetrieveAPIView):
    """detail permission"""
    serializer_class = PermissionSerializer
    lookup_field = 'id'
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    queryset = PermissionProxy.objects.all()

    def get_serializer_context(self):
        context = super(PermissionsDetailView, self).get_serializer_context()
        context.update({'with_category': True if self.request.query_params.get('category') else False})
        return context

    def get_object(self):
        return get_object_or_404(PermissionProxy, id=self.kwargs.get('id'))
