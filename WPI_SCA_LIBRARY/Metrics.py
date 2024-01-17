import numpy as np
from scipy import stats
import math


# Signal to Noise Ratio metric
#   - labels: An array of arrays. Each index of the labels array (i.e. labels[0])
#     is a label group containing the corresponding power traces.
# return: the SNR signal
def signal_to_noise_ratio(labels):
    # statistical mean and variances of each set
    set_means = []
    signal_traces = []
    l_n = []

    for trace_set in labels.values():
        set_means.append(np.mean(trace_set, axis=0))  # take the mean along the column
        for trace in trace_set:
            l_n.append(trace - set_means[-1])
        signal_traces.append(set_means[-1])

    l_n = np.var(l_n, axis=0)
    l_d = np.var(signal_traces, axis=0)

    snr = np.divide(l_d, l_n)

    return snr


# Score metric: Ranks each key guess in a key partition based on a scoring function
#   - traces: The trace set to be evaluated
#   - score_fcn: Function callback that takes two arguments, traces and a guess candidate
#                and returns a "score" such that the higher the value, the more likely the
#                key candidate is the actual key
#   - partitions: The number of partitions of the key full key.
# return: A 2D array rank. The value rank[i] are the key guess rankings for partition i.
#         The value of rank[i][0] is the highest ranked key guess for partition i.
def score_and_rank(traces, score_fcn, key_candidates, partitions):
    dtype = [('key', int), ('score', 'float64')]
    ranks = []
    # for each key partition
    for i in range(partitions):
        partition_scores = np.array([], dtype=dtype)

        # for each key guess in the partition score the value and add to list
        for k in key_candidates:
            score_k = score_fcn(traces, k)
            key_score = np.array([(k, score_k)], dtype=dtype)
            partition_scores = np.append(partition_scores, key_score)

        # rank each key where partition_ranks[0] is the key that scored the highest
        partition_ranks = np.array([key_score[0] for key_score in np.sort(partition_scores, order='score')[::-1]])

        ranks.append(partition_ranks)
    return ranks


# Success Rate and Guessing Entropy Metric
#   - correct_key: the correct key of the cryptographic system, typically a key partition in practice
#   - ranks: The ranks of key guesses for a given experiment
#   - num_experiments: The number of experiments conducted
# return: The values of success_rate and guessing_entropy for the given number of experiments
def success_rate_guessing_entropy(correct_key, ranks, order, num_experiments):
    success_rate = 0
    guessing_entropy = 0

    # for each experiment
    for i in range(num_experiments):

        # check if correct key is within o ranks
        for j in range(order):
            if ranks[i][j] == correct_key:
                success_rate += 1
                break

        # guessing entropy is the log2 of the rank of the correct key
        guessing_entropy += math.log2(ranks[i].index(correct_key) + 1)

    success_rate = success_rate / num_experiments
    guessing_entropy = guessing_entropy / num_experiments

    return success_rate, guessing_entropy


# Pearson's Correlation Coefficient Metric
#   - predicted_leakage: predicted traces associated with intermediate values and a key guess and a plaintext value
#   - observed_leakage: actual power traces observed with a given plaintext
# returns: the correlation coefficient and p-value between each trace
def pearson_correlation(predicted_leakage, observed_leakage, num_traces, num_samples):
    predicted_mean = np.mean(predicted_leakage, axis=0)
    observed_mean = np.mean(observed_leakage, axis=0)

    numerator = np.zeros(num_samples)
    denominator1 = np.zeros(num_samples)
    denominator2 = np.zeros(num_samples)

    for d in range(num_traces):
        l = observed_leakage[d] - observed_mean
        g = predicted_leakage[d] - predicted_mean

        numerator = numerator + g * l
        denominator1 = denominator1 + np.square(l)
        denominator2 = denominator2 + np.square(g)

    correlation_trace = numerator / np.sqrt(denominator1 * denominator2)

    return correlation_trace


# T-test with TVlA metric:  In general |t| > th where th = 4.5 means that the system leaks information about the
# cryptographic key. - fixed:  Trace set recorded with a fixed plaintext - random: Trace set recorded with a random
# set of plaintexts return: an array of t-statistics
# TODO: Unsure if this works will probably need to fix this
def t_test_tvla(fixed, random, num_traces):
    # calculate t-statistic for each trace
    t_stats = []
    for t in range(num_traces):
        t_statistic, p_value = stats.ttest_ind(fixed[t], random[t], axis=0, equal_var=False)
        t_stats.append(t_statistic)

    # high t-statistic and low p-values indicate that a given time sample leaks information
    return t_stats


# sbox lookup table for metric implemenations
def sbox_lut(index):
    sbox = [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67,
            0x2b, 0xfe, 0xd7, 0xab, 0x76, 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59,
            0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 0xb7,
            0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1,
            0x71, 0xd8, 0x31, 0x15, 0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05,
            0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75, 0x09, 0x83,
            0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29,
            0xe3, 0x2f, 0x84, 0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b,
            0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, 0xd0, 0xef, 0xaa,
            0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c,
            0x9f, 0xa8, 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc,
            0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 0xcd, 0x0c, 0x13, 0xec,
            0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19,
            0x73, 0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee,
            0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb, 0xe0, 0x32, 0x3a, 0x0a, 0x49,
            0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
            0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4,
            0xea, 0x65, 0x7a, 0xae, 0x08, 0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6,
            0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, 0x70,
            0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9,
            0x86, 0xc1, 0x1d, 0x9e, 0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e,
            0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf, 0x8c, 0xa1,
            0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0,
            0x54, 0xbb, 0x16]
    return sbox[index]
