import os.path

import h5py
from WPI_SCA_LIBRARY.Metrics import sbox_lut, signal_to_noise_ratio
import numpy as np
import matplotlib.pyplot as plt


def snr_ascad_verification():
    with h5py.File(os.path.dirname(__file__) + "\\ATMega8515_raw_traces.h5", "r") as file:

        # load in datasets
        meta_data = file["metadata"]
        traces = file["traces"]

        # meta data indices
        plaintext_idx = 3
        key_idx = 2
        mask_idx = 0

        # compute labels
        labels = []

        # generate intermediate values from sbox lut
        for i in range(len(traces)):
            labels.append(sbox_lut(meta_data[i][key_idx][3] ^ meta_data[i][plaintext_idx][3]) ^ meta_data[i][mask_idx][15])

        # find unique labels
        labelsUnique = np.unique(labels)

        # initialize the dictionary
        sortedLabels = {}
        for i in labelsUnique:
            sortedLabels[i] = []

        # add traces to labels
        for index, label in enumerate(labels):
            sortedLabels[label].append(traces[index][45400:46100])

        snr = signal_to_noise_ratio(sortedLabels)

        plt.plot(snr)
        plt.show()

snr_ascad_verification()
