Metric Solver API
=================
This API can be used to compute various different metrics relating to side-channel analysis. These
metrics will aid with assessing a systems security and identifying areas of interest in large trace sets.
Each metric is a standalone function and requires minimal setup to utilize.

.. py:function:: signal_to_noise_ratio(labels)

    Computes the signal-to-noise ratio of a trace set and associated labels. High magnitudes of the resulting SNR traces
    indicate cryptographic leakage at that sample.

   :param labels: A Python dictionary where the keys are labels and the values are the associated power traces. The value of
                    labels[L] is a list of power traces, list[trace_0, trace_1, ..., trace_N], associated with label L.
                    For example, the label can be the output of the AES Sbox such that L = Sbox[key ^ text].
   :type labels: dict

   :return: The SNR of the provided trace set
   :rtype: np.ndarray
   :raises TypeError: if any value in labels.items() is not a np.ndarray or list type

   :Authors: Samuel Karkache (swkarkache@wpi.edu), Trey Marcantonio (tmmarcantonio@wpi.edu)

.. py:function:: t_test(fixed_t, random_t)

    Computes the t-statistic and t-max between fixed and random trace sets. High t values indicate possible information
    leakage.

    :param random_t: The random trace set
    :param fixed_t: The fixed trace set
    :return: the t-statistic at each time sample and t-max at each trace

.. py:function:: pearson_correlation(predicted_leakage, observed_leakage, num_traces, num_samples)

    Computes the correlation between observed power traces and predicted power leakage computed using a
    key guess. The correlation when the predicted power leakage is modeled using the correct key guess has
    a relatively high magnitude.

   :param predicted_leakage: predicted leakage modeled by a given leakage model
   :param observed_leakage: observed traces collected with the key and plaintexts used to generate the predicted leakage
   :param num_traces: number of traces collected
   :param num_samples: the number of samples per trace
   :return: The correlation trace corresponding to the predicted leakage

.. py:function:: score_and_rank(key_candidates, partitions, traces, score_fcn, *args)

    Scores and ranks possible key guesses based on how likely a subkey is to be the actual key.

    :param key_candidates: All key possibilities per key partition. For 1-byte partitions it should be np.arrange(256)
    :param partitions: The number of partitions. For AES-128 there are 16 1-byte partitions.
    :param traces: A set of collected traces.
    :param score_fcn: The function used to score each key guess. NOTE: MUST BE IN THE FORM score_fcn(traces, key_guess, target_byte, ...)
    :param args: Additional arguments required for the score_fcn
    :return: Subkey ranks for each partition of the full key.

.. py:function:: score_with_correlation(traces, key_guess, target_byte, plaintexts, leakage_model)

    Scoring function that assigns a key guess a score based on the max value of the pearson correlation. In theory,
    the key guess with the highest correlation will be ranked first.

    :param traces: The collected traces
    :param key_guess: The key guess
    :param target_byte: The target byte of the key
    :param plaintexts: The plaintexts used during trace capture
    :param leakage_model: The leakage model function
    :return: The score of the key guess
