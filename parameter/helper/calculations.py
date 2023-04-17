import os
import copy
import math
import time

import numpy as np

import pandas as pd

from django.conf import settings


# ------ Functions

def operation(W_in, action_in, time_in):
    if action_in is None:
        a_time = 0
    else:
        a_time = action_in[0]

    W_out = copy.deepcopy(W_in)

    for i in range(time_in, time_in + a_time):

        W_in_time[i] = copy.deepcopy(W_out)

        for j in range(3):
            for k in range(3):
                for z in range(len(W_out[j][k])):
                    if j == 0 and k == 2:
                        W_out[j][k][z] += B[j][k][z][i - D_R[j][k]] * K[j]
                    elif j == 1:
                        W_out[j][k][z] += B[j][k][z][i - D_R[j][k]] * K[j]
                    elif j == 2 and k == 2:
                        W_out[j][k][z] += B[j][k][z][i - D_R[j][k]] * K[j]
                    else:
                        if j == 0:
                            W_out[j][k][z] -= ((CONS[j][k][i]) - B[j][k][z][i - D_R[j][k]] * K[j])
                        else:
                            W_out[j][k][z] -= (CONS[j][k][i] - B[j][k][z][i - D_R[j][k]] * K[j])

        # DRI
        if W_out[0][2][0] > W_out[0][2][1]:
            if W_out[0][2][1] - s_floor[0][2][1] > CONS[0][2][i]:
                W_out[0][2][1] -= CONS[0][2][i]
            else:
                W_out[0][2][0] -= CONS[0][2][i]
        else:
            if W_out[0][2][0] - s_floor[0][2][0] > CONS[0][2][i]:
                W_out[0][2][0] -= CONS[0][2][i]
            else:
                W_out[0][2][1] -= CONS[0][2][i]

        # LIM
        for j in range(3):
            if W_out[1][j][0] > W_out[1][j][1]:
                if W_out[1][j][1] - s_floor[1][j][1] > CONS[1][j][i]:
                    W_out[1][j][1] -= CONS[1][j][i]
                else:
                    W_out[1][j][0] -= CONS[1][j][i]
            else:
                if W_out[1][j][0] - s_floor[1][j][0] > CONS[1][j][i]:
                    W_out[1][j][0] -= CONS[1][j][i]
                else:
                    W_out[1][j][1] -= CONS[1][j][i]

        # DOL
        if W_out[2][2][0] > W_out[2][2][1]:
            if W_out[2][2][1] - s_floor[2][2][1] > CONS[2][2][i]:
                W_out[2][2][1] -= CONS[2][2][i]
            else:
                W_out[2][2][0] -= CONS[2][2][i]
        else:
            if W_out[2][2][0] - s_floor[2][2][0] > CONS[2][2][i]:
                W_out[2][2][0] -= CONS[2][2][i]
            else:
                W_out[2][2][1] -= CONS[2][2][i]

    return W_out, time_in + a_time


def delay_on_switch(action_in, past_action_in):
    if past_action_in is None:
        return False, 0

    t1, i1, j1, k1 = past_action_in
    t2, i2, j2, k2 = action_in

    if node is not None and node.wait_till_empty:
        return True, D_R[i1][i1] + D_E[i1][i1]

    if i1 == i2 and j1 == j2 and k1 == k2:
        return True, D_R[i1][i1] + D_E[i1][i1]

    if i1 == 0 and i2 == 0:
        if (j1 == 0 and j2 == 1) or (j1 == 1 and j2 == 0):
            return False, 0

    return True, D_R[i1][i1] + D_E[i1][i1]


def spend_switch_time(W_in, action_in, past_action_in, time_in):
    W_out = copy.deepcopy(W_in)
    time_out = time_in

    have_delay, delay_val = delay_on_switch(action_in, past_action_in)

    if node.parent is None and node.past_action is not None:
        if delay_val == 0:
            worker_choice = charge_instantly_choice
            if worker_choice:
                pass
            elif not worker_choice:
                delay_val = (D_R[action_in[1]][action_in[2]] + D_E[action_in[1]][action_in[2]]) - (
                        11 - 1 - last_time_b_before)
        else:
            delay_val = delay_val - (11 - 1 - last_time_b_before)

    if delay_val != 0:
        W_out, time_out = operation(W_out, (delay_val,), time_out)

    return W_out, time_out


def check_w_validation(w_in):
    for i in range(3):
        for j in range(3):
            for k in range(len(w_in[i][j])):
                if w_in[i][j][k] < s_floor[i][j][k]:
                    return False
    return True


def format_w(w_inp):
    out = [[[] for j in range(3)] for i in range(3)]

    for i in range(3):
        for j in range(3):
            for k in range(len(w_inp[i][j])):
                out[i][j].append(round(w_inp[i][j][k], 4))

    return out


def check_time_for_switch_now(a_one, a_two, a_three):
    bool_val, switch_2_3 = delay_on_switch(a_three, a_two)

    charge_time = T_MIN_Charge[0] + 1

    if a_one[0] > 60:
        return True

    if a_one[0] + charge_time + switch_2_3 <= a_two[0]:
        return True
    return False


