"""
File: Metrics.py
Authors: Samuel Karkache (swkarkache@wpi.edu), Dev Mehta (dmmehta2@wpi.edu), Trey Marcantonio (tmmarcantonio@wpi.edu)
Date: 2024-12-02
Description: Metric API for side-channel analysis experiments. Includes SNR, t-test, correlation, score and rank, and success rate and guessing entropy.
"""

from __future__ import annotations
import math
import numpy as np
import tqdm
import matplotlib.pyplot as plt
from tqdm import *
from collections.abc import *
from numbers import Number


def signal_to_noise_ratio(labels: dict, visualize: bool = False, visualization_path: any = None) -> np.ndarray:
    """
    Computes the signal-to-noise ratio of a trace set and associated labels. High magnitudes of the resulting SNR traces
    indicate cryptographic leakage at that sample.

    :param labels: A Python dictionary where the keys are labels and the values are the associated power traces. The value of
                    labels[L] is a list of power traces, list[trace_0, trace_1, ..., trace_N], associated with label L.
                    For example, the label can be the output of the AES Sbox such that L = Sbox[key ^ text].
    :type labels: dict
    :param visualize: Whether to visualize the result
    :param visualization_path: The path of where to save the visualization result, does not save if set to None
    :return: The SNR of the provided trace set
    :rtype: np.ndarray
    :raises TypeError: if any value in labels.items() is not a np.ndarray or list type
    :Authors: Samuel Karkache (swkarkache@wpi.edu), Trey Marcantonio (tmmarcantonio@wpi.edu)
    """

    label_set = labels.values()
    label_set_size = len(label_set)
    set_means = np.empty(label_set_size, dtype=object)
    set_var = np.empty(label_set_size, dtype=object)

    for i, trace_set in enumerate(tqdm(label_set, desc="Computing Signal-To-Noise Ratio")):
        if isinstance(trace_set, np.ndarray) or isinstance(trace_set, list):
            set_means[i] = np.mean(trace_set, axis=0)
            set_var[i] = np.var(trace_set, axis=0)
        else:
            raise TypeError("All items of the labels dict must be a list or numpy array")

    snr = np.divide(np.var(set_means, axis=0), np.mean(set_var, axis=0))

    if visualize:
        plt.plot(snr)
        plt.title("Signal to Noise Ratio Over Samples 45400 to 46100 ASCAD Traces")
        plt.ylabel("Amplitude")
        plt.xlabel("Sample")
        plt.grid()
        if visualization_path is not None:
            plt.savefig(visualization_path)
        plt.show()

    return snr


def t_test_tvla(fixed_t: np.ndarray | list, random_t: np.ndarray | list) -> (np.ndarray, np.ndarray):
    """
    Computes the t-statistic and t-max between fixed and random trace sets. T-statistic magnitudes above or below
    |th| = 4.5 indicate cryptographic vulnerabilities.

    :param random_t: The random trace set
    :type random_t: np.ndarray | list
    :param fixed_t: The fixed trace set
    :type fixed_t: np.ndarray | list
    :return: The t-statistic at each time sample and t-max at each trace as a tuple of numpy arrays
    :rtype: (np.ndarray, np.ndarray)
    :raises ValueError: if fixed_t and random_t do not have the same length
    :Authors: Dev Mehta (dmmehta2@wpi.edu), Samuel Karkache (swkarkache@wpi.edu)
    """
    welsh_t_outer = []
    new_mr_outer = []
    new_mf_outer = []
    new_sf_outer = []
    new_sr_outer = []
    t_max_outer = []

    if len(fixed_t) != len(random_t):
        raise ValueError("Length of fixed_t and random_t must be equal")

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

            with np.errstate(divide='ignore', invalid='ignore'):  # we get divide by zero warnings for first ~5 traces
                welsh_t = np.array(new_mr - new_mf) / np.sqrt(
                    np.array((new_stdr ** 2)) / (n + 1) + np.array((new_stdf ** 2)) / (n + 1))

            return welsh_t, new_mr, new_mf, new_sf, new_sr

    for i in tqdm(range(len(random_t)), desc="Calculating T-Test"):
        welsh_t_outer, new_mr_outer, new_mf_outer, new_sf_outer, new_sr_outer = (
            t_test_intermediate(new_mf_outer, new_mr_outer, new_sf_outer, new_sr_outer, fixed_t[i], random_t[i], i))

        if i > 5:  # remove edge effects
            t_max_outer.append(max(abs(welsh_t_outer)))

    return welsh_t_outer, t_max_outer


