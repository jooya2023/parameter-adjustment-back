from celery import shared_task
from time import sleep
from parameter.helper.calculations import main_tread, read_cons


@shared_task
def calculation(W_input, s_floor_input, storage_input, K_input, D_R_input, D_E_input, B_first_11_input,
                disables_raw_input, charge_instantly_choice_input):
    sleep(3)
    CONS_input = read_cons()
    opt_actions_output, opt_w_in_time, opt_B, opt_shooting_list, STATUS, data = main_tread(W_input, s_floor_input,
                                                                                           storage_input, K_input,
                                                                                           D_R_input, D_E_input,
                                                                                           CONS_input,
                                                                                           B_first_11_input,
                                                                                           disables_raw_input,
                                                                                           charge_instantly_choice_input
                                                                                           )
    return opt_actions_output, opt_w_in_time, opt_B, opt_shooting_list, STATUS, data
