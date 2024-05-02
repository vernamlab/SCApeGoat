#The second order DPA code is inspired by https://github.com/ermin-sakic/second-order-dpa by Ermin Sakic
import numpy as np
import math


def intermediate_value(out):
    a_ma = (out[14] << 8) + (out[15])  # out0
    b_ma = (out[12] << 8) + (out[13])  # out1
    return bin(a_ma ^ b_ma).count("1")


def std_dev(x, x_bar):
    return np.sqrt(np.sum((x - x_bar) ** 2, axis=0))


def cov(x, x_bar, y, y_bar):
    return np.sum((x - x_bar) * (y - y_bar), axis=0)


def calculate_window_averages(traces, window_size=5, traces_max=0):
    fma = []
    i = 0
    if traces_max == 0:
        traces_max = traces.shape[0] - window_size

    while i < traces_max:
        window_average_increment = np.mean(traces[i:i + window_size], axis=0)
        fma.append(window_average_increment)
        i += 1
    return fma


def calculate_dpa(traces, iv, order=1, key_guess=0, window_size_fma=5, num_of_traces=0):
    if order == 1:
        max_cpa = [0] * 1

        num_trace = len(traces)

        t_bar = np.mean(traces, axis=0)
        o_t = std_dev(traces, t_bar)

        hws = np.array([[intermediate_value(textout) for textout in iv[0:num_trace]]]).transpose()
        hws_bar = np.mean(hws, axis=0)

        o_hws = std_dev(hws, hws_bar)
        correlation = cov(traces, t_bar, hws, hws_bar)
        cpa_output = correlation / (o_t * o_hws)

        max_cpa[key_guess] = max(abs(cpa_output))

        guess = np.argmax(max_cpa)
        guess_corr = max(max_cpa)

        return cpa_output, guess_corr, guess

    if order == 2:
        if num_of_traces != 0:
            fma = calculate_window_averages(traces, window_size=window_size_fma)
            traces = np.array(fma[0:num_of_traces])
        else:
            fma = calculate_window_averages(traces, window_size=window_size_fma)
            traces = np.array(fma)
            num_of_traces = traces.shape[0]

        length_vector = traces.shape[1]
        P = np.zeros((num_of_traces, int((length_vector - 1) * length_vector / 2)))

        e = 0
        s = 0
        for i in range(length_vector):
            e = s + length_vector - i - 1
            P[:, s:e] = np.abs(np.subtract(traces[:, i + 1:], traces[:, i].reshape(-1, 1)))
            s = e

        dpa_trace = P
        max_cpa = [0] * 1
        num_trace = len(dpa_trace)
        t_bar = np.mean(dpa_trace, axis=0)
        o_t = std_dev(dpa_trace, t_bar)
        k_guess = 0

        hws = np.array([[intermediate_value(textout) for textout in iv[0:num_trace]]]).transpose()
        hws_bar = np.mean(hws, axis=0)
        o_hws = std_dev(hws, hws_bar)
        correlation = cov(dpa_trace, t_bar, hws, hws_bar)
        cpa_output = correlation / (o_t * o_hws)
        max_cpa[k_guess] = max(abs(cpa_output))
        guess = np.argmax(max_cpa)
        guess_corr = max(max_cpa)

        return cpa_output, guess_corr, guess


