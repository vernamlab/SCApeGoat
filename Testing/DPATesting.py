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

    final_cpaoutput = []
    if order == 2:
        traces = traces[:,0:4000]
        if num_of_traces != 0:
            fma = calculate_window_averages(traces, window_size = window_size_fma)
            traces = np.array(fma[0:num_of_traces])
        else:
            fma = calculate_window_averages(traces, window_size = window_size_fma)
            traces = np.array(fma)
            num_of_traces = traces.shape[0]

        length_vector = traces.shape[1]
        # length_vector = 33
        P = np.zeros((num_of_traces, int((length_vector - 1) * length_vector / 2)))

        e = 0
        s = 0
        for i in range(length_vector):
            e = s + length_vector - i - 1
            P[:, s:e] = np.abs(np.subtract(traces[:, i + 1:], traces[:, i].reshape(-1, 1)))
            s = e

        dpa_trace = P
        maxcpa = [0] * 1
        # dpa_trace = dpa_project.waves[:]
        num_trace = len(dpa_trace)
        # dpa_trace1 = np.array(IV_project.waves[0:num_trace])
        # dpa_trace = dpa_trace1[:,7000:8000]
        # dpa_trace = P
        # dpa_trace = np.array(dpa_project.waves[0:num_trace])

        # we don't need to redo the mean and std dev calculations
        # for each key guess
        t_bar = mean(dpa_trace)
        o_t = std_dev(dpa_trace, t_bar)
        kguess = 0  # for us the key guess doesn't matter as we are not guessing

        # for kguess in tnrange(0, 256):
        #     hws = np.array([[HW[aes_internal(textin[0],kguess)] for textin in textin_array]]).transpose()

        # hws = np.array([[intermediate_value(textout)for textout in dpa_project.textouts[0:num_trace]]]).transpose()
        hws = np.array([[intermediate_value(textout) for textout in IV[0:num_trace]]]).transpose()
        hws_bar = mean(hws)
        # hws_bar = mean(out[:,5])
        o_hws = std_dev(hws, hws_bar)
        correlation = cov(dpa_trace, t_bar, hws, hws_bar)
        cpaoutput = correlation / (o_t * o_hws)
        # maxcpa[kguess] = max(abs(cpaoutput))
        maxcpa[kguess] = max(abs(cpaoutput))

        # wrong key
        # hws_not = np.array([[intermediate_value_not(textout)for textout in dpa_project.textouts[0:num_trace]]]).transpose()
        # hws_bar_not = mean(hws_not)
        # o_hws_not = std_dev(hws_not, hws_bar_not)
        # correlation_not = cov(dpa_trace, t_bar, hws_not, hws_bar_not)
        # cpaoutput_not = correlation/(o_t*o_hws_not)
        # maxcpa[1] = max(abs(cpaoutput_not))

        guess = np.argmax(maxcpa)
        guess_corr = max(maxcpa)


        return cpaoutput, guess_corr, guess

traces = np.load("TestFile//Experiments//CWCapture1//CWCapture1Traces.npy")
ciphertext = np.load("TestFile//Experiments//CWCapture1//CWCapture1Ciphertexts.npy")
plaintext = np.load("TestFile//Experiments//CWCapture1//CWCapture1Plaintexts.npy")

cpaoutput, guess_corr, guess = calculate_DPA(traces, plaintext, order=2, window_size_dpa=20, num_of_traces=100)
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