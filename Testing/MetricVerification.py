import csv
import os.path
import time

import matplotlib.pyplot as plt
import tqdm
from tqdm import *
from WPI_SCA_LIBRARY.Metrics import *
from WPI_SCA_LIBRARY.CWScope import *
from WPI_SCA_LIBRARY.LeakageModels import *
import numpy as np


def read_csv_traces(csv_file, num_traces):
    traces = np.empty(num_traces, dtype=object)

    with open(os.path.dirname(__file__) + "\\ExampleData\\MetriSCA\\" + csv_file, "r") as file:
        csv_reader = csv.reader(file)

        for i, row in tqdm.tqdm(enumerate(csv_reader), desc="Reading {} Traces From CSV".format(num_traces)):
            traces[i] = np.array([int(i) for i in row])

        return traces


def read_bin_file_keys_or_texts(bin_file, set_type="Random"):
    with open(os.path.dirname(__file__) + "\\ExampleData\\MetriSCA\\" + bin_file, "rb") as file:
        dataset = np.array([int(i) for i in file.read(100000)])
        if set_type == "Random":
            return dataset[0::2]
        elif set_type == "Fixed":
            return dataset[1::2]
        elif set_type == "Multi":
            return dataset
        else:
            raise Exception("Unknown text set: {}".format(set_type))


def read_bin_file_traces(bin_file, num_traces=50000, num_samples=3000):
    with open(os.path.dirname(__file__) + "\\ExampleData\\MetriSCA\\" + bin_file, "rb") as file:
        traces = np.empty((num_traces, num_samples), dtype=object)

        for i in tqdm.tqdm(range(num_traces), desc="Reading Traces from .bin file"):
            traces[i] = np.array([int(i) for i in file.read(num_samples)])
        return traces


def read_parallel_from_bin_file(bin_file, num_traces):
    with open(os.path.dirname(__file__) + "\\ExampleData\\MetriSCA\\" + bin_file, "rb") as file:
        dataset = np.array([int(i) for i in file.read(num_traces * 16)]).reshape(num_traces, 16)

        return dataset