# ======== Class

class Node:
    def __init__(self, parent_in, W_in, time_in, action, past_action_in):
        global node_counter
        self.parent = parent_in

        self.W = copy.deepcopy(W_in)
        self.W_dec_point = copy.deepcopy(W_in)

        self.time = time_in
        self.time_dec_point = time_in
        self.action = action
        self.past_action = past_action_in

        self.make_child = False
        self.child = None
        self.possible_actions = []

        self.t_upper = []
        self.t_opr = []

        self.prediction_problem = False

        if parent_in is not None:
            self.depth = parent_in.depth + 1
        else:
            self.depth = 0

        self.number = node_counter
        node_counter += 1

        self.wait_till_empty = False

        self.do_action()

    def do_action(self):
        self.W_dec_point, self.time_dec_point = operation(self.W, self.action, self.time)

        self.decision_point()

        if len(self.possible_actions) == 0:

            find_answer = False
            while not find_answer:
                if self.t_opr[0][1] == 0:
                    t_upper_in = -1

                    if self.t_opr[0][2] == 2:
                        max_t = -1
                        for t in self.t_upper:
                            if t[1] == 0 and t[2] == 2:
                                if max_t < t[0]:
                                    max_t = t[0]

                        t_upper_in = max_t
                    else:
                        for t in self.t_upper:
                            if t[1] == 0 and t[2] == self.t_opr[0][2] and t[3] == self.t_opr[0][3]:
                                t_upper_in = t[0]
                                break

                    if t_upper_in < 5:
                        no_action = [10, -1, -1, -1]
                        no_action_spend_time.append((self.time_dec_point, no_action[0]))
                        self.W_dec_point, self.time_dec_point = operation(self.W_dec_point, no_action,
                                                                          self.time_dec_point)
                        self.t_upper = []
                        self.t_opr = []
                        self.wait_till_empty = True
                        self.decision_point()
                    else:
                        break

                elif self.t_opr[0][1] != 0:
                    t_upper_in = -1

                    for t in self.t_upper:
                        if t[1] == self.t_opr[0][1] and t[2] == self.t_opr[0][2] and t[3] == self.t_opr[0][3]:
                            t_upper_in = t[0]
                            break

                    if t_upper_in < 2:
                        no_action = [10, -1, -1, -1]
                        no_action_spend_time.append((self.time_dec_point, no_action[0]))
                        self.W_dec_point, self.time_dec_point = operation(self.W_dec_point, no_action,
                                                                          self.time_dec_point)
                        self.t_upper = []
                        self.t_opr = []
                        self.wait_till_empty = True
                        self.decision_point()
                    else:
                        break

                if len(self.possible_actions) != 0:
                    find_answer = True

    def compute_t_upper(self, i, j, k):
        return self.calc_t_upper(i, j, k, CONS[i][j])

    def compute_t_opr(self, i, j, k):
        return self.calc_t_opr(i, j, k, CONS[i][j])

    def remove_disables(self):
        for d in disables:
            if d[0] < self.time:
                disables.remove(d)

        for d in disables:
            for to in self.t_opr:
                if to[3] == 2:
                    if to[1] == d[1] and to[2] == d[2]:
                        self.t_opr.remove(to)
                        continue
                else:
                    if to[1] == d[1] and to[2] == d[2] and to[3] == d[3]:
                        self.t_opr.remove(to)
                        continue

    def bin_info_for_next_actions(self):

        for i in range(3):
            for j in range(3):
                if i == 0:
                    self.t_upper.append((self.compute_t_upper(i, j, 0), i, j, 0))
                    self.t_upper.append((self.compute_t_upper(i, j, 1), i, j, 1))
                else:
                    self.t_upper.append((self.compute_t_upper(i, j, 0), i, j, 0))

                if (i == 0 and j == 0) or (i == 0 and j == 1):
                    self.t_opr.append((self.compute_t_opr(i, j, 0), i, j, 0))
                    self.t_opr.append((self.compute_t_opr(i, j, 1), i, j, 1))
                elif i == 2 and (j == 0 or j == 1):
                    self.t_opr.append((self.compute_t_opr(i, j, 0), i, j, 0))
                else:
                    # k = 2 => (0,1)
                    self.t_opr.append((self.compute_t_opr(i, j, 0) + self.compute_t_opr(i, j, 1), i, j, 2))

        self.remove_disables()

        self.t_opr.sort(key=lambda tup: tup[0])

    def make_possible_actions_v_3(self):

        act_1 = self.t_opr[0]

        t_upper_f = -1

        bin_num = -1

        if (act_1[1] == 1) or (act_1[1] == 2 and act_1[2] == 2):
            for x in self.t_upper:
                if x[1] == act_1[1] and x[2] == act_1[2]:
                    t_upper_f = int(x[0])
                    break
        elif act_1[1] == 0 and act_1[2] == 2:
            max_t_up = 0
            for x in self.t_upper:
                if x[1] == act_1[1] and x[2] == act_1[2]:
                    if max_t_up < int(x[0]):
                        max_t_up = int(x[0])
                        bin_num = x[3]
            t_upper_f = max_t_up
        else:
            for x in self.t_upper:
                if x[1] == act_1[1] and x[2] == act_1[2] and x[3] == act_1[3]:
                    t_upper_f = int(x[0])
                    break

        have_delay, delay_val = delay_on_switch(act_1, self.action)

        out_time_info_1 = -1

        for i in range(t_upper_f, T_MIN_Charge[act_1[1]], -1):
            find_answer = True

            val = 0
            X = i + delay_val

            prediction_step = min(10, len(self.t_opr) - 1)
            for j in range(prediction_step):
                if X + val < self.t_opr[j + 1][0] - D_R[self.t_opr[j + 1][1]][self.t_opr[j + 1][2]]:
                    have_delay, delay_val = delay_on_switch(self.t_opr[j], self.t_opr[j + 1])
                    val += T_MIN_Charge[self.t_opr[j + 1][1]] + delay_val
                    continue
                else:
                    find_answer = False
                    break

            if find_answer:
                out_time_info_1 = i
                break

        if act_1[1] != 0:
            act_1 = (act_1[0], act_1[1], act_1[2], 0)
        elif act_1[1] == 0 and act_1[2] == 2:
            act_1 = (act_1[0], act_1[1], act_1[2], bin_num)

        for y in range(min(out_time_info_1, 25), max(min(out_time_info_1, 25) - 10, T_MIN_Charge[act_1[1]]), -1):
            self.possible_actions.append((y, act_1[1], act_1[2], act_1[3]))

        if False:
            pass
        else:
            ## second action

            act_1 = self.t_opr[1]

            t_upper_f = -1

            bin_num = -1

            if (act_1[1] == 1) or (act_1[1] == 2 and act_1[2] == 2):
                for x in self.t_upper:
                    if x[1] == act_1[1] and x[2] == act_1[2]:
                        t_upper_f = int(x[0])
                        break
            elif act_1[1] == 0 and act_1[2] == 2:
                max_t_up = 0
                for x in self.t_upper:
                    if x[1] == act_1[1] and x[2] == act_1[2]:
                        if max_t_up < int(x[0]):
                            max_t_up = int(x[0])
                            bin_num = x[3]
                t_upper_f = max_t_up
            else:
                for x in self.t_upper:
                    if x[1] == act_1[1] and x[2] == act_1[2] and x[3] == act_1[3]:
                        t_upper_f = int(x[0])
                        break

            have_delay, delay_val = delay_on_switch(act_1, self.action)

            out_time_info_2 = -1

            for i in range(t_upper_f, T_MIN_Charge[act_1[1]], -1):
                find_answer = True

                val = 0
                X = i + delay_val

                prediction_step = min(10, len(self.t_opr) - 1) - 1
                for j in range(prediction_step):
                    if X + val < self.t_opr[j + 2][0] - D_R[self.t_opr[j + 2][1]][self.t_opr[j + 2][2]]:
                        have_delay, delay_val = delay_on_switch(self.t_opr[j + 1], self.t_opr[j + 2])
                        val += T_MIN_Charge[self.t_opr[j + 2][1]] + delay_val
                        continue
                    else:
                        find_answer = False
                        break

                if find_answer:
                    out_time_info_2 = i
                    break

            if out_time_info_1 == -1 and out_time_info_2 == -1:
                self.prediction_problem = True

            if act_1[1] != 0:
                act_1 = (act_1[0], act_1[1], act_1[2], 0)
            elif act_1[1] == 0 and act_1[2] == 2:
                act_1 = (act_1[0], act_1[1], act_1[2], bin_num)

            for y in range(min(out_time_info_2, 25), max(min(out_time_info_2, 25) - 10, T_MIN_Charge[act_1[1]]), -1):
                self.possible_actions.append((y, act_1[1], act_1[2], act_1[3]))

    def decision_point(self):
        self.bin_info_for_next_actions()

        self.decrease_switch_delay_now()

        self.make_possible_actions_v_3()

        self.make_child = True

    def go_next_state(self):
        if not check_w_validation(self.W_dec_point):
            self.del_B_go_back()
            return True, None, None, None, -1

        if not self.check_possibility_300min():
            self.del_B_go_back()
            return True, None, None, None, -1

        try:
            chosen_action = self.possible_actions.pop(0)
        except:
            if self.prediction_problem:
                self.del_B_go_back()
                return True, None, None, None, -1
            else:
                self.del_B_go_back()
                return True, None, None, None, -1

        new_W, new_time = spend_switch_time(self.W_dec_point, chosen_action, self.action, self.time_dec_point)

        if not check_w_validation(new_W):
            self.del_B_go_back()
            return True, None, None, None, -1

        self.make_B(chosen_action, new_time)

        return False, self, new_W, chosen_action, new_time

    def calc_t_upper(self, i, j, k, cons):

        empty_w = storage[i][j][k] - self.W_dec_point[i][j][k]

        timer = 0

        for t in range(self.time_dec_point, min(MAX_TIME_DURATION + 30, self.time_dec_point + 30)):
            empty_w += (cons[t] - B[i][j][k][t - D_R[i][j]] * K[i] - K[i])

            if empty_w > 0:
                timer += 1
            else:
                timer -= 1
                break

        if timer == -1:
            return 0
        return timer

    def calc_t_opr(self, i, j, k, cons):
        w_calc = copy.deepcopy(self.W_dec_point[i][j][k])

        if i == 0 and j != 2:
            if w_calc >= 0.65 * storage[i][j][k]:
                return 1000

        s_floor_in = s_floor[i][j][k]
        timer = 0

        for t in range(self.time_dec_point, min(MAX_TIME_DURATION, self.time_dec_point + Time_Prediction)):
            w_calc -= (cons[t] - B[i][j][k][t - D_R[i][j]] * K[i])

            if w_calc > s_floor_in:
                timer += 1
            else:
                timer -= 1
                break

        return timer - 1

    def make_B(self, chosen_action, new_time):
        t, i, j, k = chosen_action
        if k == 2:
            B[i][j][0][new_time:new_time + t] = 1

        else:
            B[i][j][k][new_time:new_time + t] = 1

    def del_B_go_back(self):
        Tresh = 30

        for i in range(3):
            for j in range(3):
                for k in range(2):
                    B[i][j][k][self.time:self.time_dec_point + Tresh] = 0

    def swap_actions(self, ind1, ind2):
        temp = self.t_opr[ind2]
        self.t_opr[ind2] = self.t_opr[ind1]
        self.t_opr[ind1] = temp

    def decrease_switch_delay_now(self):

        a_one = self.action
        a_two = self.t_opr[0]
        a_three = self.t_opr[1]

        if a_one is None:
            return

        if a_one[1:3] == (0, 0) and a_two[1:3] != (0, 1) and a_three[1:3] == (0, 1):
            if check_time_for_switch_now(a_one, a_two, a_three):
                self.swap_actions(0, 1)

        elif a_one[1:3] == (0, 1) and a_two[1:3] != (0, 0) and a_three[1:3] == (0, 0):
            if check_time_for_switch_now(a_one, a_two, a_three):
                self.swap_actions(0, 1)

    def check_possibility_300min(self):

        time_of_prediction = Time_Prediction

        w_need = [[0, 0, 0],
                  [0, 0, 0],
                  [0, 0, 0]]

        t_need = [[0, 0, 0],
                  [0, 0, 0],
                  [0, 0, 0]]

        num_charge_need = [[0, 0, 0],
                           [0, 0, 0],
                           [0, 0, 0]]

        for i in range(3):
            for j in range(3):
                if i == 0 and (j == 0 or j == 1):
                    w_need[i][j] = 2 * (
                            cons_integral[i][j][self.time_dec_point + time_of_prediction] - cons_integral[i][j][
                        self.time_dec_point])
                else:
                    w_need[i][j] = cons_integral[i][j][self.time_dec_point + time_of_prediction] - cons_integral[i][j][
                        self.time_dec_point]

        for i in range(3):
            for j in range(3):
                for k in range(len(W[i][j])):
                    w_need[i][j] -= self.W_dec_point[i][j][k]

        Total_time = 0

        for i in range(3):
            for j in range(3):
                t_need[i][j] = max(w_need[i][j] / K[i], 0)
                Total_time += t_need[i][j]

        for i in range(3):
            for j in range(3):
                num_charge_need[i][j] = math.ceil(t_need[i][j] / ch_psb_charge_time[i])

        Total_time += num_charge_need[0][2] * ch_psb_delay[0]

        for i in range(1, 3):
            for j in range(3):
                # Total_time += 2 * num_charge_need[i][j] * ch_psb_delay[i]
                Total_time += num_charge_need[i][j] * ch_psb_delay[i]

        # Total_time += math.ceil(abs(num_charge_need[0][0] - num_charge_need[0][1]) / 2) * ch_psb_delay[0]

        if Total_time <= time_of_prediction:
            return True
        return False

    def check_65percent_shooting(self, ch_action):
        if self.action is not None and delay_on_switch(self.action, ch_action)[1] == 0:
            i, j, k = self.action[1:]

            if self.W_dec_point[i][j][k] + K[i] * (D_R[i][j] - 1) > 0.65 * storage[i][j][k]:
                return True
        return False