def calculate_second_order_dpa_mem_efficient(traces, IV, window_width):
    num_of_samples = traces.shape[1]
    num_of_traces = traces.shape[0]
    P_normal_width = int((num_of_samples - 1) * num_of_samples / 2)

    num_of_iterations = math.floor(P_normal_width / num_of_samples)

    #predefine
    cpaoutput = np.zeros(P_normal_width)
    P = np.zeros((num_of_traces, window_width))

    current_P_index = 0
    current_partition_index = 0
    for i in range(num_of_iterations):
        current_num_in_P = 0

        while current_num_in_P < window_width:
            if current_partition_index == 0:
                sub_array = np.abs(
                    np.subtract(traces[:, current_P_index + 1:], traces[:, current_P_index].reshape(-1, 1)))
                length_sub_array = sub_array.shape[1]

                if length_sub_array + current_num_in_P <= window_width:
                    P[:, current_num_in_P: current_num_in_P + length_sub_array] = sub_array
                    current_num_in_P = current_num_in_P + length_sub_array
                    current_P_index = current_P_index + 1
                else:
                    number_to_add = window_width - current_num_in_P
                    P[:, current_num_in_P: window_width] = sub_array[:, 0:number_to_add]
                    current_num_in_P = window_width
                    current_partition_index = number_to_add
            else:
                sub_array = np.abs(
                    np.subtract(traces[:, current_P_index + 1:], traces[:, current_P_index].reshape(-1, 1)))
                length_sub_array = sub_array.shape[1]
                num_left_to_add = length_sub_array - current_partition_index

                if num_left_to_add <= window_width:
                    P[:, current_num_in_P: num_left_to_add] = sub_array[:, current_partition_index:]
                    current_num_in_P = current_num_in_P + num_left_to_add
                    current_P_index = current_P_index + 1
                    current_partition_index = 0

                else:
                    P[:] = sub_array[:, current_partition_index:current_partition_index + window_width]
                    current_num_in_P = window_width
                    current_partition_index = current_partition_index + window_width

        #solve for cpa output
        dpa_trace = P

        t_bar = np.mean(dpa_trace)
        o_t = std_dev(dpa_trace, t_bar)
        hws = np.array([[intermediate_value(textout) for textout in IV[0:num_of_traces]]]).transpose()
        hws_bar = np.mean(hws)
        # hws_bar = mean(out[:,5])
        o_hws = std_dev(hws, hws_bar)
        correlation = cov(dpa_trace, t_bar, hws, hws_bar)
        cpaoutput[i * window_width: (i * window_width) + window_width] = correlation / (o_t * o_hws)

    #final run through
    start_index = window_width * num_of_iterations
    num_to_add = P_normal_width - start_index
    current_num_in_P = 0
    P = np.zeros((num_of_traces, num_to_add))

    if num_to_add > 0:
        while current_num_in_P < num_to_add:

            if current_partition_index == 0:
                sub_array = np.abs(
                    np.subtract(traces[:, current_P_index + 1:], traces[:, current_P_index].reshape(-1, 1)))
                length_sub_array = sub_array.shape[1]

                if length_sub_array + current_num_in_P <= num_to_add:
                    P[:, current_num_in_P: current_num_in_P + length_sub_array] = sub_array
                    current_num_in_P = current_num_in_P + length_sub_array
                    current_P_index = current_P_index + 1
                else:
                    number_to_add = num_to_add - current_num_in_P
                    P[:, current_num_in_P: num_to_add] = sub_array[:, 0:number_to_add]
                    current_num_in_P = num_to_add
                    current_partition_index = number_to_add
            else:
                sub_array = np.abs(
                    np.subtract(traces[:, current_P_index + 1:], traces[:, current_P_index].reshape(-1, 1)))
                length_sub_array = sub_array.shape[1]
                num_left_to_add = length_sub_array - current_partition_index

                if num_left_to_add <= num_to_add:
                    P[:, current_num_in_P: num_left_to_add] = sub_array[:, current_partition_index:]
                    current_num_in_P = current_num_in_P + num_left_to_add
                    current_P_index = current_P_index + 1
                    current_partition_index = 0

                else:
                    P[:] = sub_array[:, current_partition_index:current_partition_index + num_to_add]
                    current_num_in_P = num_to_add
                    current_partition_index = current_partition_index + num_to_add

        dpa_trace = P

        t_bar = np.mean(dpa_trace)
        o_t = std_dev(dpa_trace, t_bar)
        hws = np.array([[intermediate_value(textout) for textout in IV[0:num_of_traces]]]).transpose()
        hws_bar = np.mean(hws)
        # hws_bar = mean(out[:,5])
        o_hws = std_dev(hws, hws_bar)
        correlation = cov(dpa_trace, t_bar, hws, hws_bar)
        cpaoutput[start_index:] = correlation / (o_t * o_hws)

    return cpaoutput
