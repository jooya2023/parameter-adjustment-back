from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters

from parameter.api.serializers import FurnaceSettingSerializer, ParameterSerializer
from parameter.models import FurnaceSetting, Parameter

from core.helper.global_permissions import CustomDjangoModelPermissions


class FurnaceSettingListCreateAPIView(generics.ListCreateAPIView):
    queryset = FurnaceSetting.objects.all()
    serializer_class = FurnaceSettingSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["is_active", "created_at", "id"]


class FurnaceSettingRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FurnaceSetting.objects.all()
    serializer_class = FurnaceSettingSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    lookup_field = "id"


class ParameterListCreateAPIView(generics.ListCreateAPIView):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["is_active", "created_at", "id"]


class ParameterRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    lookup_field = "id"
