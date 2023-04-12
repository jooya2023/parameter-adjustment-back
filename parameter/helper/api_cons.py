import os
import numpy as np
import json
from urllib.request import urlopen
from datetime import datetime, timedelta
import pandas as pd
import pickle
import requests

from django.conf import settings


def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if (gm > 2):
        gy2 = gy + 1
    else:
        gy2 = gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if (days > 365):
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if (days < 186):
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return [jy, jm, jd]


v1 = None
v2 = None
v3 = None


def create_consumption(f1D, f1Ds, f2D, f2Ds, f3D, f3Ds, f1l, f2l, f3l, f1d, f2d, f3d):
    # def create_consumption( ):

    # current_time = datetime.now()
    global v1, v2, v3
    current_time = datetime.strptime("2023/04/04 08:00:11", "%Y/%m/%d %H:%M:%S")
    current_time_str = current_time.strftime("%Y/%m/%d %H:%M:%S")

    jalali_time_c = gregorian_to_jalali(int(current_time_str[0:4]), int(current_time_str[5:7]),
                                        int(current_time_str[8:10]))
    month = str(jalali_time_c[1])
    day = str(jalali_time_c[2])
    if len(str(jalali_time_c[1])) == 1:
        month = "0" + str(jalali_time_c[1])

    if len(str(jalali_time_c[2])) == 1:
        day = "0" + str(jalali_time_c[2])

    fromdate = str(jalali_time_c[0]) + "/" + month + "/" + day + " " + current_time_str[11:19]
    current_time_jalali = datetime.strptime(fromdate, "%Y/%m/%d %H:%M:%S")

    forecast_hours = 24
    total_time = forecast_hours * 60
    start = 12

    last_time = current_time + timedelta(hours=forecast_hours)
    last_time_str = last_time.strftime("%Y/%m/%d %H:%M:%S")

    jalali_time_l = gregorian_to_jalali(int(last_time_str[0:4]), int(last_time_str[5:7]), int(last_time_str[8:10]))
    toDate = str(jalali_time_l[0]) + "/" + str(jalali_time_l[1]) + "/" + str(jalali_time_l[2]) + " " + last_time_str[
                                                                                                       11:19]

    myobj = {'fromDate': fromdate, 'toDate': toDate}

    ################## API Link ########################
    # url_ProductionPlan = "http://ias22:8735/MeltShopHttpServiceLibrary/GetProductionPlan"
    # data_ProductionPlan = requests.post(url_ProductionPlan,json = myobj)
    # response_ProductionPlan = data_ProductionPlan.content
    # data_ProductionPlan = json.loads(data_ProductionPlan.content)
    # dataProductionPlan =data_ProductionPlan

    ##################### File #############################

    f2 = open(os.path.join(settings.BASE_DIR, 'parameter/helper/GetProductionPlan.json'))
    dataProductionPlan = json.load(f2)
    temp = []

    pp = []

    dtnullvalue_str = "1348/10/11 00:00:00"
    dtnullvalue = datetime.strptime(dtnullvalue_str, "%Y/%m/%d %H:%M:%S")

    for i in range(0, len(dataProductionPlan)):
        if dataProductionPlan[i]['AreaName'] == 'EAF':
            if ((dataProductionPlan[i]['ProcessStartDate'] == dtnullvalue_str
                 or dataProductionPlan[i]['ProcessStopDate'] == dtnullvalue_str or dataProductionPlan[i][
                     'ProcessStop'] == 0)
                    and fromdate < dataProductionPlan[i]['ProcessSchedStopDate'] and dataProductionPlan[i][
                        'ProcessSchedStartDate'] < toDate):

                tstart = datetime.strptime(dataProductionPlan[i]['ProcessStartDate'], "%Y/%m/%d %H:%M:%S")
                tend = datetime.strptime(dataProductionPlan[i]['ProcessStopDate'], "%Y/%m/%d %H:%M:%S")
                furnaceid = dataProductionPlan[i]['StationCode']

                tpstart = datetime.strptime(dataProductionPlan[i]['ProcessSchedStartDate'], "%Y/%m/%d %H:%M:%S")
                tpend = datetime.strptime(dataProductionPlan[i]['ProcessSchedStopDate'], "%Y/%m/%d %H:%M:%S")

                furnaceid = dataProductionPlan[i]['StationCode']

                temp = np.append(temp, [(tpend - tpstart) // 60, dataProductionPlan[i]['StationCode']])

                if tstart < current_time_jalali and tend == dtnullvalue and current_time_jalali < tpend:

                    if tstart != dtnullvalue:
                        diffstart = current_time_jalali - tstart
                        remtime = tpend - current_time_jalali
                        # pp = np.append(pp,[(tend - tstart).seconds/60,remtime.seconds/60,furnaceid])
                        pp = np.append(pp, [remtime.seconds / 60, furnaceid, dataProductionPlan[i]['BucketPlaned']])
                    else:

                        pp = np.append(pp, [(tpend - tpstart).seconds / 60, furnaceid,
                                            dataProductionPlan[i]['BucketPlaned']])

                elif current_time_jalali < tpstart and tstart == dtnullvalue and tend == dtnullvalue:
                    pp = np.append(pp,
                                   [(tpend - tpstart).seconds / 60, furnaceid, dataProductionPlan[i]['BucketPlaned']])

    consumption = np.zeros([total_time, 9])

    production_program1 = []
    production_program2 = []
    production_program3 = []
    sabad1 = []
    sabad2 = []
    sabad3 = []
    for i in range(0, len(pp) - 1, 3):
        period = pp[i]
        fid = pp[i + 1]

        if fid == 1:
            sabad1 = np.append(sabad1, pp[i + 2])
            production_program1 = np.append(production_program1, pp[i])
            production_program1 = production_program1.astype(int)

        elif fid == 2:
            sabad2 = np.append(sabad2, pp[i + 2])
            production_program2 = np.append(production_program2, pp[i])
            production_program2 = production_program2.astype(int)

        elif fid == 3:
            sabad3 = np.append(sabad3, pp[i + 2])
            production_program3 = np.append(production_program3, pp[i])
            production_program3 = production_program3.astype(int)

    ####################################
    j = start
    cnt = 0

    # sabad1=np.zeros(len(production_program1))
    # #for i in range(0,len(production_program1),2):
    # #    sabad1[i] = 1

    # sabad2=np.zeros(len(production_program2))
    # #for i in range(0,len(production_program2),2):
    # #    sabad2[i] = 1

    # sabad3=np.zeros(len(production_program3))
    # #for i in range(0,len(production_program3),2):
    # #    sabad3[i] = 1

    s_cnt = 0
    for p in production_program1:

        if sabad1[s_cnt] == 1:
            F1D = np.array(f1Ds) / 2
        else:
            F1D = np.array(f1D) / 2

        if p > len(F1D):
            diff = int(p - len(F1D))
            v1 = np.concatenate((F1D, np.zeros((1, diff)).flatten()))
            v2 = np.concatenate((f1l, np.zeros((1, diff)).flatten()))
            v3 = np.concatenate((f1d, np.zeros((1, diff)).flatten()))

        elif p < len(F1D):
            v1 = F1D[1:p + 1]
            v2 = f1l[1:p + 1]
            v3 = f1d[1:p + 1]
        elif p == len(F1D):
            v1 = F1D
            v2 = f1l
            v3 = f1d

        consumption[j: j + p, 0] = v1
        consumption[j: j + p, 3] = v2
        consumption[j: j + p, 6] = v3
        j = j + p + 1
        cnt = cnt + 1
        s_cnt = s_cnt + 1

    ########################################
    j = start

    s_cnt = 0
    for p in production_program2:
        if sabad2[s_cnt] == 1:
            F2D = np.array(f2Ds) / 2
        else:
            F2D = np.array(f2D) / 2

        if p > len(F2D):
            diff = int(p - len(F2D))
            v1 = np.concatenate((F2D, np.zeros((1, diff)).flatten()))
            v2 = np.concatenate((f2l, np.zeros((1, diff)).flatten()))
            v3 = np.concatenate((f2d, np.zeros((1, diff)).flatten()))

        elif p < len(F2D):
            v1 = F2D[1:p + 1]
            v2 = f2l[1:p + 1]
            v3 = f2d[1:p + 1]
        elif p == len(F2D):
            v1 = F2D
            v2 = f2l
            v3 = f2d
        consumption[j: j + p, 1] = v1
        consumption[j: j + p, 4] = v2
        consumption[j: j + p, 7] = v3
        j = j + p + 1
        s_cnt = s_cnt + 1
    #####################################
    j = start
    s_cnt = 0
    for p in production_program3:
        if sabad3[s_cnt] == 1:
            F3D = np.array(f3Ds)
        else:
            F3D = np.array(f3D)

        if p > len(F3D):
            diff = int(p - len(F3D))
            v1 = np.concatenate((np.array(F3D), np.zeros((1, diff)).flatten()))
            v2 = np.concatenate((np.array(f3l), np.zeros((1, diff)).flatten()))
            v3 = np.concatenate((np.array(f3d), np.zeros((1, diff)).flatten()))

        elif p < len(F3D):
            v1 = np.array(F3D)[1:p + 1]
            v2 = np.array(f3l)[1:p + 1]
            v3 = np.array(f3d)[1:p + 1]

        elif p == len(F3D):
            v1 = np.array(F3D)
            v2 = np.array(f3l)
            v3 = np.array(f3d)


        consumption[j: j + p, 2] = v1
        consumption[j: j + p, 5] = v2
        consumption[j: j + p, 8] = v3
        j = j + p + 1
        s_cnt = s_cnt + 1

    df = pd.DataFrame(consumption)
    CONS = np.empty([3, 3], dtype=object)

    for i in range(3):
        for j in range(3):
            CONS[i][j] = df[3 * i + j].tolist()
    return CONS
