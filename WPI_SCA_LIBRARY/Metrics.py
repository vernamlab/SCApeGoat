import numpy as np
from tqdm import *
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

    for i, trace_set in enumerate(tqdm(label_set, desc="Computing Signal-To-Noise Ratio")):
        # compute statistical mean of every label set
        set_means[i] = np.mean(trace_set, axis=0)
        set_var[i] = np.var(trace_set, axis=0)

    snr = np.divide(np.var(set_means, axis=0), np.mean(set_var, axis=0))

    return snr


def t_test_tvla(fixed_t, random_t):
    """
    Computes the t-statistic and t-max between fixed and random trace sets.
    :param random_t: The random trace set
    :param fixed_t: The fixed trace set
    :return: the t-statistic at each time sample and t-max at each trace
    """
    welsh_t_outer = []
    new_mr_outer = []
    new_mf_outer = []
    new_sf_outer = []
    new_sr_outer = []
    t_max_outer = []

    def t_test_intermediate(mf_old, mr_old, sf_old, sr_old, new_tf, new_tr, n):
        """
        Inner function to help with t-test implementation. Not intended to be called outside this scope.
        """
        if n == 0:
            new_mf = new_tf
            new_mr = new_tr
            new_sf = new_tf - new_mf
            new_sr = new_tr - new_mr
            welsh_t = new_sf

            return welsh_t, new_mr, new_mf, new_sf, new_sr

        elif n > 0:

            new_mf = mf_old + (new_tf - mf_old) / (n + 1)
            new_mr = mr_old + (new_tr - mr_old) / (n + 1)

            new_sf = sf_old + (new_tf - mf_old) * (new_tf - new_mf)
            new_sr = sr_old + (new_tr - mr_old) * (new_tr - new_mr)

            new_stdf = np.sqrt(np.array(new_sf / n))
            new_stdr = np.sqrt(np.array(new_sr / n))

            with np.errstate(divide='ignore', invalid='ignore'):
                welsh_t = np.array(new_mr - new_mf) / np.sqrt(
                    np.array((new_stdr ** 2)) / (n + 1) + np.array((new_stdf ** 2)) / (n + 1))

            return welsh_t, new_mr, new_mf, new_sf, new_sr

    for i in tqdm(range(len(random_t)), desc="Calculating T-Test"):
        welsh_t_outer, new_mr_outer, new_mf_outer, new_sf_outer, new_sr_outer = (
            t_test_intermediate(new_mf_outer, new_mr_outer, new_sf_outer, new_sr_outer, fixed_t[i], random_t[i], i))

        if i > 5:  # remove edge effects
            t_max_outer.append(max(abs(welsh_t_outer)))

    return welsh_t_outer, t_max_outer


def pearson_correlation(predicted_leakage, observed_leakage, num_traces, num_samples):
    """
    Computes the correlation between observed power traces and predicted power leakage computed using a
    key guess. The correlation when the predicted power leakage is modeled using the correct key guess has
    a relatively high magnitude.

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


def generate_hypothetical_leakage(num_traces, plaintext_byte, subkey_guess, leakage_model=leakage_model_hw):
    """
    Generates hypothetical leakage based on a provided leakage model. Useful when conducting pearson correlation metric.
    :param num_traces: The number of traces collected when measuring the observed leakage
    :param plaintext_byte: The array of plaintexts used to collect the observed leakage
    :param subkey_guess: the subkey guess
    :param leakage_model: the leakage model that will be used, defaults to the pre-defined hamming weight leakage model
    :return: numpy array of the hypothetical leakage
    """
    predicted = np.empty(num_traces, dtype=object)

    for i in range(num_traces):
        predicted[i] = leakage_model(subkey_guess, plaintext_byte[i])

    return predicted


def score_and_rank(key_candidates, partitions, traces, score_fcn, *args):
    """
    Scores and ranks possible key guesses based on how likely a subkey is to be the actual key
    :param key_candidates: All key possibilities per key partition. For 1-byte partitions it should be np.arrange(256)
    :param partitions: The number of partitions. For AES-128 there are 16 1-byte partitions.
    :param traces: A set of collected traces.
    :param score_fcn: The function used to score each key guess. NOTE: MUST BE IN THE FORM score_fcn(traces, key_guess, target_byte, ...)
    :param args: Additional arguments required for the score_fcn
    :return: Subkey ranks for each partition of the full key.
    """
    dtype = [('key', int), ('score', 'float64')]
    ranks = []
    # for each key partition
    for i in tqdm(range(partitions), desc='Scoring {} Partitions'.format(partitions)):
        partition_scores = np.array([], dtype=dtype)

        # for each key guess in the partition score the value and add to list
        for k in key_candidates:
            score_k = score_fcn(traces, k, i, *args)
            key_score = np.array([(k, score_k)], dtype=dtype)
            partition_scores = np.append(partition_scores, key_score)

        # rank each key where partition_ranks[0] is the key that scored the highest
        partition_ranks = np.array([key_score[0] for key_score in np.sort(partition_scores, order='score')[::-1]])

        ranks.append(partition_ranks)
    return ranks


def score_and_rank_subkey(key_candidates, target_byte, traces, score_fcn, *args):
    dtype = [('key', int), ('score', 'float64')]
    key_scores = np.array([], dtype=dtype)

    # for each key guess in the partition score the value and add to list
    for k in tqdm(key_candidates):
        score_k = score_fcn(traces, k, target_byte, *args)
        key_score = np.array([(k, score_k)], dtype=dtype)
        key_scores = np.append(key_scores, key_score)

    # rank each key where partition_ranks[0] is the key that scored the highest
    key_ranks = np.array([key_score[0] for key_score in np.sort(key_scores, order='score')[::-1]])

    return key_ranks


def score_with_correlation(traces, key_guess, target_byte, plaintexts, leakage_model):
    """
    Scoring function that assigns a key guess a score based on the max value of the pearson correlation.
    :param traces: The collected traces
    :param key_guess: The key guess
    :param target_byte: The target byte of the key
    :param plaintexts: The plaintexts used during trace capture
    :param leakage_model: The leakage model function
    :return: The score of the key guess
    """

    # generate the predicted leakage
    predicted_leakage = generate_hypothetical_leakage(len(traces), plaintexts, key_guess, leakage_model)

    # calculate correlation based on the key guess
    correlation = pearson_correlation(predicted_leakage, traces, len(traces), len(traces[0]))

    # the score will be the max correlation present in the trace
    return np.max(np.abs(correlation))


def success_rate_guessing_entropy(correct_key, experiment_ranks, order, num_experiments):
    """
    Computes the success rate and guessing entropy based on computed key ranks
    :param correct_key: the correct key of the cryptographic system, typically a key partition in practice
    :param experiment_ranks: The ranks of a given key guess for all experiments conducted
    :param order: If a key is within the number specified by the order ranks, then it will count towards the success rate
    :param num_experiments: The number of experiments conducted
    :return: The values of success_rate and guessing_entropy for the given number of experiments
    """
    success_rate = 0
    guessing_entropy = 0

    # for each experiment
    for i in range(num_experiments):

        # check if correct key is within 'order' number of ranks
        for j in range(order):
            if experiment_ranks[i][j] == correct_key:
                success_rate += 1
                break

        # guessing entropy is the log2 of the rank of the correct key
        guessing_entropy += math.log2(np.where(experiment_ranks[i] == correct_key)[0][0] + 1)

    success_rate = success_rate / num_experiments
    guessing_entropy = guessing_entropy / num_experiments

    return success_rate, guessing_entropy


# AES 128 Sbox LUT
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