# ------ Functions

def read_cons():
    global MAX_TIME_DURATION, CONS
    # Test:
    # time: 4670
    # df = pd.read_excel('./Data/Test-Data/input--new.xlsx', sheet_name='consumption', header=None)
    # # time: 1058
    # df = pd.read_excel('./Data/Test-Data/input_0812101.xlsx', sheet_name='consumption', header=None)
    # # time: 537
    # df = pd.read_excel('./Data/Test-Data/consumption_201201.xlsx', sheet_name='cons_500min_bkt1', header=None)
    # # time: 537
    # df = pd.read_excel('./Data/Test-Data/consumption_201201.xlsx', sheet_name='cons_500min_bkt13', header=None)
    # # time: 290
    # df = pd.read_excel('./Data/Test-Data/consumption_201201.xlsx', sheet_name='cons_300min_bkt13', header=None)
    # # time: 1450
    df = pd.read_excel(os.path.join(settings.BASE_DIR, 'parameter/helper/CONS.xlsx'), sheet_name='consumption',
                       header=None)
    # # time: 1450
    # df = pd.read_excel('./Data/Test-Data/consumption_12_23.xlsx', sheet_name='consumption2_12_to_23', header=None)
    # # time: 900
    # df = pd.read_excel('./Data/Test-Data/consumption_12_23.xlsx', sheet_name='consumption_300_60_300', header=None)

    # df = pd.read_excel('./Data/inititalization.xlsx', header=None)
    # df = pd.read_excel('./Data/input_191101.xlsx', sheet_name='consumption', header=None)
    # df = pd.read_excel('./Data/input_191101-edit.xlsx', sheet_name='consumption', header=None)
    # df = pd.read_excel('./Data/input_191101-e2.xlsx', sheet_name='consumption', header=None)
    # df = pd.read_excel('./Data/input_0812101.xlsx', sheet_name='consumption', header=None)
    # df = pd.read_excel('./Data/input--new.xlsx', sheet_name='consumption', header=None)
    # df = pd.read_excel('./Data/input_0812101 - Copy.xlsx', sheet_name='consumption', header=None)
    # df = pd.read_excel('./Data/input2_0912101.xlsx', sheet_name='consumption', header=None)
    # df = pd.read_excel('./Data/input3_0912101.xlsx', sheet_name='consumption', header=None)

    for i in range(3):
        for j in range(3):
            CONS[i][j] = df[3 * i + j].tolist()

    return CONS