def snr_verification():
    """
    Computes SNR with ASCAD Traces. Reference Figure 3 in https://eprint.iacr.org/2018/053.pdf
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
            sorted_labels[label].append(np.array(traces_set[index]))  # we only want to look over this interval

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

        print(end - start)

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


def t_test_verification():
    """
    Verifies T-test with MetriSCA Traces. Reference Figure 8(a) and Figure 8(b) in https://eprint.iacr.org/2022/253.pdf
    """
    # Load in Binary Data
    unmasked_fixed = read_bin_file_traces(
        "unprotected_sbox\\single\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_fixed_positive_uint8_t.bin")
    unmasked_random = read_bin_file_traces(
        "unprotected_sbox\\single\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")
    # masked_fixed = read_bin_file_traces(
    #     "masked_sbox1\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_fixed_positive_uint8_t.bin")
    # masked_random = read_bin_file_traces(
    #     "masked_sbox1\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")
    # masked_fixed_2 = read_bin_file_traces(
    #     "masked_sbox2\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_fixed_positive_uint8_t.bin")
    # masked_random_2 = read_bin_file_traces(
    #     "masked_sbox2\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")

    # compute t-test for each dataset
    t, tmax = t_test_tvla(unmasked_fixed, unmasked_random)
    # t1, tmax1 = t_test_tvla(masked_fixed, masked_random)
    # t2, tmax2 = t_test_tvla(masked_fixed_2, masked_random_2)

    # plot t-test
    plt.plot(t[1000:1500], label="Unprotected Sbox", color='tab:blue')
    # plt.plot(t1[1000:1500], label="Masked Sbox 1", color='tab:green')
    # plt.plot(t2[1000:1500], label="Masked Sbox 2", color='tab:orange')

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
    # plt.plot(tmax1, label="Masked Sbox 1", color='tab:green')
    # plt.plot(tmax2, label="Masked Sbox 2", color='tab:orange')

    plt.title("T-Max as a Function of the Number of Traces")
    plt.xlabel("Number of Traces")
    plt.ylabel("T-Max")
    plt.axhline(y=4.5, color='0', linestyle='--')
    plt.legend()
    plt.grid()
    plt.show()


def correlation_validation():
    """
    Verifies Correlation with MetriSCA traces. Uses hamming distance leakage model. There is no figure to reference
    but the correct key is 203.
    """
    unmasked_random = read_bin_file_traces(
        "unprotected_sbox\\single\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")
    texts = read_bin_file_keys_or_texts("unprotected_sbox\\single\\traces\\oscilloscope_traces\\plaintexts.bin",
                                        "Random")
    num_traces = 50000
    leakage = np.empty(num_traces, dtype=object)

    colors = ['tab:purple', 'tab:green', 'tab:pink', 'tab:red', 'tab:orange', 'tab:blue']
    for j, k in tqdm.tqdm(enumerate(range(200, 206))):
        for i in range(num_traces):
            leakage[i] = bin(Sbox[0] ^ Sbox[k ^ texts[i]]).count('1')

        correlation = pearson_correlation(leakage, unmasked_random)
        plt.plot(correlation, label=k, color=colors[j])

    plt.legend(title="Key Guess")
    plt.title("Correlation For Correct Key 203 MetriSCA Example Traces")
    plt.xlabel("Sample")
    plt.ylabel("Correlation")
    plt.grid()
    plt.show()


def score_and_rank_verification():
    """
    Verify score and rank metric. References Figure 2(a) and Figure 2(b) https://eprint.iacr.org/2022/253.pdf
    """
    unmasked_random = read_bin_file_traces("unprotected_sbox\\single\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")
    texts = [
        [t, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] for t in
        read_bin_file_keys_or_texts("unprotected_sbox\\single\\traces\\oscilloscope_traces\\plaintexts.bin", "Random")
    ]

    key_candidates = range(256)
    trace_nums = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 9000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000]

    key_ranks = np.empty(256, dtype=object)
    key_scores = np.empty(256, dtype=object)
    for i in range(256):
        key_scores[i] = []
        key_ranks[i] = []

    for i in trace_nums:
        ranks = score_and_rank(key_candidates, 0, unmasked_random[:i], score_with_correlation, texts[:i], leakage_model_hamming_distance)

        for k in range(256):
            key_scores[k].append([key_and_score for key_and_score in ranks if key_and_score[0] == k][0][1])
            key_ranks[k].append([idx for idx, key_and_score in enumerate(ranks) if key_and_score[0] == k][0] + 1)

    # plot key scores
    for k in range(256):
        if k != 203:
            plt.plot(trace_nums, key_scores[k], color="#C0C0C0")
    plt.plot(trace_nums, key_scores[203], color="tab:blue", label="203")
    plt.title("Correct Key Score as a Function of the Number of Traces")
    plt.ylabel("Score")
    plt.xlabel("Number of Traces")
    plt.legend(title="Correct Key")
    plt.grid()
    plt.show()

    # plot key ranks
    for k in range(256):
        if k != 203:
            plt.plot(trace_nums, key_ranks[k], color="#C0C0C0")
    plt.plot(trace_nums, key_ranks[203], color="tab:blue", label="203")
    plt.title("Correct Key Rank as a Function of the Number of Traces")
    plt.ylabel("Rank")
    plt.xlabel("Number of Traces")
    plt.legend(title="Correct Key")
    plt.grid()
    plt.show()


def success_rate_verification():
    """
    Verification function for success rate and guessing entropy metric. References to Figure 4 in
    https://eprint.iacr.org/2022/253.pdf
    """

    # Figure 4 Success Rate 16 parallel unprotected Sboxes
    unprotected_parallel = read_bin_file_traces("unprotected_sbox\\multiple\\traces\\oscilloscope_traces\\oscilloscope_traces_100k_535_samples_random_positive_uint8_t.bin", num_traces=100000, num_samples=535)
    texts = read_parallel_from_bin_file("unprotected_sbox\\multiple\\traces\\oscilloscope_traces\\plaintexts_random.bin", 100000)

    key_candidates = range(256)
    num_experiments = 16
    experiment_ranks = np.empty(num_experiments, dtype=object)
    experiment_keys = np.empty(num_experiments)

    success_rates = []
    num_t = []

    for t in range(1000, 100000 + 1000, 4500):
        for i in tqdm.tqdm(range(num_experiments), desc="Running Experiments for {} Traces".format(t)):
            ranks = score_and_rank(key_candidates, i, unprotected_parallel[:t], score_with_correlation, texts[:t], leakage_model_hamming_distance)
            experiment_ranks[i] = ranks
            experiment_keys[i] = 203

        s, e = success_rate_guessing_entropy([203] * 16, experiment_ranks, 1, num_experiments)
        success_rates.append(s)
        num_t.append(t)

    plt.plot(num_t, success_rates)
    plt.title("Success Rate as a Function of the Number of Traces")
    plt.xlabel("Number of Traces")
    plt.ylabel("Success Rate")
    plt.axhline(y=1.0, color='0', linestyle='--')
    plt.grid()
    plt.show()


def guessing_entropy_validation():
    """Validates guessing entropy metric. References Figure 5 in https://eprint.iacr.org/2022/253.pdf"""
    # Load in Binary Data
    unprotected_sbox = read_bin_file_traces("unprotected_sbox\\single\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")
    unprotected_texts = [
        [t, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] for t in
        read_bin_file_keys_or_texts("unprotected_sbox\\single\\traces\\oscilloscope_traces\\plaintexts.bin", "Random")
    ]

    masked_sbox_1 = read_bin_file_traces("masked_sbox1\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")
    masked_texts_1 = [
        [t, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] for t in
        read_bin_file_keys_or_texts("masked_sbox1\\traces\\oscilloscope_traces\\plaintexts.bin", "Random")
    ]

    masked_sbox_2 = read_bin_file_traces("masked_sbox2\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")
    masked_texts_2 = [
        [t, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] for t in
        read_bin_file_keys_or_texts("masked_sbox2\\traces\\oscilloscope_traces\\plaintexts.bin", "Random")
    ]

    key_candidates = range(256)
    num_experiments = 8
    experiment_ranks_unprotected = np.empty(num_experiments, dtype=object)
    experiment_ranks_protected_1 = np.empty(num_experiments, dtype=object)
    experiment_ranks_protected_2 = np.empty(num_experiments, dtype=object)
    experiment_keys = np.empty(num_experiments)

    trace_nums = [1000, 2000, 3000, 4000, 5000, 9000, 12000, 18000, 22000, 30000, 40000, 50000]
    entropy_unprotected = []
    entropy_protected_1 = []
    entropy_protected_2 = []

    for t in trace_nums:
        for i in trange(num_experiments):
            rank_unprotected = score_and_rank(key_candidates, 0, unprotected_sbox[:t], score_with_correlation, unprotected_texts[:t], leakage_model_hamming_distance)
            experiment_ranks_unprotected[i] = rank_unprotected

            rank_protected_1 = score_and_rank(key_candidates, 0, masked_sbox_1[:t], score_with_correlation, masked_texts_1[:t], leakage_model_hamming_distance)
            experiment_ranks_protected_1[i] = rank_protected_1

            rank_protected_2 = score_and_rank(key_candidates, 0, masked_sbox_2[:t], score_with_correlation, masked_texts_2[:t], leakage_model_hamming_distance)
            experiment_ranks_protected_2[i] = rank_protected_2

            experiment_keys[i] = 203

        s_unprotected, e_unprotected = success_rate_guessing_entropy(experiment_keys, experiment_ranks_unprotected, 1, num_experiments)
        s_protected_1, e_protected_1 = success_rate_guessing_entropy(experiment_keys, experiment_ranks_protected_1, 1, num_experiments)
        s_protected_2, e_protected_2 = success_rate_guessing_entropy(experiment_keys, experiment_ranks_protected_2, 1, num_experiments)

        entropy_unprotected.append(e_unprotected)
        entropy_protected_1.append(e_protected_1)
        entropy_protected_2.append(e_protected_2)

        print("T = {} Done".format(t))

    plt.plot(trace_nums, entropy_unprotected, color="tab:blue", label="Unprotected Sbox")
    plt.plot(trace_nums, entropy_protected_1, color="tab:green", label="Masked Sbox 1")
    plt.plot(trace_nums, entropy_protected_2, color="tab:orange", label="Masked Sbox 2")
    plt.title("Guessing Entropy as a Function of The Number of Traces")
    plt.xlabel("Number of Traces")
    plt.ylabel("Guessing Entropy")
    plt.legend()
    plt.grid()
    plt.show()

