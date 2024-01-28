import os.path
from WPI_SCA_LIBRARY.Metrics import *
from WPI_SCA_LIBRARY.CWScope import *
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


def validate_t_test():
    cw_scope = CWScope(
        "simpleserial-aes-CWLITEARM-SS_2_1.hex",
        25,
        5000,
        0,
        simple_serial_version="2"
    )

    # capture traces
    fixed_t, rand_t = cw_scope.capture_traces_tvla(1000)

    rand = []
    fixed = []
    for trace_r in rand_t:
        rand.append(trace_r.wave)

    for trace_f in fixed_t:
        fixed.append(trace_f.wave)

    # library calculation
    t, t2 = t_test(fixed[:], rand[:], cw_scope.scope.adc.samples, step=2000, order_2=True)

    # plot the results
    plt.plot(t)
    plt.title("Value of tf for 10,000 traces")
    plt.ylabel("T-statistic")
    plt.xlabel("Sample")
    plt.show()

    plt.plot(t2)
    plt.title("Value of tf_2 for 10,000 traces")
    plt.ylabel("T-statistic")
    plt.xlabel("Sample")
    plt.show()


def validate_correlation():
    cw_scope = CWScope(
        "simpleserial-aes-CWLITEARM-SS_2_1.hex",
        25,
        5000,
        0,
        simple_serial_version="2"
    )

    # capture trace set
    traces = cw_scope.standard_capture_traces(1000, fixed_key=True, fixed_pt=False)

    # TODO: This can be removed once I change the standard capture procedure
    keys = []
    texts = []
    waves = []
    for trace in traces:
        keys.append(trace.key)
        texts.append(trace.textin)
        waves.append(trace.wave)

    # we will target the correct key for the sake of demonstration
    target_byte = 0
    key_guess = keys[0][target_byte]
    print("Key: ", key_guess)

    # compute predicted leakage using the hamming weight leakage model
    predicted_leakage = generate_hypothetical_leakage(1000, texts, key_guess, target_byte, leakage_model_hw)

    # calculate correlation and plot, there should be a large spike since we are guessing the correct key
    correlation = pearson_correlation(predicted_leakage, waves, 1000, 5000)
    plt.plot(correlation)
    plt.title("Correlation Coefficient For Correct Key Guess {}".format(hex(key_guess)))
    plt.ylabel("Correlation")
    plt.xlabel("Sample")
    plt.show()