def fill_gap():
    global action_output

    action_output_helper = []

    for index in range(len(action_output)):
        try:
            if action_output[index][0] + action_output[index][1] == action_output[index + 1][0]:
                action_output_helper.append(action_output[index])
            else:
                action_output_helper.append(action_output[index])

                action_output_helper.append((action_output[index][0] + action_output[index][1],
                                             action_output[index + 1][0] - (action_output[index][0] +
                                                                            action_output[index][
                                                                                1]), '', '', ''))
        except:
            action_output_helper.append(action_output[index])

    action_output = action_output_helper


def save_actions_output():
    fill_gap()

    df_save_action_output = pd.DataFrame(action_output, columns=['start-time', 'duration', 'i', 'j', 'k'])

    file_name = f'{path}/log-actions-output.xlsx'
    df_save_action_output.to_excel(file_name)

    return df_save_action_output


def save_w_in_time():
    w_list = []

    co = 0
    for w in W_in_time:
        tp = [co, ]
        for i in range(3):
            for j in range(3):
                for k in range(len(w[i][j])):
                    tp.append(w[i][j][k])
        w_list.append(tp)
        co += 1

    df_w_in_time = pd.DataFrame(w_list,
                                columns=['time', '0,0,0', '0,0,1', '0,1,0', '0,1,1', '0,2,0', '0,2,1', '1,0,0', '1,0,1',
                                         '1,1,0', '1,1,1', '1,2,0', '1,2,1', '2,0,0', '2,1,0', '2,2,0', '2,2,1'])

    file_name = f'{path}/log-weight.xlsx'
    df_w_in_time.to_excel(file_name)

    return df_w_in_time


