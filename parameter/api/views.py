from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.parsers import FormParser, MultiPartParser

from django.utils.translation import gettext_lazy as _

from parameter.api.serializers import (
    FurnaceSettingSerializer,
    ParameterSerializer,
    ParameterCalculationSerializer,
    ParameterApiFactorySerializer,
    FurnaceSettingDetailSerializer,
    FurnaceSettingListSerializer,
    ParameterDetailSerializer,
    ParameterListSerializer,
    ParameterUploadSerializer
)
from parameter.models import FurnaceSetting, Parameter
from parameter.helper.utils import test_request_factory_api, read_excel_analyze

from core.helper.global_permissions import CustomDjangoModelPermissions


class FurnaceSettingListCreateAPIView(generics.ListCreateAPIView):
    queryset = FurnaceSetting.objects.all()
    serializer_class = FurnaceSettingSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["is_active", "created_at", "id"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return FurnaceSettingListSerializer
        return FurnaceSettingSerializer


class FurnaceSettingRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FurnaceSetting.objects.all()
    serializer_class = FurnaceSettingSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return FurnaceSettingDetailSerializer
        return FurnaceSettingSerializer


class ParameterListCreateAPIView(generics.ListCreateAPIView):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["is_active", "created_at", "id"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ParameterListSerializer
        return ParameterSerializer


class ParameterRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ParameterDetailSerializer
        return ParameterSerializer


class ParameterCalculationAPIView(generics.ListAPIView):
    serializer_class = ParameterCalculationSerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.data)
        return Response(serializer.data)


class ParameterApiFactoryAPIView(generics.ListAPIView):
    serializer_class = ParameterApiFactorySerializer
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = test_request_factory_api()
        return Response({"data": data})


class ParameterUploadFileAPIView(generics.CreateAPIView):
    serializer_class = ParameterUploadSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.FILES:
            raise exceptions.ValidationError(_("Please upload the desired excel file."))
        file = request.FILES['file']
        data = read_excel_analyze(file)
        return Response(data)

