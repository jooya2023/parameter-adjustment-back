import os
import pandas as pd
import numpy as np
import requests
import datetime
import json
import pandas
from pickle5 import pickle

from parameter.helper.calculations import main_tread
from parameter.helper.api_cons import create_consumption
from parameter.models import Parameter, FurnaceSetting, ParameterCalc

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions


def test_request_factory_api():
    file = f"{settings.BASE_DIR}/parameter/helper/BinStatus01.pkl"
    # file = "BinStatus.pkl"
    f = open(file, 'rb')
    BinStatus = pickle.load(f)
    return BinStatus


def request_factory_api(from_date, to_date):
    obj_data = {"fromDate": "1401/12/10 09:20:20", "toDate": "1401/12/12 23:59:59"}

    # دریافت وضعیت بین ها که فقط در داخل کارخانه کار می کند
    url_BinStatus = "http://ias22:8735/MeltShopHttpServiceLibrary/GetBinStatus"
    data_BinStatus = requests.post(url_BinStatus, json=obj_data)
    data_BinStatus = json.loads(data_BinStatus.content)
    BinStatus = data_BinStatus
    return BinStatus


def read_excel_analyze(file, data_instance):
    excel_read_f1 = pandas.read_excel(file, sheet_name="f1")
    data_s1 = excel_read_f1["s1"].to_numpy(dtype='float')
    data_sb1 = excel_read_f1["sb1"].to_numpy(dtype='float')

    excel_read_f2 = pandas.read_excel(file, sheet_name="f2")
    data_s2 = excel_read_f2["s2"].to_numpy(dtype='float')
    data_sb2 = excel_read_f2["sb2"].to_numpy(dtype='float')

    excel_read_f3 = pandas.read_excel(file, sheet_name="f3")
    data_s3 = excel_read_f3["s3"].to_numpy(dtype='float')
    data_sb3 = excel_read_f3["sb3"].to_numpy(dtype='float')

    # for i in data_s1:
    #     if str(i) == "nan":
    #         lst_data_s1.append(float(0.0))
    #     else:
    #         lst_data_s1.append(i)
    #
    # for i in data_sb1:
    #     if str(i) == "nan":
    #         lst_data_sb1.append(float(0.0))
    #     else:
    #         lst_data_sb1.append(i)
    # # -----------------------------------------
    #
    # for i in data_s2:
    #     if str(i) == "nan":
    #         lst_data_s2.append(float(0.0))
    #     else:
    #         lst_data_s2.append(i)
    #
    # for i in data_sb2:
    #     if str(i) == "nan":
    #         lst_data_sb2.append(float(0.0))
    #     else:
    #         lst_data_sb2.append(i)
    #
    # # -----------------------------------------------
    #
    # for i in data_s3:
    #     if str(i) == "nan":
    #         lst_data_s3.append(float(0.0))
    #     else:
    #         lst_data_s3.append(i)
    #
    # for i in data_sb3:
    #     if str(i) == "nan":
    #         lst_data_sb3.append(float(0.0))
    #     else:
    #         lst_data_sb3.append(i)

    lst_furnaces = []
    for item_instance in data_instance["furnaces"]:
        if item_instance["id"] == 1:
            item_instance["DRI_usage"] = {"s": list(data_s1), "sb": list(data_sb1)}
            lst_furnaces.append(item_instance)
        if item_instance["id"] == 2:
            item_instance["DRI_usage"] = {"s": list(data_s2), "sb": list(data_sb2)}
            lst_furnaces.append(item_instance)
        if item_instance["id"] == 3:
            item_instance["DRI_usage"] = {"s": list(data_s3), "sb": list(data_sb3)}
            lst_furnaces.append(item_instance)

    data_instance["furnaces"] = lst_furnaces

    return data_instance