def save_B():
    b_list = []

    for t in range(MAX_TIME_DURATION):
        tp = [t, ]
        for i in range(3):
            for j in range(3):
                if i == 0:
                    tp.append(B[i][j][0][t])
                    tp.append(B[i][j][1][t])
                else:
                    tp.append(B[i][j][0][t])

        b_list.append(tp)

    df_B = pd.DataFrame(b_list,
                        columns=['time', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                                 '10', '11', '12'])

    file_name = f'{path}/log-B.xlsx'
    df_B.to_excel(file_name)

    return df_B


def double_del_B_go_back(nd):
    Tresh = 30

    for i in range(3):
        for j in range(3):
            for k in range(2):
                B[i][j][k][nd.time:nd.time_dec_point + Tresh] = 0


def save_shooting_list():
    shooting_list = []

    index = 0
    while index <= len(action_output):

        log = []
        counter = 0

        try:
            while action_output[index][2] != '':
                counter += 1
                log.append(action_output[index])
                index += 1
        except:
            pass

        if counter > 1:
            # data: (start_charging_time, sum_shooting, [(t, bin1, bin2), (t, bin2, bin3), ...])

            shooting_sum = 0
            shooter_changes = []

            for l in log:
                shooting_sum += l[1]

            for num in range(len(log) - 1):
                shooter_changes.append((log[num][0] + log[num][1] + 6, (log[num][2], log[num][3], log[num][4]),
                                        (log[num + 1][2], log[num + 1][3], log[num + 1][4])))

            shooting_list.append((log[0][0], shooting_sum, shooter_changes))

        index += 1

    return shooting_list


