Metric Solver API
=================
This API can be used to compute various different metrics relating to side-channel analysis. These
metrics will aid with assessing a systems security and identifying areas of interest in large trace sets.
Each metric is a standalone function and requires minimal setup to utilize.

.. py:function:: signal_to_noise_ratio (labels)

    Computes the signal-to-noise ratio of a set of traces associated with intermediate labels. Spikes in
    magnitude of the resulting SNR trance indicate possible cryptographic information leakage.

   :param labels: SNR label set where label[L] are power traces associated with label L
   :type labels: dict
   :return: The SNR trace of the supplied trace set

.. py:function:: t_test (fixed_t, random_t, num_samples, step=2000, order_2=False):

    Computes the t-statistic between fixed and random trace sets.

    :param fixed_t: the set of traces collected with a fixed pt
    :param random_t: the set of traces collected with a random pt
    :param num_samples: the number of samples per trace
    :param step: TODO: ask Dev about this
    :param order_2: compute second order
    :return: (tf, tf_2) where tf is the first order t-statistic and tf_2 is the second order t-statistic

.. py:function:: pearson_correlation (predicted_leakage, observed_leakage, num_traces, num_samples)

    Computes the correlation between observed power traces and predicted power leakage computed using a
    key guess. The correlation when the predicted power leakage is modeled using the correct key guess has
    a relatively high magnitude.

   :param predicted_leakage: predicted leakage modeled by a given leakage model
   :param observed_leakage: observed traces collected with the key and plaintexts used to generate the predicted leakage
   :param num_traces: number of traces collected
   :param num_samples: the number of samples per trace
   :return: The correlation trace corresponding to the predicted leakage


.. py:function:: leakage_model_hw (plaintext, key)

    Hamming weight leakage model. Returns the Hamming weight of intermediate output Sbox[key ^ plaintext]

    :param plaintext: the plaintext
    :param key: the key used to encrypt the plaintext
    :return: the intermediate output

.. py:function:: generate_hypothetical_leakage (num_traces, plaintexts, subkey_guess, target_byte, leakage_model=leakage_model_hw):

     Generates hypothetical leakage based on a provided leakage model. Useful when conducting pearson correlation metric.

    :param num_traces: The number of traces collected when measuring the observed leakage
    :param plaintexts: The array of plaintexts used to collect the observed leakage
    :param subkey_guess: the subkey guess
    :param target_byte: the target byte of the key
    :param leakage_model: the leakage model that will be used, defaults to the pre-defined hamming weight leakage model
    :return: numpy array of the hypothetical leakage

.. py:function:: score_and_rank (key_candidates, partitions, traces, score_fcn, *args)

    Scores and ranks possible key guesses based on how likely a subkey is to be the actual key.

    :param key_candidates: All key possibilities per key partition. For 1-byte partitions it should be np.arrange(256)
    :param partitions: The number of partitions. For AES-128 there are 16 1-byte partitions.
    :param traces: A set of collected traces.
    :param score_fcn: The function used to score each key guess. NOTE: MUST BE IN THE FORM score_fcn(traces, key_guess, target_byte, ...)
    :param args: Additional arguments required for the score_fcn
    :return: Subkey ranks for each partition of the full key.

.. py:function:: score_with_correlation(traces, key_guess, target_byte, plaintexts, leakage_model)

    Scoring function that assigns a key guess a score based on the max value of the pearson correlation.

    :param traces: The collected traces
    :param key_guess: The key guess
    :param target_byte: The target byte of the key
    :param plaintexts: The plaintexts used during trace capture
    :param leakage_model: The leakage model function
    :return: The score of the key guess
