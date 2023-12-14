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
    set_variances = []

    for label in labels:
        set_means.append(np.mean(label, axis=0))  # take the mean along the column
        set_variances.append(np.var(label, axis=0))  # take the variance along the column

    # calculate overall mean and variance
    overall_mean = np.mean(set_means, axis=0)
    overall_variance = np.var(set_variances, axis=0)

    # perform SNR calculation
    l_d = np.zeros(len(set_means[0]))
    for mean in set_means:
        l_d = np.add(l_d, np.square(np.subtract(mean, overall_mean)))
    l_n = overall_variance

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
def t_test_tvla(fixed, random, num_traces):
    # calculate t-statistic for each trace
    t_stats = []
    for t in range(num_traces):
        t_statistic, p_value = stats.ttest_ind(fixed[t], random[t], axis=0, equal_var=False)
        t_stats.append(t_statistic)

    # high t-statistic and low p-values indicate that a given time sample leaks information
    return t_stats