def save_log():
    global opt_actions_output, opt_w_in_time, opt_B, opt_shooting_list, no_action_spend_time

    opt_actions_output = save_actions_output()

    opt_w_in_time = save_w_in_time()

    opt_B = save_B()

    opt_shooting_list = save_shooting_list()


### check_possibility_200min Requirements
def clac_cons_integral():
    ary = np.zeros([3, 3, len(CONS[0][0])])

    for tc in range(1, len(CONS[0][0]) - 1):
        for i in range(3):
            for j in range(3):
                ary[i][j][tc + 1] = CONS[i][j][tc + 1] + ary[i][j][tc]
    return ary


def furnace_converter_bin2matrix(dr):
    num = dr[1]

    if num == 1:
        return dr[0], 0, 0, 0
    elif num == 2:
        return dr[0], 0, 0, 1
    elif num == 3:
        return dr[0], 0, 1, 0
    elif num == 4:
        return dr[0], 0, 1, 1
    elif num == 5:
        return dr[0], 0, 2, 0
    elif num == 6:
        return dr[0], 0, 2, 1
    elif num == 7:
        return dr[0], 1, 0, 0
    elif num == 8:
        return dr[0], 1, 1, 0
    elif num == 9:
        return dr[0], 1, 2, 0
    elif num == 10:
        return dr[0], 2, 0, 0
    elif num == 11:
        return dr[0], 2, 1, 0
    elif num == 12:
        return dr[0], 2, 2, 0


def furnace_converter_trix2bin(mt):
    i, j, k = mt[1:]

    if i == 0:
        if j == 0:
            if k == 0:
                return 1
            elif k == 1:
                return 2
        elif j == 1:
            if k == 0:
                return 3
            elif k == 1:
                return 4
        elif j == 2:
            return 56
    elif i == 1:
        if j == 0:
            return 7
        elif j == 1:
            return 8
        elif j == 2:
            return 9
    elif i == 2:
        if j == 0:
            return 10
        elif j == 1:
            return 11
        elif j == 2:
            return 12


def add_disables():
    for dr in disables_raw:
        disables.append(furnace_converter_bin2matrix(dr))


def add_B_first_11():
    global last_time_b_before, starting_action

    temp = -1
    f_i, f_j, f_k = -1, -1, -1

    for t in range(11):
        row = B_first_11.iloc[t]
        index = 0

        for i in range(3):
            for j in range(3):
                if i == 0:
                    for k in range(2):
                        B[i][j][k][t] = row[index + 1]

                        if row[index + 1] == 1:
                            temp = t
                            f_i, f_j, f_k = i, j, k

                        index += 1

                else:
                    B[i][j][0][t] = row[index + 1]

                    if row[index + 1] == 1:
                        temp = t
                        f_i, f_j, f_k = i, j, k

                    index += 1

    if temp != -1:
        last_time_b_before = temp

        starting_action = (0, f_i, f_j, f_k)


def del_B_back_to_top():
    for i in range(3):
        for j in range(3):
            for k in range(2):
                B[i][j][k][node.time:MAX_TIME_SEARCH_NODE] = 0


def back_to_top():
    global node, level_check

    while node.depth != level_check:
        node = node.parent
        action_history.pop()
        action_output.pop()

    if len(node.possible_actions) == 0:
        if node.parent is None:
            return
        node = node.parent
        action_history.pop()
        action_output.pop()
        level_check -= 1

    del_B_back_to_top()


def is_full():
    for tu in node.t_upper:
        if tu[0] > T_MIN_Charge[tu[1]]:
            return False
    return True


def zero_point():
    for to in node.t_opr:
        if to[0] < 290:
            return False
    return True


# ___________SETTINGS___________
# path = './Data/Test-Data/Result/input--new'

# path = './Data/Test-Data/Result/input_0812101'
#
# path = './Data/Test-Data/Result/consumption_201201-cons_500min_bkt13'
# path = './Data/Test-Data/Result/consumption_201201-cons_500min_bkt1'
# path = './Data/Test-Data/Result/consumption_201201-cons_300min_bkt13'
#
# path = './Data/Test-Data/Result/consumption_12_23-consumption2_12_to_23'
# path = './Data/Test-Data/Result/consumption_12_23-consumption_300_60_300'
path = os.path.join(settings.BASE_DIR, 'parameter/helper/consumption_12_23-consumption_12_to_23')

node_counter = 0

MAX_TIME_DURATION = 1500

CONS = np.empty([3, 3], dtype=object)

B = None

K = None

D_R = None
D_E = None

# DRI -> 5 , DRI & Lim -> 2
T_MIN_Charge = [4, 1, 1]

MAX_CHARGE_TIME_DRI = 25
MAX_CHARGE_TIME_LIM_DOL = 7

actions = []

storage = [[[] for j in range(3)] for i in range(3)]

s_floor = [[[] for j in range(3)] for i in range(3)]

W = [[[] for j in range(3)] for i in range(3)]

disables_raw = []
disables = []

