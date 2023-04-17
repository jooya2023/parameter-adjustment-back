# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 16:09:24 2023

@author: Admin
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from parameter.helper.api_cons import create_consumption
from parameter.helper.calculations import main_tread
from django.conf import settings

setting = pd.read_excel(os.path.join(settings.BASE_DIR, 'parameter/helper/input.xlsx'), sheet_name='setting', usecols=[1, 2, 3])
pw = setting.loc[:, "power on"].to_numpy(dtype='int')
taptotap = setting.loc[:, "taptotap"].to_numpy(dtype='int')


f_cons1 = pd.read_excel(os.path.join(settings.BASE_DIR, 'parameter/helper/input.xlsx'), sheet_name='f1', usecols=[1, 2, 3, 4])
f1D = f_cons1.loc[:, "s1"].to_numpy(dtype='float32') / 1000
f1Ds = f_cons1.loc[:, "sbasket1"].to_numpy(dtype='float32') / 1000

f_cons2 = pd.read_excel(os.path.join(settings.BASE_DIR, 'parameter/helper/input.xlsx'), sheet_name='f2', usecols=[1, 2, 3, 4, 5, 6])
f2D = f_cons2.loc[:, "s1"].to_numpy(dtype='float32') / 1000
f2Ds = f_cons2.loc[:, "sbasket1"].to_numpy(dtype='float32') / 1000

f_cons3 = pd.read_excel(os.path.join(settings.BASE_DIR, 'parameter/helper/input.xlsx'), sheet_name='f3', usecols=[1, 2])
f3D = f_cons3.loc[:, "s1"].to_numpy(dtype='float32') / 1000
f3Ds = f_cons3.loc[:, "sbasket1"].to_numpy(dtype='float32') / 1000

lime_cons_rate = [3.2, 3.2, 3.2]
dolomit_cons_rate = [2.1, 2.1, 2.1]

# combobox_binid = [-1,-1,-1]
combobox_binid = [2, 6, 7]
entryhour = [18, 18, 18]
entrymin = [30, 33, 36]
entryduration = [3, 3, 3]

f1lime = (lime_cons_rate[0] / pw[0]) * np.concatenate(
    (np.ones((1, pw[0])).flatten(), np.zeros((1, taptotap[0] - pw[0] + 1)).flatten()))
f2lime = (lime_cons_rate[1] / pw[1]) * np.concatenate(
    (np.ones((1, pw[1])).flatten(), np.zeros((1, taptotap[1] - pw[1] + 1)).flatten()))
f3lime = (lime_cons_rate[2] / pw[2]) * np.concatenate(
    (np.ones((1, pw[2])).flatten(), np.zeros((1, taptotap[2] - pw[2] + 1)).flatten()))

f1dol = (dolomit_cons_rate[0] / pw[0]) * np.concatenate(
    (np.ones((1, pw[0])).flatten(), np.zeros((1, taptotap[0] - pw[0] + 1)).flatten()))
f2dol = (dolomit_cons_rate[1] / pw[1]) * np.concatenate(
    (np.ones((1, pw[1])).flatten(), np.zeros((1, taptotap[1] - pw[1] + 1)).flatten()))
f3dol = (dolomit_cons_rate[2] / pw[2]) * np.concatenate(
    (np.ones((1, pw[2])).flatten(), np.zeros((1, taptotap[2] - pw[2] + 1)).flatten()))

CONS_input = create_consumption(f1D, f1Ds, f2D, f2Ds, f3D, f3Ds, f1lime, f2lime, f3lime, f1dol, f2dol, f3dol)

############################################################
wzero = np.zeros((11, 12))
current_time = datetime.now()
zero_time = current_time - timedelta(minutes=10)
rng12 = pd.date_range(zero_time, current_time, freq='1min').strftime("%H:%M")
wzeroall = pd.DataFrame(wzero, index=rng12)

i = 0

for binid in combobox_binid:
    if (binid > -1):
        d = str(entryhour[i]) + ":" + str(entrymin[i])
        dt = datetime.strptime(d, "%H:%M")
        dtrange = pd.date_range(dt, dt + timedelta(minutes=int(entryduration[i]) - 1), freq='1min').strftime("%H:%M")
        ins1 = wzeroall.index.intersection(dtrange)
        b1 = binid
        if ins1.empty != 1:
            wzeroall.loc[ins1, b1] = 1
    i = i + 1

B_first_11_input = wzeroall.values.tolist()
##############################################################

W_input = [[[] for j in range(3)] for i in range(3)]

W_input[0][0] = [28.8, 28.0]
W_input[0][1] = [28.6, 28.4]
W_input[0][2] = [45.6, 25.2]

W_input[1][0] = [5.32, 2]
W_input[1][1] = [5.88, 2]
W_input[1][2] = [5.8, 3]

W_input[2][0] = [5.68]
W_input[2][1] = [5.6]
W_input[2][2] = [7.68, 4]

s_floor_input = [[[] for j in range(3)] for i in range(3)]
s_floor_input[0][0] = [0, 2]
s_floor_input[0][1] = [0, 2]
s_floor_input[0][2] = [0, 2]

s_floor_input[1][0] = [0, 0.1]
s_floor_input[1][1] = [0, 0.1]
s_floor_input[1][2] = [0, 0.1]

s_floor_input[2][0] = [0]
s_floor_input[2][1] = [0]
s_floor_input[2][2] = [0, 0.1]

storage_input = [[[] for j in range(3)] for i in range(3)]
storage_input[0][0] = [60, 60]
storage_input[0][1] = [12, 60]
storage_input[0][2] = [12, 80]

storage_input[1][0] = [60, 8]
storage_input[1][1] = [12, 8]
storage_input[1][2] = [12, 8]

storage_input[2][0] = [80]
storage_input[2][1] = [12]
storage_input[2][2] = [12, 6]

K_input = [3.1, 2.3, 2.4]

D_R_input = [[8, 5, 5],
             [7, 5, 5],
             [9, 7, 7]]
D_E_input = [[2, 2, 2],
             [2, 2, 2],
             [2, 2, 2]]

disables_raw_input = [(10, 9), (4, 12)]

charge_instantly_choice_input = False


def call_main():
    opt_actions_output, opt_w_in_time, opt_B, opt_shooting_list, STATUS, no_action_spend_time, data = main_tread(W_input, s_floor_input, storage_input, K_input, D_R_input, D_E_input, CONS_input, B_first_11_input,
               disables_raw_input, charge_instantly_choice_input=False)
    return opt_actions_output, opt_w_in_time, opt_B, opt_shooting_list, STATUS, no_action_spend_time, data