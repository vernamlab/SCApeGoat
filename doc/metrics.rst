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

    Computes the t-statistic and t-max between fixed and random trace sets. T-statistic magnitudes above or below
    \|th\| = 4.5 indicate cryptographic vulnerabilities.

    :param random_t: The random trace set
    :type random_t: np.ndarray | list
    :param fixed_t: The fixed trace set
    :type fixed_t: np.ndarray | list
    :return: The t-statistic at each time sample and t-max at each trace as a tuple of numpy arrays
    :rtype: (np.ndarray, np.ndarray)
    :raises ValueError: if fixed_t and random_t do not have the same length
    :Authors: Dev Mehta (dmmehta2@wpi.edu), Samuel Karkache (swkarkache@wpi.edu)

.. py:function:: pearson_correlation(predicted_leakage, observed_leakage, num_traces, num_samples)


.. py:function:: score_and_rank(key_candidates, partitions, traces, score_fcn, *args)


.. py:function:: score_with_correlation(traces, key_guess, target_byte, plaintexts, leakage_model)