ch_psb_charge_time = [8, 4, 4]
ch_psb_delay = [11, 9, 9]

W_in_time = None

starting_action = None
starting_time = 11
last_time_b_before = 0

charge_instantly_choice = True

past_action = None

name_counter = 0
depth_counter = 0

MAX_TIME_SEARCH_NODE = 1000
Time_Prediction = 300

action_history = []
action_output = []

max_time_go_forward = -1
max_time_B = None
max_time_W_in_time = None
max_time_action_output = None

end_out_w = None

start_time = time.time()
start_time_helper = start_time

base_level_check = 2
level_check = 2

STATUS = 400

MAX_TIME_EXIT = 10

cons_integral = None

B_first_11 = None

disables_raw = None

charge_instantly_choice = None

node = None

# output variables
opt_actions_output = None
opt_w_in_time = None
opt_B = None
opt_shooting_list = None
no_action_spend_time = []


# - - - - - - - - - - - - - - -


def B_first_11_converter(matrix_input):
    return pd.DataFrame({'time': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                         '1': [row[0] for row in matrix_input],
                         '2': [row[1] for row in matrix_input],
                         '3': [row[2] for row in matrix_input],
                         '4': [row[3] for row in matrix_input],
                         '5': [row[4] for row in matrix_input],
                         '6': [row[5] for row in matrix_input],
                         '7': [row[6] for row in matrix_input],
                         '8': [row[7] for row in matrix_input],
                         '9': [row[8] for row in matrix_input],
                         '10': [row[9] for row in matrix_input],
                         '11': [row[10] for row in matrix_input],
                         '12': [row[11] for row in matrix_input]})


def fill_11_first_W_in_time():
    for i in range(11):
        W_in_time[i] = copy.deepcopy(W)


def reset_info():
    global node_counter, MAX_TIME_DURATION, CONS, B, K, D_R, D_E, T_MIN_Charge, MAX_CHARGE_TIME_DRI, MAX_CHARGE_TIME_LIM_DOL, actions, storage, s_floor, W
    global disables, disables_raw, ch_psb_delay, ch_psb_charge_time, W_in_time, starting_action, starting_time, last_time_b_before, charge_instantly_choice
    global past_action, name_counter, depth_counter, MAX_TIME_SEARCH_NODE, Time_Prediction, action_output, action_history, max_time_go_forward, max_time_B
    global max_time_W_in_time, max_time_action_output, end_out_w, start_time_helper, base_level_check, level_check, STATUS, MAX_TIME_EXIT, cons_integral, B_first_11
    global node, opt_B, opt_shooting_list, opt_w_in_time, opt_actions_output, no_action_spend_time

    node_counter = 0

    MAX_TIME_DURATION = 1500

    CONS = np.empty([3, 3], dtype=object)

    B = None

    K = None

    D_R = None
    D_E = None

    # DRI -> 5 , DRI & Lim -> 2
    T_MIN_Charge = [4, 1, 1]

    MAX_CHARGE_TIME_DRI = 25
    MAX_CHARGE_TIME_LIM_DOL = 7

    actions = []

    storage = [[[] for j in range(3)] for i in range(3)]

    s_floor = [[[] for j in range(3)] for i in range(3)]

    W = [[[] for j in range(3)] for i in range(3)]

    disables_raw = []
    disables = []

    ch_psb_charge_time = [8, 4, 4]
    ch_psb_delay = [11, 9, 9]

    W_in_time = None

    starting_action = None
    starting_time = 11
    last_time_b_before = 0

    charge_instantly_choice = True

    past_action = None

    name_counter = 0
    depth_counter = 0

    MAX_TIME_SEARCH_NODE = 1000
    Time_Prediction = 300

    action_history = []
    action_output = []

    max_time_go_forward = -1
    max_time_B = None
    max_time_W_in_time = None
    max_time_action_output = None

    end_out_w = None

    start_time = time.time()
    start_time_helper = start_time

    base_level_check = 2
    level_check = 2

    STATUS = 400

    MAX_TIME_EXIT = 10

    cons_integral = None

    B_first_11 = None

    disables_raw = None

    charge_instantly_choice = None

    node = None

    # output variables
    opt_actions_output = None
    opt_w_in_time = None
    opt_B = None
    opt_shooting_list = None
    no_action_spend_time = []


