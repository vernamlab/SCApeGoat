import os.path

import h5py
from WPI_SCA_LIBRARY.Metrics import Sbox, signal_to_noise_ratio
import numpy as np
import matplotlib.pyplot as plt


def snr_ascad_verification():
    with h5py.File(os.path.dirname(__file__) + "\\ATMega8515_raw_traces.h5", "r") as file:
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
        snr2 = signal_to_noise_ratio(organize_labels_for_testing(snr2_labels, traces))
        snr3 = signal_to_noise_ratio(organize_labels_for_testing(snr3_labels, traces))

        plt.plot(snr2, label="SNR2")
        plt.plot(snr3, label="SNR3")
        plt.title("Signal to Noise Ratio Over Samples 45400 to 46100")
        plt.ylabel("Amplitude")
        plt.xlabel("Sample")
        plt.xlim(45400, 46100)
        plt.ylim(0, 1)
        plt.legend()
        plt.show()


def organize_labels_for_testing(labels, traces):
    # find unique labels
    labelsUnique = np.unique(labels)

    # initialize the dictionary
    sorted_labels = {}
    for i in labelsUnique:
        sorted_labels[i] = []

    # add traces to labels
    for index, label in enumerate(labels):
        sorted_labels[label].append(traces[index])  # we only want to look over this interval

    return sorted_labels


snr_ascad_verification()
