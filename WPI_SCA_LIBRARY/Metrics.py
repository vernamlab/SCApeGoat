import math
import numpy as np
import tqdm
from tqdm import *


def signal_to_noise_ratio(labels: dict):
    """
    Computes the signal-to-noise ratio of a trace set and associated labels. High magnitudes of the resulting SNR traces
    indicate cryptographic leakage at that sample.

    :param labels: A Python dictionary where the keys are labels and the values are the associated power traces. The value of
                    labels[L] is a list of power traces, list[trace_0, trace_1, ..., trace_N], associated with label L.
                    For example, the label can be the output of the AES Sbox such that L = Sbox[key ^ text].
    :return: The SNR of the provided trace set
    :rtype: np.ndarray
    :raises TypeError: if any value in labels.items() is not a np.ndarray or list type
    :Authors: Samuel Karkache (swkarkache@wpi.edu), Trey Marcantonio (tmmarcantonio@wpi.edu)
    """

    # define the label set
    label_set = labels.values()
    label_set_size = len(label_set)

    # statistical mean and variances of each set, preallocate memory when possible
    set_means = np.empty(label_set_size, dtype=object)
    set_var = np.empty(label_set_size, dtype=object)

    for i, trace_set in enumerate(tqdm(label_set, desc="Computing Signal-To-Noise Ratio")):
        if isinstance(trace_set, np.ndarray) or isinstance(trace_set, list):
            # compute statistical mean of every label set
            set_means[i] = np.mean(trace_set, axis=0)
            set_var[i] = np.var(trace_set, axis=0)
        else:
            raise TypeError("All items of the labels dict must be a list or numpy array")

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


def score_and_rank(key_candidates, target_byte, traces, score_fcn, *args):
    """

    :param key_candidates:
    :param target_byte:
    :param traces:
    :param score_fcn:
    :param args:
    :return:
    """
    dtype = [('key', int), ('score', 'float64')]
    key_scores = np.array([], dtype=dtype)

    # for each key guess in the partition score the value and add to list
    for k in key_candidates:
        score_k = score_fcn(traces, k, target_byte, *args)
        key_score = np.array([(k, score_k)], dtype=dtype)
        key_scores = np.append(key_scores, key_score)

    # rank each key where partition_ranks[0] is the key that scored the highest
    key_ranks = np.sort(key_scores, order='score')[::-1]

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
    predicted_leakage = leakage_model(len(traces), plaintexts, key_guess, target_byte)

    # calculate correlation based on the key guess
    correlation = pearson_correlation(predicted_leakage, traces, len(traces), len(traces[0]))

    # the score will be the max correlation present in the trace
    return np.max(np.abs(correlation))


def success_rate_guessing_entropy(correct_keys, experiment_ranks, order, num_experiments):
    """
    Computes the success rate and guessing entropy based on computed key ranks
    :param correct_keys: an array of the correct keys of the given experiment
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
            if experiment_ranks[i][j][0] == correct_keys[i]:
                success_rate += 1
                break

        # guessing entropy is the log2 of the rank of the correct key
        guessing_entropy += math.log2([idx for idx, key_and_score in enumerate(experiment_ranks[i]) if key_and_score[0] == correct_keys[i]][0] + 1)

    success_rate = success_rate / num_experiments
    guessing_entropy = guessing_entropy / num_experiments

    return success_rate, guessing_entropy
