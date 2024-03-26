import random
import numpy as np
import time
from tqdm import tnrange

def HW(n):
    return bin(n).count("1")


def intermediate_value(out):
    ma0 = bin(out[5]).count("1") + bin(out[4]).count("1")
    ma1 = bin(out[6]).count("1") + bin(out[7]).count("1")

    a_ma = (out[14] << 8) + (out[15])  # out0
    b_ma = (out[12] << 8) + (out[13])  # out1
    return HW(a_ma ^ b_ma)


#     return abs(ma0 + ma1)
def mean(X):
    return np.sum(X, axis=0) / len(X)


def std_dev(X, X_bar):
    return np.sqrt(np.sum((X - X_bar) ** 2, axis=0))


def cov(X, X_bar, Y, Y_bar):
    return np.sum((X - X_bar) * (Y - Y_bar), axis=0)


# generating a wrong key
def intermediate_value_not():
    return random.randint(0, 32)

def calculate_window_averages(traces, window_size = 5, traces_max = 0):
    fma = []
    i = 0
    if traces_max == 0:
        traces_max = traces.shape[0] - window_size

    while i < traces_max:
        window_average_increment = np.mean(traces[i:i+window_size],axis=0)
        fma.append(window_average_increment)
        i += 1
    return fma

def calculate_DPA(traces, IV, order = 1, key_guess = 0, window_size_fma = 5, window_size_dpa = 20, num_of_traces = 0):
    if order == 1:
        maxcpa = [0] * 1

        num_trace = len(traces)

        t_bar = mean(traces)
        o_t = std_dev(traces, t_bar)

        hws = np.array([[intermediate_value(textout) for textout in IV[0:num_trace]]]).transpose()
        hws_bar = mean(hws)

        o_hws = std_dev(hws, hws_bar)
        correlation = cov(traces, t_bar, hws, hws_bar)
        cpaoutput = correlation / (o_t * o_hws)

        maxcpa[key_guess] = max(abs(cpaoutput))

        guess = np.argmax(maxcpa)
        guess_corr = max(maxcpa)

        return cpaoutput, guess_corr, guess


    if order == 2:
        if num_of_traces != 0:
            fma = calculate_window_averages(traces, window_size = window_size_fma)
            traces = np.array(fma[0:num_of_traces])
        else:
            fma = calculate_window_averages(traces, window_size = window_size_fma)
            traces = np.array(fma)
            num_of_traces = traces.shape[0]

        size = 0
        for i in range(0, int(traces[0, :].size / window_size_dpa)):
            max_local_CPA_list = []
            traces_devide = traces[:, i * window_size_dpa:i * window_size_dpa + window_size_dpa]
            length_vector = traces_devide[0, :].size

            P = np.zeros((num_of_traces, int((length_vector - 1) * length_vector / 2)))
            cpaoutput = np.zeros((num_of_traces, int((length_vector - 1) * length_vector / 2)))
            correlation = np.zeros((num_of_traces, int((length_vector - 1) * length_vector / 2)))

            e = 0
            s = 0
            for i in range(length_vector):
                e = s + length_vector - i - 1
                P[:, s:e] = np.abs(np.subtract(traces_devide[:, i + 1:], traces_devide[:, i].reshape(-1, 1)))
                s = e

            maxcpa = [0] * 1
            dpa_trace = P

            # we don't need to redo the mean and std dev calculations
            # for each key guess
            t_bar = mean(dpa_trace)
            o_t = std_dev(dpa_trace, t_bar)
            kguess = 0  # for us the key guess doesn't matter as we are not guessing

            hws = np.array([[intermediate_value(textout) for textout in IV[0:num_of_traces]]]).transpose()
            hws_bar = mean(hws)
            # hws_bar = mean(out[:,5])
            o_hws = std_dev(hws, hws_bar)
            correlation = cov(dpa_trace, t_bar, hws, hws_bar)
            cpaoutput = correlation / (o_t * o_hws)

            maxcpa[kguess] = max(abs(cpaoutput))

            guess = np.argmax(maxcpa)
            guess_corr = max(maxcpa)
            max_local_CPA_list.append(guess_corr)

        return cpaoutput, guess_corr, guess

traces = np.load("TestFile//Experiments//CWCapture1//CWCapture1Traces.npy")
ciphertext = np.load("TestFile//Experiments//CWCapture1//CWCapture1Ciphertexts.npy")

cpaoutput, guess_corr, guess = calculate_DPA(traces, ciphertext, order=2, num_of_traces=100)
print(traces.shape)
print(cpaoutput.shape)

import matplotlib.pyplot as plt

plt.plot(cpaoutput,'black')
up = np.zeros(len(cpaoutput))
up.fill(0.004)
down = np.zeros(len(cpaoutput))
down.fill(-0.004)
plt.plot(up,'r')
plt.plot(down,'r')
plt.show()