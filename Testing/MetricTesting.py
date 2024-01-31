import os.path

import cwtvla
import tqdm

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


def validate_t_test():
    """
    Computes t-test and plot the t-statistics and t-max for 1000 traces of fixed and 1000 traces of random
    """
    cw_scope = CWScope(
        "simpleserial-aes_CW308-STM32F3_MASKEDAES_ANSSI.hex",
        25,
        24000,
        0,
        simple_serial_version="1"
    )

    # capture traces
    fixed_t, rand_t = cw_scope.capture_traces_tvla(2500)

    rand = []
    fixed = []
    for trace_r in rand_t:
        rand.append(trace_r.wave)

    for trace_f in fixed_t:
        fixed.append(trace_f.wave)

    # library calculation
    t_stat, t_max = t_test_tvla(rand, fixed)

    plt.plot(t_stat)
    plt.title("T-test using WPI_SCLA_MQP Implementation")
    plt.axhline(y=-4.5, color='r', linestyle='--')
    plt.axhline(y=4.5, color='r', linestyle='--')
    plt.ylabel("T-statistic")
    plt.xlabel("Sample")
    plt.show()


def validate_correlation():
    """
    Computes correlation for a correct key guess
    """
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
    for key_guess in tqdm.tqdm(range(40, 50), desc="Calculation Correlation"):
        predicted_leakage = generate_hypothetical_leakage(1000, texts, key_guess, target_byte, leakage_model_hw)
        correlation = pearson_correlation(predicted_leakage, waves, 1000, 5000)
        plt.legend(title="Key Guess")
        plt.plot(correlation, label=str(hex(key_guess)))

    plt.title("Correlation For Different Key Guesses for Byte 0")
    plt.xlabel("Sample")
    plt.ylabel("Correlation")
    plt.show()


def validate_score_and_rank():
    """
    Scores and ranks keys using correlation. Compares result to the actual key.
    """
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

    # There are 16 partitions each are 1-byte
    partitions = 16
    key_candidates = np.arange(256)

    # score and rank each key guess for each partition
    rankedKeys = score_and_rank(key_candidates, partitions, waves, score_with_correlation, texts, leakage_model_hw)

    # obtain the correct key and key guess based on ranks
    full_guess = np.empty(partitions)
    correct_key = np.empty(partitions)
    for i in range(partitions):
        full_guess[i] = rankedKeys[i][0]
        correct_key[i] = keys[0][i]

    # Check if the ranking function worked
    print("Full Key Guess Based on Ranks : {}".format(full_guess))
    print("Correct Key: {}".format(correct_key))


def validate_success_rate_guessing_entropy():
    """
    Computes the success rate and guessing entropy.
    """
    cw_scope = CWScope(
        "simpleserial-aes-MASKEDAES-ANSSI-CWLITEARM.hex",
        25,
        5000,
        0,
        simple_serial_version="1"
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

    # conduct experiments on a given subkey
    num_experiments = 10
    key_candidates = np.arange(256)
    target_byte = 2
    experiment_ranks = np.empty(num_experiments, dtype=object)

    # run experiments
    for i in tqdm.tqdm(range(num_experiments), desc="Running Experiments"):
        experiment_ranks[i] = score_and_rank_subkey(key_candidates, target_byte, waves, score_with_correlation, texts,
                                                    leakage_model_hw)

    # compute the success rate and guessing entropy
    sr, ge = success_rate_guessing_entropy(keys[0][target_byte], experiment_ranks, 1, num_experiments)

    print("Success Rate For 1000 Traces ", sr)
    print("Guessing Entropy For 1000 Traces ", ge)
