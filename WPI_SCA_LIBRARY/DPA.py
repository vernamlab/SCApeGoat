import numpy as np


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


def calculate_dpa(traces, iv, order=1, key_guess=0, window_size_fma=5, window_size_dpa=20, num_of_traces=0):
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
        traces = traces[:, 0:4000]
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
