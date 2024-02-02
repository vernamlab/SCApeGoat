import os.path

from WPI_SCA_LIBRARY.Metrics import *
from WPI_SCA_LIBRARY.CWScope import *
import numpy as np
import matplotlib.pyplot as plt


def snr_ascad_verification():
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

        start = time.time()
        snr2 = signal_to_noise_ratio(organizedSN2)
        end = time.time()

        organizedSN3 = organize_labels_for_testing(snr3_labels, traces)

        start2 = time.time()
        snr3 = signal_to_noise_ratio(organizedSN3)
        end2 = time.time()

        total_time = ((end - start) + (end2 - start2)) / 2

        print("SNR Execution Time on 10,000 ASCAD Traces: " + str(total_time) + " seconds")

        plt.plot(snr2, label="SNR2")
        plt.plot(snr3, label="SNR3")
        plt.title("Signal to Noise Ratio Over Samples 45400 to 46100")
        plt.ylabel("Amplitude")
        plt.xlabel("Sample")
        plt.xlim(45400, 46100)
        plt.ylim(0, 1)
        plt.legend()
        plt.show()


# PATH = "C:\\Users\\samka\\PycharmProjects\\MQP\\SCLA_API_MQP\\Testing\\ExampleData\\MetriSCA\\masked_sbox1\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_fixed_positive_uint8_t.csv"
#
# with open(PATH) as file:
#     reader = csv.reader(file)
#
#     traces = np.empty(50000, dtype=object)
#
#     for i, row in enumerate(reader):
#         print("{} out of 50,000 traces loaded".format(i + 1))
#         traces[i] = row
#
#     print(traces[0])
#     plt.plot(traces[0])
#     plt.show()