def pearson_correlation(predicted_leakage: np.ndarray | list, observed_leakage: np.ndarray | list) -> np.ndarray:
    """
    Computes the correlation between observed power traces and predicted power leakage corresponding to a
    key guess. The correlation when the predicted power leakage is modeled using the correct key guess has
    a relatively high magnitude.

    :param predicted_leakage: predicted power consumption generated by a leakage model
    :type predicted_leakage: np.ndarray | list
    :param observed_leakage: actual power traces collected from the cryptographic target
    :type observed_leakage: np.ndarray | list
    :return: The correlation trace corresponding to the predicted leakage
    :rtype: np.ndarray
    :raises ValueError: if the predicted power leakage and the observed power leakage do not have the same length
    :Authors: Samuel Karkache (swkarkache@wpi.edu)
    """

    if len(predicted_leakage) != len(observed_leakage):
        raise ValueError("The predicted_leakage and observed_leakage must have the same length")

    num_traces = len(observed_leakage)
    num_samples = len(observed_leakage[0])

    observed_mean = np.mean(observed_leakage, axis=0)
    predicted_mean = np.mean(predicted_leakage, axis=0)
    top_sum_observed_predicted = np.zeros(num_samples)
    bottom_sum_observed = np.zeros(num_samples)
    bottom_sum_predicted = np.zeros(num_samples)

    for i in range(num_traces):
        observed_minus_mean = np.subtract(observed_leakage[i], observed_mean)
        predicted_minus_mean = np.subtract(predicted_leakage[i], predicted_mean)

        top_sum_observed_predicted = (
            np.add(top_sum_observed_predicted, np.multiply(observed_minus_mean, predicted_minus_mean)))

        bottom_sum_observed = np.add(bottom_sum_observed, np.square(observed_minus_mean))
        bottom_sum_predicted = np.add(bottom_sum_predicted, np.square(predicted_minus_mean))

    return np.divide(top_sum_observed_predicted, np.sqrt(np.multiply(bottom_sum_observed, bottom_sum_predicted)))


def score_and_rank(key_candidates: Iterable, target_byte: int, traces: list | np.ndarray, score_fcn: Callable,
                   *args: any) -> np.ndarray:
    """
    Scores and ranks a set of key candidates based on how likely they are to be the actual key.

    :param key_candidates: List of key possible key candidates. For a one-byte subkey it would be [0, 1, ..., 255].
    :type key_candidates: np.ndarray | list
    :param target_byte: The byte of the full key that you are targeting. Ignore and set to 0 if your scoring function does not need it.
    :type target_byte: int
    :param traces: The set of power traces that will be used for scoring
    :type traces: numpy.ndarray | list
    :param score_fcn: Callback to the scoring function used to score each key candidate. The score with correlation scoring
                    function is pre-defined and can be used. NOTE: User defined scoring functions must be in the form
                    score_fcn(traces, key_guess, target_byte, ...) to work with this metric. Your scoring function does not
                    need to use all the required arguments, but they must be present as shown.
    :type score_fcn: Callable
    :param args: Additional arguments for the scoring function supplied in score_fcn. For example, the predefined score with
                    correlation function requires plaintexts and a leakage model callback as additional arguments.
    :type args: Any
    :return: An numpy array of sorted tuples containing the key candidates and corresponding scores. For example, assuming that
                    numpy array `ranks` was returned from the metric, ranks[0][0] is the highest ranked key candidate and
                    ranks[0][1] is the score of the highest ranked key candidate.
    :rtype: numpy.ndarray
    :Authors: Samuel Karkache (swkarkache@wpi.edu)
    """

    dtype = [('key', int), ('score', 'float64')]
    key_scores = np.array([], dtype=dtype)

    for k in key_candidates:
        score_k = score_fcn(traces, k, target_byte, *args)
        key_score = np.array([(k, score_k)], dtype=dtype)
        key_scores = np.append(key_scores, key_score)

    key_ranks = np.sort(key_scores, order='score')[::-1]

    return key_ranks


def score_with_correlation(traces: list | np.ndarray, key_guess: any, target_byte: int, plaintexts: list | np.ndarray,
                           leakage_model: Callable) -> Number:
    """
    Scoring function that assigns a key guess a score based on the max value of the pearson correlation.
    :param traces: The collected power traces
    :type traces: list | np.ndarray
    :param key_guess: The key guess
    :type key_guess: any
    :param target_byte: The target byte of the key
    :type target_byte: int
    :param plaintexts: The plaintexts used during trace capture
    :type plaintexts: list | np.ndarray
    :param leakage_model: The leakage model function. The hamming weight and hamming distance leakage model function are
                        pre-defined in this library.
    :type leakage_model: Callable
    :return: The score of the key guess
    :rtype: Number
    :Authors: Samuel Karkache (swkarkache@wpi.edu)
    """

    # generate the predicted leakage
    predicted_leakage = leakage_model(len(traces), plaintexts, key_guess, target_byte)

    # calculate correlation based on the key guess
    correlation = pearson_correlation(predicted_leakage, traces)

    # the score will be the max correlation present in the trace
    return np.max(np.abs(correlation))


def success_rate_guessing_entropy(correct_keys: list | np.ndarray, experiment_ranks: list | np.ndarray, order: int,
                                  num_experiments: int) -> (Number, Number):
    """
    Computes the success rate and guessing entropy based on computed key ranks.
    :param correct_keys: an array of the correct keys of the given experiment
    :type correct_keys: list | np.ndarray
    :param experiment_ranks: The ranks of a given key guess for all experiments conducted
    :type experiment_ranks: list | np.ndarray
    :param order: If a key is within the number specified by the order ranks, then it will count towards the success rate
    :type order: int
    :param num_experiments: The number of experiments conducted
    :type num_experiments: int
    :return: The values of success_rate and guessing_entropy for the given number of experiments
    :rtype: (Number, Number)
    :Authors: Samuel Karkache (swkarkache@wpi)
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
        guessing_entropy += math.log2(
            [idx for idx, key_and_score in enumerate(experiment_ranks[i]) if key_and_score[0] == correct_keys[i]][
                0] + 1)

    success_rate = success_rate / num_experiments
    guessing_entropy = guessing_entropy / num_experiments

    return success_rate, guessing_entropy
