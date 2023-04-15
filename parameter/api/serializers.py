import datetime
import pandas as pd

from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from parameter.helper.calculations import read_cons, main_tread
from parameter.helper.utils import CallMain, read_excel_analyze
from parameter.helper.call_main import call_main
from parameter.helper.api_cons import create_consumption
from parameter.models import FurnaceSetting, Parameter, ParameterCalc
from parameter.helper.utils import request_factory_api, test_request_factory_api


class FurnaceSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FurnaceSetting
        fields = ["id", "name", "data", "is_active"]

    def validate_is_active(self, value):
        if value:
            FurnaceSetting.objects.all().update(is_active=False)
            return value
        return value

    def update(self, instance, validated_data):
        is_active = validated_data.get("is_active", instance.is_active)
        if is_active:
            instance.name = validated_data.get("name", instance.name)
            instance.data = validated_data.get("data", instance.data)
            instance.is_active = is_active
            FurnaceSetting.objects.all().update(is_active=False)
        if is_active == False:
            instance.name = validated_data.get("name", instance.name)
            instance.data = validated_data.get("data", instance.data)
        instance.save()
        try:
            obj_call_main = CallMain()
            obj_call_main.main()
        except Exception:
            raise serializers.ValidationError(_("Please check the entries, there may be a problem with the entries"))
        return instance


class FurnaceSettingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FurnaceSetting
        fields = ["id", "name", "data", "is_active", "created_at"]


class FurnaceSettingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FurnaceSetting
        fields = ["id", "name", "is_active", "created_at"]


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ["id", "name", "data", "is_active"]

    def validate_is_active(self, value):
        if value:
            Parameter.objects.all().update(is_active=False)
            return value
        return value

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.data = validated_data.get("data", instance.data)
        is_active = validated_data.get("is_active", instance.is_active)
        if is_active:
            instance.is_active = is_active
            Parameter.objects.all().update(is_active=False)
        if is_active == False:
            raise serializers.ValidationError(
                _("This parameter is the default, if you want it not to be the default, please choose another "
                  "parameter as the default.")
            )
        instance.save()
        try:
            obj_call_main = CallMain()
            obj_call_main.main()
        except Exception:
            raise serializers.ValidationError(_("Please check the entries, there may be a problem with the entries"))
        return instance


class ParameterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FurnaceSetting
        fields = ["id", "name", "data", "is_active", "created_at"]


class ParameterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FurnaceSetting
        fields = ["id", "name", "is_active", "created_at"]


class ParameterCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterCalc
        fields = ["data"]


class ParameterApiFactorySerializer(serializers.Serializer):
    data = serializers.JSONField()


class ParameterUploadSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        fields = ["file"]


class ParameterCallMainSerializer(serializers.Serializer):
    data = serializers.JSONField()

    class Meta:
        fields = ["data"]

    def to_representation(self, instance):
        try:
            obj_call_main = CallMain()
            data = obj_call_main.main()
            return data
        except Exception:
            raise serializers.ValidationError(_("Please check the entries, there may be a problem with the entries"))