def main_tread(W_input, s_floor_input, storage_input, K_input, D_R_input, D_E_input, CONS_input, B_first_11_input,
               disables_raw_input, charge_instantly_choice_input=False):
    global cons_integral, charge_instantly_choice, B, node, max_time_go_forward, W_in_time, action_output, start_time_helper, level_check, max_time_B, max_time_W_in_time, max_time_action_output, STATUS
    global W, s_floor, storage, K, D_R, D_E, CONS, B_first_11, disables_raw

    reset_info()

    probable_risk_bin = None

    W = copy.deepcopy(W_input)
    s_floor = copy.deepcopy(s_floor_input)
    storage = copy.deepcopy(storage_input)
    K = copy.deepcopy(K_input)
    D_R = copy.deepcopy(D_R_input)
    D_E = copy.deepcopy(D_E_input)
    CONS = copy.deepcopy(CONS_input)
    B_first_11 = copy.deepcopy(B_first_11_converter(B_first_11_input))
    disables_raw = copy.deepcopy(disables_raw_input)
    charge_instantly_choice = charge_instantly_choice_input

    B = np.zeros([3, 3, 2, MAX_TIME_DURATION + 115])

    W_in_time = [[[[] for j in range(3)] for i in range(3)] for z in range(MAX_TIME_DURATION + 350)]

    fill_11_first_W_in_time()

    cons_integral = clac_cons_integral()

    add_B_first_11()

    add_disables()

    node = Node(None, W, starting_time, starting_action, past_action)

    while node.time <= MAX_TIME_DURATION:

        go_back, next_parent, next_W, next_action, next_time = node.go_next_state()

        if next_time > max_time_go_forward:
            max_time_go_forward = next_time

            max_time_B = copy.deepcopy(B)
            max_time_W_in_time = copy.deepcopy(W_in_time)
            max_time_action_output = copy.deepcopy(action_output)

            probable_risk_bin = node.t_opr[0]

        # if time.time() - start_time > MAX_TIME_EXIT:
        #     break

        # is_full()
        if zero_point():
            STATUS = 200

            print('Spend Time: ', time.time() - start_time)
            save_log()
            break

        if node.time > MAX_TIME_SEARCH_NODE:
            STATUS = 200

            print('Spend Time: ', time.time() - start_time)
            save_log()
            break

        if go_back:
            try:
                action_history.pop()
                action_output.pop()
                node = node.parent
            except:
                pass

            if node.depth == level_check - 1:
                level_check = node.depth

            if base_level_check >= node.depth > level_check:
                level_check += 1

        else:
            action_history.append(next_action)
            action_output.append((next_time, next_action[0], next_action[1], next_action[2], next_action[3]))
            node = Node(next_parent, next_W, next_time, next_action, node.action)

    if STATUS == 400:
        STATUS = 500
        # print('Spend Time: ', time.time() - start_time)

        B = max_time_B
        if len(max_time_W_in_time[0][0][0]) == 2:
            W_in_time = max_time_W_in_time
        action_output = max_time_action_output
        save_log()

    end_time = time.time()

    print('Max Time Reach: ', max_time_go_forward)
    # print('Duration: ', end_time - start_time)
    print('Status: ', STATUS)

    return opt_actions_output, opt_w_in_time, opt_B, opt_shooting_list, STATUS, no_action_spend_time, [
        max_time_go_forward,
        furnace_converter_trix2bin(
            probable_risk_bin)]


# ___________main___________

# if __name__ == '__main__':
#     W_input = [[[] for j in range(3)] for i in range(3)]
#
#     W_input[0][0] = [28.8, 28.0]
#     W_input[0][1] = [28.6, 28.4]
#     W_input[0][2] = [45.6, 25.2]
#
#     W_input[1][0] = [5.32, 2]
#     W_input[1][1] = [5.88, 2]
#     W_input[1][2] = [5.8, 2]
#
#     W_input[2][0] = [5.68]
#     W_input[2][1] = [5.6]
#     W_input[2][2] = [7.68, 2]
#
#     s_floor_input = [[[] for j in range(3)] for i in range(3)]
#     s_floor_input[0][0] = [2, 2]
#     s_floor_input[0][1] = [2, 2]
#     s_floor_input[0][2] = [2, 2]
#
#     s_floor_input[1][0] = [0.2, 0.1]
#     s_floor_input[1][1] = [0.2, 0.1]
#     s_floor_input[1][2] = [0.2, 0.1]
#
#     s_floor_input[2][0] = [0.2]
#     s_floor_input[2][1] = [0.2]
#     s_floor_input[2][2] = [0.2, 0.1]
#
#     storage_input = [[[] for j in range(3)] for i in range(3)]
#     storage_input[0][0] = [60, 60]
#     storage_input[0][1] = [60, 60]
#     storage_input[0][2] = [80, 80]
#
#     storage_input[1][0] = [12, 8]
#     storage_input[1][1] = [12, 8]
#     storage_input[1][2] = [12, 8]
#
#     storage_input[2][0] = [12]
#     storage_input[2][1] = [12]
#     storage_input[2][2] = [12, 6]
#
#     K_input = [3.1, 2.3, 2.4]
#
#     D_R_input = [[8, 7, 9],
#                  [5, 5, 7],
#                  [5, 5, 7]]
#     D_E_input = [[2, 2, 2],
#                  [2, 2, 2],
#                  [2, 2, 2]]
#
#     disables_raw_input = [(10, 9), (4, 12)]
#
#     B_first_11_input = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
#
#     charge_instantly_choice_input = False
#
#     CONS_input = read_cons()
#
#     while True:
#         outputs = main_tread(W_input, s_floor_input, storage_input, K_input, D_R_input, D_E_input, CONS_input,
#                              B_first_11_input, disables_raw_input, charge_instantly_choice_input)
