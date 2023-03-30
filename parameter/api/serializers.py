import datetime
import pandas as pd

from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from parameter.helper.calculations import read_cons, main_tread
from parameter.models import FurnaceSetting, Parameter


class FurnaceSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FurnaceSetting
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
                _("This is the default setting of the furnace, if you want it not to be the default, please choose another setting as the default.")
            )
        instance.save()
        return instance


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

            W_input[0][0] = [[item["amount"] for item in parameter_1["tanks"] if item["id"] == 1][0], [item["amount"] for item in parameter_1["tanks"] if item["id"] == 2][0]]
            W_input[0][1] = [[item["amount"] for item in parameter_2["tanks"] if item["id"] == 1][0], [item["amount"] for item in parameter_2["tanks"] if item["id"] == 2][0]]
            W_input[0][2] = [[item["amount"] for item in parameter_3["tanks"] if item["id"] == 1][0], [item["amount"] for item in parameter_3["tanks"] if item["id"] == 2][0]]

            W_input[1][0] = [[item["amount"] for item in parameter_1["tanks"] if item["id"] == 3][0], 0]
            W_input[1][1] = [[item["amount"] for item in parameter_2["tanks"] if item["id"] == 3][0], 0]
            W_input[1][2] = [[item["amount"] for item in parameter_3["tanks"] if item["id"] == 3][0]]

            W_input[2][0] = [[item["amount"] for item in parameter_1["tanks"] if item["id"] == 4][0]]
            W_input[2][1] = [[item["amount"] for item in parameter_2["tanks"] if item["id"] == 4][0]]
            W_input[2][2] = [[item["amount"] for item in parameter_3["tanks"] if item["id"] == 4][0], 0]

            # min capacity a matter
            s_floor_input = [[[] for j in range(3)] for i in range(3)]
            s_floor_input[0][0] = [furnace_1["minCapacity"]["iron"], 0]
            s_floor_input[0][1] = [furnace_1["minCapacity"]["lime"], 0]
            s_floor_input[0][2] = [furnace_1["minCapacity"]["dolomite"], 0]

            s_floor_input[1][0] = [furnace_2["minCapacity"]["iron"], 0]
            s_floor_input[1][1] = [furnace_2["minCapacity"]["lime"], 0]
            s_floor_input[1][2] = [furnace_2["minCapacity"]["dolomite"]]

            s_floor_input[2][0] = [furnace_3["minCapacity"]["iron"]]
            s_floor_input[2][1] = [furnace_3["minCapacity"]["lime"]]
            s_floor_input[2][2] = [furnace_3["minCapacity"]["dolomite"], 0]

            # max capacity a matter
            storage_input = [[[] for j in range(3)] for i in range(3)]
            storage_input[0][0] = [furnace_1["maxCapacity"]["iron"], 60]
            storage_input[0][1] = [furnace_1["maxCapacity"]["lime"], 60]
            storage_input[0][2] = [furnace_1["maxCapacity"]["dolomite"], 80]

            storage_input[1][0] = [furnace_2["maxCapacity"]["iron"], 8]
            storage_input[1][1] = [furnace_2["maxCapacity"]["lime"], 8]
            storage_input[1][2] = [furnace_2["maxCapacity"]["dolomite"]]

            storage_input[2][0] = [furnace_3["maxCapacity"]["iron"]]
            storage_input[2][1] = [furnace_3["maxCapacity"]["lime"]]
            storage_input[2][2] = [furnace_3["maxCapacity"]["dolomite"], 6]

            # نرخ شارژ
            K_input = [furnace_setting[0].data["chargeRate"]["iron"], furnace_setting[0].data["chargeRate"]["lime"],
                       furnace_setting[0].data["chargeRate"]["dolomite"]]

            # delay arrival
            D_R_input = [[furnace_1["arrivalDelay"]["iron"], furnace_1["arrivalDelay"]["lime"],
                          furnace_1["arrivalDelay"]["dolomite"]],
                         [furnace_2["arrivalDelay"]["iron"], furnace_2["arrivalDelay"]["lime"],
                          furnace_2["arrivalDelay"]["dolomite"]],
                         [furnace_3["arrivalDelay"]["iron"], furnace_3["arrivalDelay"]["lime"],
                          furnace_3["arrivalDelay"]["dolomite"]]]
            # delay empty
            D_E_input = [[furnace_1["emptyingDelay"]["iron"], furnace_1["emptyingDelay"]["lime"],
                          furnace_1["emptyingDelay"]["dolomite"]],
                         [furnace_2["emptyingDelay"]["iron"], furnace_2["emptyingDelay"]["lime"],
                          furnace_2["emptyingDelay"]["dolomite"]],
                         [furnace_3["emptyingDelay"]["iron"], furnace_3["emptyingDelay"]["lime"],
                          furnace_3["emptyingDelay"]["dolomite"]]]

            disables_raw_input = [(10, 9)]

            B_first_11_input = pd.DataFrame({'time': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                                             '1': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                             '2': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                             '3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                             '4': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                             '5': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                             '6': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                             '7': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                             '8': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                             '9': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                             '10': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                             '11': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                             '12': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})

            charge_instantly_choice_input = False

            try:
                CONS_input = read_cons()
                opt_actions_output, opt_w_in_time, opt_B, opt_shooting_list, STATUS, data = main_tread(
                    W_input, s_floor_input, storage_input, K_input, D_R_input, D_E_input, CONS_input,
                    B_first_11_input, disables_raw_input, charge_instantly_choice_input
                )
            except Exception as e:
                raise serializers.ValidationError(e)

            if STATUS == "400":
                raise serializers.ValidationError(_("There is a problem, please check the values."))

            parameter_obj = Parameter.objects.filter(is_active=True)
            if parameter_obj.exists():
                lst_action_output = []

                for item_opt_actions_output in opt_actions_output.values.tolist():
                    minute = datetime.timedelta(minutes=item_opt_actions_output[0])
                    duration = datetime.timedelta(minutes=item_opt_actions_output[1])
                    actions_output = {
                        "start_time": parameter_obj[0].updated_at + minute,
                        "end_time": parameter_obj[0].updated_at + minute + duration,
                        "row": [item_opt_actions_output[2], item_opt_actions_output[3], item_opt_actions_output[4]]
                    }
                    lst_action_output.append(actions_output)
            else:
                raise serializers.ValidationError(_("dose not exists parameter."))

            data_ = {
                "opt_actions_output": lst_action_output,
                "opt_w_in_time": str(opt_w_in_time),
                "opt_B": str(opt_B),
                "opt_shooting_list": str(opt_shooting_list),
                "STATUS": str(STATUS),
                "data": str(data)
            }
            return data_
        raise serializers.ValidationError(_("parameter or furnace setting not found."))
