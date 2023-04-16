from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.parsers import FormParser, MultiPartParser

from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from parameter.api.serializers import (
    FurnaceSettingSerializer,
    ParameterSerializer,
    ParameterCalculationSerializer,
    ParameterApiFactorySerializer,
    FurnaceSettingDetailSerializer,
    FurnaceSettingListSerializer,
    ParameterDetailSerializer,
    ParameterListSerializer,
    ParameterUploadSerializer,
    ParameterCallMainSerializer
)
from parameter.models import FurnaceSetting, Parameter, ParameterCalc
from parameter.helper.utils import test_request_factory_api, read_excel_analyze, CallMain

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
    queryset = ParameterCalc.objects.all()
    serializer_class = ParameterCalculationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ParameterCalc.objects.filter(is_active=True)


class ParameterCallMain(generics.CreateAPIView):
    serializer_class = None
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            obj_call_main = CallMain()
            obj_call_main.main()
        except Exception as e:
            exceptions.APIException(e)
        return Response({}, status=200)


class ParameterApiFactoryAPIView(generics.ListAPIView):
    serializer_class = ParameterApiFactorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = test_request_factory_api()
        return Response({"data": data})


class ParameterUploadFileAPIView(generics.UpdateAPIView):
    queryset = FurnaceSetting.objects.all()
    serializer_class = ParameterUploadSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [CustomDjangoModelPermissions, IsAuthenticated]

    def get_object(self):
        return get_object_or_404(FurnaceSetting, id=self.kwargs.get("id"))

    def update(self, request, *args, **kwargs):
        if not request.FILES:
            raise exceptions.ValidationError(_("Please upload the desired excel file."))
        file = request.FILES['file']
        instance = self.get_object()
        data = read_excel_analyze(file, instance.data)
        instance.data = data
        instance.save()
        data = {
            "name": instance.name,
            "data": instance.data,
            "is_active": instance.is_active,
            "created_at": instance.created_at,
            "updates_at": instance.updated_at
        }
        return Response(data, status=200)
