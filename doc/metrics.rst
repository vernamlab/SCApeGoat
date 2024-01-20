Metric Solver API
=================

.. py:function:: signal_to_noise_ratio (labels)

    Computes the signal to noise ratio of a set of traces associated with intermediate labels.

   :param labels (lst[lst[float]]): SNR label set where label[L] are power traces associated with label L
   :return: The SNR trace of the supplied trace set
   :rtype: list[float]

.. py:function:: pearson_correlation (predicted_leakage, observed_leakage, num_traces, num_samples)

    Compares two trace sets corresponding to predicted and observed leakage. High magnitudes indicate
    that an intermediate value may be leaked at that time sample.

   :param predicted_leakage (lst[float]): predicted traces associated with intermediate values and a key guess and plaintext value
   :param observed_leakage (lst[float]): predicted traces associated with intermediate values and a key guess and plaintext value
   :param num_traces (int): number of traces in each trace set
   :param num_samples (int): the number of samples per trace
   :return: The correlation trace corresponding to the predicted leakage
   :rtype: list[float]