import datetime
import pandas as pd

from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from parameter.helper.calculations import read_cons, main_tread
from parameter.helper.utils import CallMain, read_excel_analyze
from parameter.helper.call_main import call_main
from parameter.helper.api_cons import create_consumption
from parameter.models import FurnaceSetting, Parameter
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
                _("This parameter is the default, if you want it not to be the default, please choose another parameter as the default.")
            )
        instance.save()
        return instance


class ParameterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FurnaceSetting
        fields = ["id", "name", "data", "is_active", "created_at"]


class ParameterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FurnaceSetting
        fields = ["id", "name", "is_active", "created_at"]


class ParameterCalculationSerializer(serializers.Serializer):
    data = serializers.JSONField()

    def to_representation(self, instance):
        furnace_setting = FurnaceSetting.objects.filter(is_active=True)
        parameter_obj = Parameter.objects.filter(is_active=True)
        if furnace_setting.exists() and parameter_obj.exists():
            furnace_1 = [item for item in furnace_setting[0].data["furnaces"] if item["id"] == 1][0]
            furnace_2 = [item for item in furnace_setting[0].data["furnaces"] if item["id"] == 2][0]
            furnace_3 = [item for item in furnace_setting[0].data["furnaces"] if item["id"] == 3][0]

            parameter_1 = [item for item in parameter_obj[0].data["furnaces"] if item["id"] == 1][0]
            parameter_2 = [item for item in parameter_obj[0].data["furnaces"] if item["id"] == 2][0]
            parameter_3 = [item for item in parameter_obj[0].data["furnaces"] if item["id"] == 3][0]

            W_input = [[[] for j in range(3)] for i in range(3)]

            W_input[0][0] = [[item["amount"] for item in parameter_1["tanks"] if item["id"] == 1][0],
                             [item["amount"] for item in parameter_1["tanks"] if item["id"] == 2][0]]
            W_input[0][1] = [[item["amount"] for item in parameter_2["tanks"] if item["id"] == 1][0],
                             [item["amount"] for item in parameter_2["tanks"] if item["id"] == 2][0]]
            W_input[0][2] = [[item["amount"] for item in parameter_3["tanks"] if item["id"] == 1][0],
                             [item["amount"] for item in parameter_3["tanks"] if item["id"] == 2][0]]

            W_input[1][0] = [[item["amount"] for item in parameter_1["tanks"] if item["id"] == 3][0],
                             [item["amount"] for item in parameter_1["tanks"] if item["id"] == 5][0]]
            W_input[1][1] = [[item["amount"] for item in parameter_2["tanks"] if item["id"] == 3][0],
                             [item["amount"] for item in parameter_2["tanks"] if item["id"] == 5][0]]
            W_input[1][2] = [[item["amount"] for item in parameter_3["tanks"] if item["id"] == 3][0],
                             [item["amount"] for item in parameter_3["tanks"] if item["id"] == 5][0]]

            W_input[2][0] = [[item["amount"] for item in parameter_1["tanks"] if item["id"] == 4][0]]
            W_input[2][1] = [[item["amount"] for item in parameter_2["tanks"] if item["id"] == 4][0]]
            W_input[2][2] = [[item["amount"] for item in parameter_3["tanks"] if item["id"] == 4][0],
                             [item["amount"] for item in parameter_3["tanks"] if item["id"] == 5][0]]

            # W_input[0][0] = [28.8, 28.0]
            # W_input[0][1] = [28.6, 28.4]
            # W_input[0][2] = [45.6, 25.2]
            #
            # W_input[1][0] = [5.32, 2]
            # W_input[1][1] = [5.88, 2]
            # W_input[1][2] = [5.8, 3]
            #
            # W_input[2][0] = [5.68]
            # W_input[2][1] = [5.6]
            # W_input[2][2] = [7.68, 4]

            # min capacity a matter
            s_floor_input = [[[] for j in range(3)] for i in range(3)]
            s_floor_input[0][0] = [furnace_1["minCapacity"]["iron"], furnace_1["minCapacity"]["iron"]]
            s_floor_input[0][1] = [furnace_1["minCapacity"]["lime"], furnace_1["minCapacity"]["lime"]]
            s_floor_input[0][2] = [furnace_1["minCapacity"]["dolomite"], furnace_1["minCapacity"]["dolomite"]]

            s_floor_input[1][0] = [furnace_2["minCapacity"]["iron"], 0.1]
            s_floor_input[1][1] = [furnace_2["minCapacity"]["lime"], 0.1]
            s_floor_input[1][2] = [furnace_2["minCapacity"]["dolomite"], 0.1]

            s_floor_input[2][0] = [furnace_3["minCapacity"]["iron"]]
            s_floor_input[2][1] = [furnace_3["minCapacity"]["lime"]]
            s_floor_input[2][2] = [furnace_3["minCapacity"]["dolomite"], 0.1]

            # s_floor_input[0][0] = [2, 2]
            # s_floor_input[0][1] = [2, 2]
            # s_floor_input[0][2] = [2, 2]
            #
            # s_floor_input[1][0] = [0.2, 0.1]
            # s_floor_input[1][1] = [0.2, 0.1]
            # s_floor_input[1][2] = [0.2, 0.1]
            #
            # s_floor_input[2][0] = [0.2]
            # s_floor_input[2][1] = [0.2]
            # s_floor_input[2][2] = [0.2, 0.1]

            # max capacity a matter
            storage_input = [[[] for j in range(3)] for i in range(3)]
            storage_input[0][0] = [furnace_1["maxCapacity"]["iron"], furnace_1["maxCapacity"]["iron"]]
            storage_input[0][1] = [furnace_1["maxCapacity"]["lime"], furnace_1["maxCapacity"]["lime"]]
            storage_input[0][2] = [furnace_1["maxCapacity"]["dolomite"], furnace_1["maxCapacity"]["dolomite"]]

            storage_input[1][0] = [furnace_2["maxCapacity"]["iron"], 8]
            storage_input[1][1] = [furnace_2["maxCapacity"]["lime"], 8]
            storage_input[1][2] = [furnace_2["maxCapacity"]["dolomite"], 8]

            storage_input[2][0] = [furnace_3["maxCapacity"]["iron"]]
            storage_input[2][1] = [furnace_3["maxCapacity"]["lime"]]
            storage_input[2][2] = [furnace_3["maxCapacity"]["dolomite"], 6]

            # storage_input[0][0] = [60, 60]
            # storage_input[0][1] = [60, 60]
            # storage_input[0][2] = [80, 80]
            #
            # storage_input[1][0] = [12, 8]
            # storage_input[1][1] = [12, 8]
            # storage_input[1][2] = [12, 8]
            #
            # storage_input[2][0] = [12]
            # storage_input[2][1] = [12]
            # storage_input[2][2] = [12, 6]

            # نرخ شارژ
            K_input = [furnace_setting[0].data["chargeRate"]["iron"], furnace_setting[0].data["chargeRate"]["lime"],
                       furnace_setting[0].data["chargeRate"]["dolomite"]]
            # K_input = [3.1, 2.3, 2.4]

            # delay arrival
            D_R_input = [[furnace_1["arrivalDelay"]["iron"], furnace_1["arrivalDelay"]["lime"],
                          furnace_1["arrivalDelay"]["dolomite"]],
                         [furnace_2["arrivalDelay"]["iron"], furnace_2["arrivalDelay"]["lime"],
                          furnace_2["arrivalDelay"]["dolomite"]],
                         [furnace_3["arrivalDelay"]["iron"], furnace_3["arrivalDelay"]["lime"],
                          furnace_3["arrivalDelay"]["dolomite"]]]
            # # delay empty
            D_E_input = [[furnace_1["emptyingDelay"]["iron"], furnace_1["emptyingDelay"]["lime"],
                          furnace_1["emptyingDelay"]["dolomite"]],
                         [furnace_2["emptyingDelay"]["iron"], furnace_2["emptyingDelay"]["lime"],
                          furnace_2["emptyingDelay"]["dolomite"]],
                         [furnace_3["emptyingDelay"]["iron"], furnace_3["emptyingDelay"]["lime"],
                          furnace_3["emptyingDelay"]["dolomite"]]]
            # D_R_input = [[8, 7, 9],
            #              [5, 5, 7],
            #              [5, 5, 7]]
            # D_E_input = [[2, 2, 2],
            #              [2, 2, 2],
            #              [2, 2, 2]]

            # disables_raw_input = [(10, 9)]
            disables_raw_input = [(10, 9), (4, 12)]
            #
            # B_first_11_input = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #                     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #                     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #                     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

            charge_instantly_choice_input = False
            # CONS_input = read_cons()

            obj_call_main = CallMain()
            data = obj_call_main.main(W_input, s_floor_input, storage_input, K_input, D_R_input, D_E_input, disables_raw_input, charge_instantly_choice_input)

            return data
        raise serializers.ValidationError(_("parameter or furnace setting not found."))


class ParameterApiFactorySerializer(serializers.Serializer):
    data = serializers.JSONField()


class ParameterUploadSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        fields = ["file"]

