import numpy as np
from scipy.stats import ttest_ind
import math


def signal_to_noise_ratio(labels):
    """
    Computes the signal-to-noise ratio of a set of traces associated with intermediate labels. Spikes in
    magnitude of the resulting SNR trance indicate possible cryptographic information leakage.

    :param labels: SNR label set where label[L] are power traces associated with label L
    :type labels: dict
    :return: The SNR trace of the supplied trace set
    """

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


def pearson_correlation(predicted_leakage, observed_leakage, num_traces, num_samples):
    """
    Compares two trace sets corresponding to predicted and observed leakage. High magnitudes indicate
    that an intermediate value may be leaked at that time sample.

    :param predicted_leakage: predicted traces associated with intermediate values and a key guess and plaintext value
    :param observed_leakage: predicted traces associated with intermediate values and a key guess and plaintext value
    :param num_traces: number of traces in each trace set
    :param num_samples: the number of samples per trace
    :return: The correlation trace corresponding to the predicted leakage
    """
    predicted_mean = np.mean(predicted_leakage, axis=0)
    observed_mean = np.mean(observed_leakage, axis=0)

    numerator = np.zeros(num_samples)
    denominator1 = np.zeros(num_samples)
    denominator2 = np.zeros(num_samples)

    for d in range(num_traces):
        L = observed_leakage[d] - observed_mean
        g = predicted_leakage[d] - predicted_mean

        numerator = numerator + g * L
        denominator1 = denominator1 + np.square(L)
        denominator2 = denominator2 + np.square(g)

    correlation_trace = numerator / np.sqrt(denominator1 * denominator2)

    return correlation_trace


def t_test(fixed_t, random_t, num_samples, step=2000, order_2=False):
    """
    Computes the t-statistic between fixed and random trace sets
    :param fixed_t:
    :param random_t:
    :param num_samples:
    :param step:
    :param order_2:
    :return:
    """
    # initialize t-test results
    tf = np.zeros(num_samples)
    tf_2 = np.zeros(num_samples)

    for i in range(0, num_samples, step):
        stt = i
        end = i + step
        if end > num_samples:
            end = num_samples

        # get traces for a no. of samples
        r = []
        for j, trace_r in enumerate(random_t):
            r.append(trace_r[stt:end])

        f = []
        for k, trace_f in enumerate(fixed_t):
            f.append(trace_f[stt:end])

        # calculate t-test
        t = ttest_ind(f, r, axis=0, equal_var=False)[0]

        # append the output
        tf[stt:end] = t

        if order_2:
            # convert to numpy and preprocess them
            r = np.array(r)
            f = np.array(f)
            r_2 = (r - r.mean(axis=0)) ** 2
            f_2 = (f - f.mean(axis=0)) ** 2
            t_2 = ttest_ind(f_2, r_2, axis=0, equal_var=False)[0]
            tf_2[stt:end] = t_2

    return tf, tf_2


def score_and_rank(traces, score_fcn, key_candidates, partitions):
    """
    Ranks each key guess in a key partition based on a scoring function
    :param traces: The trace set to be evaluated
    :param score_fcn: Scoring function callback
    :param key_candidates: the sub-keys to be ranked
    :param partitions: the number of partitions of the full key
    :return: the key partitions ordered by rank from highest to lowest
    """
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


def success_rate_guessing_entropy(correct_key, ranks, order, num_experiments):
    """
    Computes the success rate and guessing entropy based on computed key ranks
    :param correct_key: the correct key of the cryptographic system, typically a key partition in practice
    :param ranks: The ranks of key guesses for a given experiment
    :param order:
    :param num_experiments: The number of experiments conducted
    :return: The values of success_rate and guessing_entropy for the given number of experiments
    """
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
