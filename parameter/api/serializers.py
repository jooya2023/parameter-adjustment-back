from rest_framework import serializers

from parameter.models import FurnaceSetting, Parameter


class FurnaceSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FurnaceSetting
        fields = ["id", "name", "data", "is_active"]


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ["id", "name", "data", "is_active"]
