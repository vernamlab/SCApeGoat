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

    # define the label set
    label_set = labels.values()
    label_set_size = len(label_set)

    # statistical mean and variances of each set, preallocate memory when possible
    set_means = np.empty(label_set_size, dtype=object)
    set_var = np.empty(label_set_size, dtype=object)

    for i, trace_set in enumerate(label_set):
        # compute statistical mean of every label set
        set_means[i] = np.mean(trace_set, axis=0)
        set_var[i] = np.var(trace_set, axis=0)

    snr = np.divide(np.var(set_means, axis=0), np.mean(set_var, axis=0))

    return snr


def t_test(fixed_t, random_t, num_samples, step=2000, order_2=False):
    """
    author: Dev Mehta
    Computes the t-statistic between fixed and random trace sets
    :param fixed_t: the set of traces collected with a fixed pt
    :param random_t: the set of traces collected with a random pt
    :param num_samples: the number of samples per trace
    :param step: TODO: ask Dev about this
    :param order_2: compute second order
    :return: (tf, tf_2) where tf is the first order t-statistic and tf_2 is the second order t-statistic
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

    # take the mean of each trace set
    observed_mean = np.mean(observed_leakage, axis=0)
    predicted_mean = np.mean(predicted_leakage, axis=0)

    # correlation equation has three sums
    # one in the numerator and two in the denominator
    # they are initialized to zero to start the sum
    top_sum_observed_predicted = np.zeros(num_samples)
    bottom_sum_observed = np.zeros(num_samples)
    bottom_sum_predicted = np.zeros(num_samples)

    # for 0 to the number of traces
    for i in range(num_traces):
        # these terms are referenced in both the numerator and denominator
        observed_minus_mean = np.subtract(observed_leakage[i], observed_mean)
        predicted_minus_mean = np.subtract(predicted_leakage[i], predicted_mean)

        # this computes the sum in the numerator
        top_sum_observed_predicted = (
            np.add(top_sum_observed_predicted, np.multiply(observed_minus_mean, predicted_minus_mean)))

        # this computes the two sums in the denominator, we can work on these in parallel
        bottom_sum_observed = np.add(bottom_sum_observed, np.square(observed_minus_mean))
        bottom_sum_predicted = np.add(bottom_sum_predicted, np.square(predicted_minus_mean))

    # return the correlation trace, the denominator sums are multiplied and square rooted
    return np.divide(top_sum_observed_predicted, np.sqrt(np.multiply(bottom_sum_observed, bottom_sum_predicted)))


def leakage_model_hw(plaintext, key):
    """
    Leakage model that can produce hypothetical power traces useful for correlation metric
    :param plaintext: the plaintext
    :param key: the key used to encrypt the plaintext
    :return: the intermediate output
    """
    return bin(Sbox[plaintext ^ key]).count('1')


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


Sbox = np.array([
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
])
