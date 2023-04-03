import requests
import json
import pandas
from pickle5 import pickle

from django.conf import settings


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


def read_excel_analyze(file):
    excel_read = pandas.read_excel(file)
    data_s1 = excel_read["s1"].tolist()
    lst_data_s1 = []
    data_sb1 = excel_read["sb1"].tolist()
    lst_data_sb1 = []
    data_s2 = excel_read["s2"].tolist()
    lst_data_s2 = []
    data_sb2 = excel_read["sb2"].tolist()
    lst_data_sb2 = []
    data_s3 = excel_read["s3"].tolist()
    lst_data_s3 = []
    data_sb3 = excel_read["sb3"].tolist()
    lst_data_sb3 = []

    for i in data_s1:
        if str(i) == "nan":
            lst_data_s1.append(float(0.0))
        else:
            lst_data_s1.append(i)

    for i in data_sb1:
        if str(i) == "nan":
            lst_data_sb1.append(float(0.0))
        else:
            lst_data_sb1.append(i)
    # -----------------------------------------

    for i in data_s2:
        if str(i) == "nan":
            lst_data_s2.append(float(0.0))
        else:
            lst_data_s2.append(i)

    for i in data_sb2:
        if str(i) == "nan":
            lst_data_sb2.append(float(0.0))
        else:
            lst_data_sb2.append(i)

    # -----------------------------------------------

    for i in data_s3:
        if str(i) == "nan":
            lst_data_s3.append(float(0.0))
        else:
            lst_data_s3.append(i)

    for i in data_sb3:
        if str(i) == "nan":
            lst_data_sb3.append(float(0.0))
        else:
            lst_data_sb3.append(i)

    data = {
        "furnace_1": {
            "s1": lst_data_s1,
            "sb1": lst_data_sb1
        },
        "furnace_2": {
            "s2": lst_data_s2,
            "sb2": lst_data_sb2
        },
        "furnace_3": {
            "s3": lst_data_s3,
            "sb3": lst_data_sb3
        }

    }
    return data
