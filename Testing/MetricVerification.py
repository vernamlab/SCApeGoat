import csv
import os.path

import matplotlib.pyplot as plt

from WPI_SCA_LIBRARY.Metrics import *
from WPI_SCA_LIBRARY.CWScope import *
import numpy as np


def snr_verification():
    """
    Computes SNR with ASCAD Traces
    """

    def organize_labels_for_testing(labels, traces_set):
        # find unique labels
        labelsUnique = np.unique(labels)

        # initialize the dictionary
        sorted_labels = {}
        for i in labelsUnique:
            sorted_labels[i] = []

        # add traces to labels
        for index, label in enumerate(labels):
            sorted_labels[label].append(traces_set[index])  # we only want to look over this interval

        return sorted_labels

    with h5py.File(os.path.dirname(__file__) + "\\ExampleData\\ASCAD\\ATMega8515_raw_traces.h5", "r") as file:
        # obtain data from HDF5 file
        metadata = np.array(file['metadata'][:10000])
        traces = file['traces'][:10000, :]
        keys = metadata['key'][:, 2]
        plaintexts = metadata['plaintext'][:, 2]
        rout = metadata['masks'][:, 15]

        # We will use the SNR2 and SNR3 processing for metric verification
        snr2_labels = Sbox[keys ^ plaintexts] ^ rout
        snr3_labels = rout

        # compute SNR for each
        organizedSN2 = organize_labels_for_testing(snr2_labels, traces)
        snr2 = signal_to_noise_ratio(organizedSN2)

        organizedSN3 = organize_labels_for_testing(snr3_labels, traces)
        snr3 = signal_to_noise_ratio(organizedSN3)

        # plot result
        plt.plot(snr2, label="SNR2")
        plt.plot(snr3, label="SNR3")
        plt.title("Signal to Noise Ratio Over Samples 45400 to 46100 ASCAD Traces")
        plt.ylabel("Amplitude")
        plt.xlabel("Sample")
        plt.xlim(45400, 46100)
        plt.ylim(0, 1)
        plt.grid()
        plt.legend()
        plt.show()


def read_csv_traces(csv_file, num_traces):
    traces = np.empty(num_traces, dtype=object)

    with open(os.path.dirname(__file__) + "\\ExampleData\\MetriSCA\\" + csv_file, "r") as file:
        csv_reader = csv.reader(file)

        for i, row in tqdm.tqdm(enumerate(csv_reader), desc="Reading {} Traces From CSV".format(num_traces)):
            traces[i] = np.array([int(i) for i in row])

        return traces


def read_bin_file_traces(bin_file, num_traces=50000, num_samples=3000):
    with open(os.path.dirname(__file__) + "\\ExampleData\\MetriSCA\\" + bin_file, "rb") as file:

        traces = np.empty(num_traces, dtype=object)

        for i in tqdm.tqdm(range(num_traces), desc="Reading Traces from .bin file"):
            traces[i] = np.array([int(i) for i in file.read(num_samples)])
        return traces


def t_test_verification():
    """
    Verifies T-test with MetriSCA Traces
    """
    # Load in Binary Data
    unmasked_fixed = read_bin_file_traces("unprotected_sbox\\single\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_fixed_positive_uint8_t.bin")
    unmasked_random = read_bin_file_traces("unprotected_sbox\\single\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")
    masked_fixed = read_bin_file_traces("masked_sbox1\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_fixed_positive_uint8_t.bin")
    masked_random = read_bin_file_traces("masked_sbox1\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")
    masked_fixed_2 = read_bin_file_traces("masked_sbox2\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_fixed_positive_uint8_t.bin")
    masked_random_2 = read_bin_file_traces("masked_sbox2\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")

    # compute t-test for each dataset
    t, tmax = t_test_tvla(unmasked_fixed, unmasked_random)
    t1, tmax1 = t_test_tvla(masked_fixed, masked_random)
    t2, tmax2 = t_test_tvla(masked_fixed_2, masked_random_2)

    # plot t-test
    plt.plot(t[1000:1500], label="Unprotected Sbox", color='tab:blue')
    plt.plot(t1[1000:1500], label="Masked Sbox 1", color='tab:green')
    plt.plot(t2[1000:1500], label="Masked Sbox 2", color='tab:orange')

    plt.title("T-test implementation using MetriSCA Example Traces")
    plt.xlabel("Sample")
    plt.ylabel("T-Statistic")
    plt.axhline(y=-4.5, color='0', linestyle='--')
    plt.axhline(y=4.5, color='0', linestyle='--')
    plt.yticks([4.5, 0, -4.5, -10, -20, -30, -40])
    plt.legend()
    plt.grid()
    plt.show()

    # plot t-max
    plt.plot(tmax, label="Unprotected Sbox", color='tab:blue')
    plt.plot(tmax1, label="Masked Sbox 1", color='tab:green')
    plt.plot(tmax2, label="Masked Sbox 2", color='tab:orange')

    plt.title("T-Max as a Function of the Number of Traces")
    plt.xlabel("Number of Traces")
    plt.ylabel("T-Max")
    plt.axhline(y=4.5, color='0', linestyle='--')
    plt.legend()
    plt.grid()
    plt.show()