class CallMain:

    def __init__(self):
        self.parameter_obj = Parameter.objects.filter(is_active=True)

    def cons_input(self):
        global s1, sb1, s2, sb2, s3, sb3, power_on_1, power_on_2, power_on_3, tab_to_tab_1, tab_to_tab_2, tab_to_tab_3, usage_lime_1, usage_lime_2, usage_lime_3, usage_dolomite_1, usage_dolomite_2, usage_dolomite_3
        furnace_obj = FurnaceSetting.objects.filter(is_active=True)[0]
        for item in furnace_obj.data["furnaces"]:
            if item["id"] == 1:
                s1 = item["DRI_usage"]["s"]
                sb1 = item["DRI_usage"]["sb"]
                power_on_1 = item["baseSettings"]["powerOn"]
                tab_to_tab_1 = item["baseSettings"]["tabToTab"]
                usage_lime_1 = item["usage"]["lime"]
                usage_dolomite_1 = item["usage"]["dolomite"]

            if item["id"] == 2:
                s2 = item["DRI_usage"]["s"]
                sb2 = item["DRI_usage"]["sb"]
                power_on_2 = item["baseSettings"]["powerOn"]
                tab_to_tab_2 = item["baseSettings"]["tabToTab"]
                usage_lime_2 = item["usage"]["lime"]
                usage_dolomite_2 = item["usage"]["dolomite"]

            if item["id"] == 3:
                s3 = item["DRI_usage"]["s"]
                sb3 = item["DRI_usage"]["sb"]
                power_on_3 = item["baseSettings"]["powerOn"]
                tab_to_tab_3 = item["baseSettings"]["tabToTab"]
                usage_lime_3 = item["usage"]["lime"]
                usage_dolomite_3 = item["usage"]["dolomite"]

        s1_lst = []
        sb1_lst = []
        s2_lst = []
        sb2_lst = []
        s3_lst = []
        sb3_lst = []
        power_on = [power_on_1, power_on_2, power_on_3]
        tab_to_tab = [tab_to_tab_1, tab_to_tab_2, tab_to_tab_3]
        for i in s1:
            s1_lst.append(i / 1000)
        for i in sb1:
            sb1_lst.append(i / 1000)
        for i in s2:
            s2_lst.append(i / 1000)
        for i in sb2:
            sb2_lst.append(i / 1000)
        for i in s3:
            s3_lst.append(i / 1000)
        for i in sb3:
            sb3_lst.append(i / 1000)

        f1D = s1_lst
        f1Ds = sb1_lst
        f2D = s2_lst
        f2Ds = sb2_lst
        f3D = s3_lst
        f3Ds = sb3_lst
        pw = power_on
        taptotap = tab_to_tab

        lime_cons_rate = [usage_lime_1, usage_lime_2, usage_lime_3]
        dolomite_cons_rate = [usage_dolomite_1, usage_dolomite_2, usage_dolomite_3]

        f1lime = (lime_cons_rate[0] / pw[0]) * np.concatenate(
            (np.ones((1, pw[0])).flatten(), np.zeros((1, taptotap[0] - pw[0] + 1)).flatten()))
        f2lime = (lime_cons_rate[1] / pw[1]) * np.concatenate(
            (np.ones((1, pw[1])).flatten(), np.zeros((1, taptotap[1] - pw[1] + 1)).flatten()))
        f3lime = (lime_cons_rate[2] / pw[2]) * np.concatenate(
            (np.ones((1, pw[2])).flatten(), np.zeros((1, taptotap[2] - pw[2] + 1)).flatten()))

        f1dol = (dolomite_cons_rate[0] / pw[0]) * np.concatenate(
            (np.ones((1, pw[0])).flatten(), np.zeros((1, taptotap[0] - pw[0] + 1)).flatten()))
        f2dol = (dolomite_cons_rate[1] / pw[1]) * np.concatenate(
            (np.ones((1, pw[1])).flatten(), np.zeros((1, taptotap[1] - pw[1] + 1)).flatten()))
        f3dol = (dolomite_cons_rate[2] / pw[2]) * np.concatenate(
            (np.ones((1, pw[2])).flatten(), np.zeros((1, taptotap[2] - pw[2] + 1)).flatten()))

        CONS_input = create_consumption(f1D, f1Ds, f2D, f2Ds, f3D, f3Ds, f1lime, f2lime, f3lime, f1dol, f2dol, f3dol)

        return CONS_input

    def b_first_11_input(self):
        binid_lst = []
        entryhour_lst = []
        entrymin_lst = []
        entryduration_lst = []
        for item in self.parameter_obj[0].data["gatesStatus"]:
            if item["gate"]:
                binid_lst.append(item["gate"]["id"])
                time_lst = item["time"].split(":")
                entryhour_lst.append(time_lst[0])
                entrymin_lst.append(time_lst[1])
                entryduration_lst.append(item["duration"])
            else:
                binid_lst = [0, 0, 0]
                entryhour_lst = [0, 0, 0]
                entrymin_lst = [0, 0, 0]
                entryduration_lst = [0, 0, 0]

        wzero = np.zeros((11, 12))
        current_time = datetime.datetime.now()
        zero_time = current_time - datetime.timedelta(minutes=10)
        rng12 = pd.date_range(zero_time, current_time, freq='1min').strftime("%H:%M")
        wzeroall = pd.DataFrame(wzero, index=rng12)

        i = 0

        for binid in binid_lst:
            if binid > -1:
                d = str(entryhour_lst[i]) + ":" + str(entrymin_lst[i])
                dt = datetime.datetime.strptime(d, "%H:%M")
                dtrange = pd.date_range(dt, dt + datetime.timedelta(minutes=int(entryduration_lst[i]) - 1),
                                        freq='1min').strftime(
                    "%H:%M")
                ins1 = wzeroall.index.intersection(dtrange)
                b1 = binid
                if ins1.empty != 1:
                    wzeroall.loc[ins1, b1] = 1
            i = i + 1

        B_first_11_input = wzeroall.values.tolist()
        return B_first_11_input

    def create_input_main(self):
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
            B_first_11_input = self.b_first_11_input()

            charge_instantly_choice_input = False
            CONS_input = self.cons_input()
            print(CONS_input)
            return W_input, s_floor_input, storage_input, K_input, D_R_input, D_E_input, CONS_input, B_first_11_input, disables_raw_input, charge_instantly_choice_input
        raise exceptions.ValidationError(_("parameter or furnace setting not found."))

    def main(self):
        W_input, s_floor_input, storage_input, K_input, D_R_input, D_E_input, CONS_input, B_first_11_input, disables_raw_input, charge_instantly_choice_input = self.create_input_main()
        self.opt_actions_output, self.opt_w_in_time, self.opt_B, self.opt_shooting_list, self.STATUS, self.no_action_spend_time, self.data = main_tread(
            W_input,
            s_floor_input,
            storage_input,
            K_input,
            D_R_input,
            D_E_input,
            CONS_input,
            B_first_11_input,
            disables_raw_input,
            charge_instantly_choice_input=False
        )

        if self.STATUS == "400":
            raise exceptions.ValidationError(_("There is a problem, please check the values."))

        data = self.create_data_json()
        self.save_data_main(data)
        return data

    def save_data_main(self, data):
        furnace = FurnaceSetting.objects.filter(is_active=True)
        parameter = Parameter.objects.filter(is_active=True)
        ParameterCalc.objects.all().update(is_active=False)
        ParameterCalc.objects.create(
            data=data,
            furnace_setting=furnace[0],
            parameter=parameter[0],
            is_active=True
        )
        return True

    def data_convert(self):
        data = [
            {"row": "0, 0, 0", "convert": "آهن کوره ۱"},
            {"row": "0, 0, 1", "convert": "آهن کوره ۱ بین ۱"},
            {"row": "0, 1, 0", "convert": "آهن کوره ۲"},
            {"row": "0, 1, 1", "convert": "آهن کوره ۲ بین ۱"},
            {"row": "0, 2, 0", "convert": "اهن کوره ۳"},
            {"row": "0, 2, 1", "convert": "آهن کوره ۳ بین ۱"},
            {"row": "1, 0, 0", "convert": "آهک کوره ۱"},
            {"row": "1, 1, 0", "convert": "آهک کوره ۲"},
            {"row": "1, 2, 0", "convert": "آهک کوره ۳"},
            {"row": "2, 0, 0", "convert": "دولومیت کوره ۱"},
            {"row": "2, 1, 0", "convert": "دولومیت کوره ۲"},
            {"row": "2, 2, 0", "convert": "دولومیت کوره ۳"},
        ]
        return data

    def convert_row_action_putput(self, material, furnace, pin):
        row = f"{material}, {furnace}, {pin}"
        for item in self.data_convert():
            if item["row"] == row:
                return item["convert"]
        else:
            return ""

    def action_output(self):
        if self.parameter_obj.exists():
            lst_action_output = []

            for item_opt_actions_output in self.opt_actions_output.values.tolist():
                minute = datetime.timedelta(minutes=item_opt_actions_output[0])
                timezone = datetime.timedelta(hours=3, minutes=30)
                duration = datetime.timedelta(minutes=item_opt_actions_output[1])
                actions_output = {
                    "start_time": str(datetime.datetime.now() + minute + timezone),
                    "end_time": str(datetime.datetime.now() + minute + duration + timezone),
                    "furnace": self.convert_row_action_putput(item_opt_actions_output[2], item_opt_actions_output[3],
                                                              item_opt_actions_output[4])
                }
                lst_action_output.append(actions_output)
            return lst_action_output
        else:
            raise exceptions.ValidationError(_("dose not exists parameter."))

    def opt_w_in_time_iron(self):
        # Iron
        iron_furnace1_bin1 = self.opt_w_in_time.loc[:, ["0,0,0"]]
        lst_iron_furnace1_bin1 = []
        for item_iron_furnace1_bin1 in iron_furnace1_bin1.values.tolist():
            for item in item_iron_furnace1_bin1:
                if str(item) == "nan":
                    lst_iron_furnace1_bin1.append(0.0)
                else:
                    lst_iron_furnace1_bin1.append(round(item, 2))

        iron_furnace1_bin2 = self.opt_w_in_time.loc[:, ["0,0,1"]]
        lst_iron_furnace1_bin2 = []
        for item_iron_furnace1_bin2 in iron_furnace1_bin2.values.tolist():
            for item in item_iron_furnace1_bin2:
                if str(item) == "nan":
                    lst_iron_furnace1_bin2.append(0.0)
                else:
                    lst_iron_furnace1_bin2.append(round(item, 2))

        iron_furnace2_bin1 = self.opt_w_in_time.loc[:, ["0,1,0"]]
        lst_iron_furnace2_bin1 = []
        for item_iron_furnace2_bin1 in iron_furnace2_bin1.values.tolist():
            for item in item_iron_furnace2_bin1:
                if str(item) == "nan":
                    lst_iron_furnace2_bin1.append(0.0)
                else:
                    lst_iron_furnace2_bin1.append(round(item, 2))

        iron_furnace2_bin2 = self.opt_w_in_time.loc[:, ["0,1,1"]]
        lst_iron_furnace2_bin2 = []
        for item_iron_furnace2_bin2 in iron_furnace2_bin2.values.tolist():
            for item in item_iron_furnace2_bin2:
                if str(item) == "nan":
                    lst_iron_furnace2_bin2.append(0.0)
                else:
                    lst_iron_furnace2_bin2.append(round(item, 2))

        iron_furnace3_bin1 = self.opt_w_in_time.loc[:, ["0,2,0"]]
        lst_iron_furnace3_bin1 = []
        for item_iron_furnace3_bin1 in iron_furnace3_bin1.values.tolist():
            for item in item_iron_furnace3_bin1:
                if str(item) == "nan":
                    lst_iron_furnace3_bin1.append(0.0)
                else:
                    lst_iron_furnace3_bin1.append(round(item, 2))

        iron_furnace3_bin2 = self.opt_w_in_time.loc[:, ["0,2,1"]]
        lst_iron_furnace3_bin2 = []
        for item_iron_furnace3_bin2 in iron_furnace3_bin2.values.tolist():
            for item in item_iron_furnace3_bin2:
                if str(item) == "nan":
                    lst_iron_furnace3_bin2.append(0.0)
                else:
                    lst_iron_furnace3_bin2.append(round(item, 2))

        return lst_iron_furnace1_bin1, lst_iron_furnace1_bin2, lst_iron_furnace2_bin1, lst_iron_furnace2_bin2, lst_iron_furnace3_bin1, lst_iron_furnace3_bin2

    def opt_in_time_lime(self):
        # Lime
        lime_furnace1_bin1 = self.opt_w_in_time.loc[:, ["1,0,0"]]
        lst_lime_furnace1_bin1 = []
        for item_lime_furnace1_bin1 in lime_furnace1_bin1.values.tolist():
            for item in item_lime_furnace1_bin1:
                if str(item) == "nan":
                    lst_lime_furnace1_bin1.append(0.0)
                else:
                    lst_lime_furnace1_bin1.append(round(item, 2))

        lime_furnace1_bin2 = self.opt_w_in_time.loc[:, ["1,0,1"]]
        lst_lime_furnace1_bin2 = []
        for item_lime_furnace1_bin2 in lime_furnace1_bin2.values.tolist():
            for item in item_lime_furnace1_bin2:
                if str(item) == "nan":
                    lst_lime_furnace1_bin2.append(0.0)
                else:
                    lst_lime_furnace1_bin2.append(round(item, 2))

        lime_furnace2_bin1 = self.opt_w_in_time.loc[:, ["1,1,0"]]
        lst_lime_furnace2_bin1 = []
        for item_lime_furnace2_bin1 in lime_furnace2_bin1.values.tolist():
            for item in item_lime_furnace2_bin1:
                if str(item) == "nan":
                    lst_lime_furnace2_bin1.append(0.0)
                else:
                    lst_lime_furnace2_bin1.append(round(item, 2))
        lime_furnace2_bin2 = self.opt_w_in_time.loc[:, ["1,1,1"]]
        lst_lime_furnace2_bin2 = []
        for item_lime_furnace2_bin2 in lime_furnace2_bin2.values.tolist():
            for item in item_lime_furnace2_bin2:
                if str(item) == "nan":
                    lst_lime_furnace2_bin2.append(0.0)
                else:
                    lst_lime_furnace2_bin2.append(round(item, 2))
        lime_furnace3_bin1 = self.opt_w_in_time.loc[:, ["1,2,0"]]
        lst_lime_furnace3_bin1 = []
        for item_lime_furnace3_bin1 in lime_furnace3_bin1.values.tolist():
            for item in item_lime_furnace3_bin1:
                if str(item) == "nan":
                    lst_lime_furnace3_bin1.append(0.0)
                else:
                    lst_lime_furnace3_bin1.append(round(item, 2))
        return lst_lime_furnace1_bin1, lst_lime_furnace1_bin2, lst_lime_furnace2_bin1, lst_lime_furnace2_bin2, lst_lime_furnace3_bin1

    def opt_in_time_dolomite(self):
        # Dolomite
        dolomite_furnace1_bin1 = self.opt_w_in_time.loc[:, ["2,0,0"]]
        lst_dolomite_furnace1_bin1 = []
        for item_dolomite_furnace1_bin1 in dolomite_furnace1_bin1.values.tolist():
            for item in item_dolomite_furnace1_bin1:
                if str(item) == "nan":
                    lst_dolomite_furnace1_bin1.append(0.0)
                else:
                    lst_dolomite_furnace1_bin1.append(round(item, 2))

        dolomite_furnace1_bin2 = self.opt_w_in_time.loc[:, ["2,1,0"]]
        lst_dolomite_furnace2_bin1 = []
        for item_dolomite_furnace1_bin2 in dolomite_furnace1_bin2.values.tolist():
            for item in item_dolomite_furnace1_bin2:
                if str(item) == "nan":
                    lst_dolomite_furnace2_bin1.append(0.0)
                else:
                    lst_dolomite_furnace2_bin1.append(round(item, 2))

        dolomite_furnace3_bin1 = self.opt_w_in_time.loc[:, ["2,2,0"]]
        lst_dolomite_furnace3_bin1 = []
        for item_dolomite_furnace3_bin1 in dolomite_furnace3_bin1.values.tolist():
            for item in item_dolomite_furnace3_bin1:
                if str(item) == "nan":
                    lst_dolomite_furnace3_bin1.append(0.0)
                else:
                    lst_dolomite_furnace3_bin1.append(round(item, 2))

        return lst_dolomite_furnace1_bin1, lst_dolomite_furnace2_bin1, lst_dolomite_furnace3_bin1

    def create_data_opt_in_time(self):
        lst_iron_furnace1_bin1, lst_iron_furnace1_bin2, lst_iron_furnace2_bin1, lst_iron_furnace2_bin2, lst_iron_furnace3_bin1, lst_iron_furnace3_bin2 = self.opt_w_in_time_iron()
        lst_lime_furnace1_bin1, lst_lime_furnace1_bin2, lst_lime_furnace2_bin1, lst_lime_furnace2_bin2, lst_lime_furnace3_bin1 = self.opt_in_time_lime()
        lst_dolomite_furnace1_bin1, lst_dolomite_furnace2_bin1, lst_dolomite_furnace3_bin1 = self.opt_in_time_dolomite()
        opt_in_time_materials = {
            "iron": [
                {
                    "name": "کوره ۱ - پین ۱",
                    "data": lst_iron_furnace1_bin1
                },
                {
                    "name": "کوره ۱ - پین ۲",
                    "data": lst_iron_furnace1_bin2,
                },
                {
                    "name": "کوره ۲ - پین ۱",
                    "data": lst_iron_furnace2_bin1,
                },
                {
                    "name": "کوره ۲ - پین ۲",
                    "data": lst_iron_furnace2_bin2,
                },
                {
                    "name": "کوره ۳ - پین ۱",
                    "data": lst_iron_furnace3_bin1,
                },
                {
                    "name": "کوره ۳ - پین ۲",
                    "data": lst_iron_furnace3_bin2,
                }
            ],
            "lime": [
                {
                    "name": "کوره ۱ - پین ۱",
                    "data": lst_lime_furnace1_bin1,
                },
                {
                    "name": "کوره ۱ - پین ۲",
                    "data": lst_lime_furnace1_bin2,
                },
                {
                    "name": "کوره ۲ - پین ۱",
                    "data": lst_lime_furnace2_bin1,
                },
                {
                    "name": "کوره ۲ - پین ۲",
                    "data": lst_lime_furnace2_bin2,
                },
                {
                    "name": "کوره ۳ - پین ۱",
                    "data": lst_lime_furnace3_bin1,
                }
            ],
            "dolomite": [
                {
                    "name": "کوره ۱ - پین ۱",
                    "data": lst_dolomite_furnace1_bin1,
                },
                {
                    "name": "کوره ۲ - پین ۱",
                    "data": lst_dolomite_furnace2_bin1,
                },
                {
                    "name": "کوره ۳ - پین ۱",
                    "data": lst_dolomite_furnace3_bin1,
                }
            ]
        }

        data = {
            "time": self.time_opt_in_time(),
            "data": dict(opt_in_time_materials)
        }

        return data

    def create_opt_B_data(self):
        furnace = FurnaceSetting.objects.filter(is_active=True)[0]
        lst_time = [str(furnace.created_at + datetime.timedelta(minutes=item_time_)) for item_time in
                    self.opt_B.loc[:, ["time"]].values.tolist() for item_time_ in item_time]
        header = self.opt_B.columns.values[1:]
        lst_bins = []
        for item in header:
            bins = {
                "bin" + item: [item__ for item_ in self.opt_B.loc[:, [item]].values.tolist() for item__ in item_]
            }
            lst_bins.append(bins)
        data = {
            "time": lst_time,
            "bins": lst_bins
        }
        return data

    def convert_opt_opt_shooting_list_1(self, furnace):
        row = f"{furnace[0]}, {furnace[1]}, {furnace[2]}"
        for item in self.data_convert():
            if item["row"] == row:
                return item["convert"]
        else:
            return ""

    def convert_opt_opt_shooting_list_2(self, furnace):
        row = f"{furnace[0]}, {furnace[1]}, {furnace[2]}"
        for item in self.data_convert():
            if item["row"] == row:
                return item["convert"]
        else:
            return ""

    def create_data_opt_shooting_list(self):
        lst = []
        furnace = FurnaceSetting.objects.filter(is_active=True)[0]
        timezone = datetime.timedelta(hours=3, minutes=30)
        for item_shooting_list in self.opt_shooting_list:
            time = datetime.datetime.now() + datetime.timedelta(minutes=item_shooting_list[0]) + timezone
            data = {
                "start_time": str(time),
                "duration": item_shooting_list[1],
                "data": [{"notification_time": str(time + datetime.timedelta(minutes=item[0])),
                          "furnace_1": self.convert_opt_opt_shooting_list_1(item[1]),
                          "furnace_2": self.convert_opt_opt_shooting_list_2(item[2])
                          } for item in item_shooting_list[2]]
            }
            lst.append(data)

        return lst

    def create_data_json(self):
        opt_actions_output = self.action_output()
        opt_w_in_time = self.create_data_opt_in_time()
        opt_shooting_list = self.create_data_opt_shooting_list()

        data = {
            "opt_actions_output": opt_actions_output,
            "opt_w_in_time": opt_w_in_time,
            "opt_shooting_list": opt_shooting_list
        }
        return dict(data)

    def time_opt_in_time(self):
        parameter = Parameter.objects.filter(is_active=True)[0]
        lst_times = []
        times = self.opt_w_in_time.loc[:, ["time"]]
        for item_times in times.values.tolist():
            for item_time in item_times:
                lst_times.append(str(parameter.created_at + datetime.timedelta(minutes=item_time)))
        return lst_times
