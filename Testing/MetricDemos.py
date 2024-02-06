import os.path

import cwtvla
import tqdm

from WPI_SCA_LIBRARY.Metrics import *
from WPI_SCA_LIBRARY.CWScope import *
import numpy as np
import matplotlib.pyplot as plt

# TODO: This entire file needs to fixed due to updates in the CWSCope and Metric Functionality

def t_test_demo():
    """
    Computes t-test and plot the t-statistics and t-max for 1000 traces of fixed and 1000 traces of random
    """
    cw_scope = CWScope(
        "simpleserial-aes_CW308-STM32F3_MASKEDAES_ANSSI+UNROLLED+KEYSCHEDULE.hex",
        25,
        24000,
        0,
        simple_serial_version="1"
    )

    # capture traces
    fixed_t, rand_t = cw_scope.capture_traces_tvla(2000)

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

    plt.plot(t_max)
    plt.title("Max T-value vs number of traces")
    plt.ylabel("T-statistic")
    plt.xlabel("Number of traces")
    plt.show()


def correlation_demo():
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


def score_and_rank_demo():
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


def correct_key_rank_vs_num_traces():
    """
     Scores and ranks keys using correlation. Compares result to the actual key.
     """
    cw_scope = CWScope(
        "simpleserial-aes-CWLITEARM-SS_2_1.hex",
        25,
        1400,
        0,
        simple_serial_version="2"
    )

    trace_amounts = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
    correct_key_ranks = []
    target_key_byte = 0

    for num_traces in trace_amounts:
        traces = cw_scope.standard_capture_traces(num_traces, fixed_key=True, fixed_pt=False)

        keys = []
        texts = []
        waves = []
        for trace in traces:
            keys.append(trace.key)
            texts.append(trace.textin)
            waves.append(trace.wave)

        # There are 16 partitions each are 1-byte
        key_candidates = np.arange(256)

        # score and rank each key guess for each partition
        rankedKeys = score_and_rank_subkey(key_candidates, target_key_byte, waves, score_with_correlation, texts,
                                           leakage_model_hw)
        correct_key_ranks.append(np.where(rankedKeys == keys[0][target_key_byte])[0])

    plt.plot(trace_amounts, correct_key_ranks)
    plt.xlabel("Number of Traces")
    plt.ylabel("Rank")
    plt.title("Rank of Correct Key Guess vs. Number of Traces (1400 samples per trace)")
    plt.show()


def success_rate_guessing_entropy_demo():
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
