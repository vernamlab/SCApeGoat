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

.. py:function:: pearson_correlation (predicted_leakage, observed_leakage, num_traces, num_samples)

    Compares two trace sets corresponding to predicted and observed leakage. High magnitudes indicate
    that an intermediate value may be leaked at that time sample.

   :param predicted_leakage: predicted traces associated with intermediate values and a key guess and plaintext value
   :type predicted_leakage: list[float]
   :param observed_leakage: predicted traces associated with intermediate values and a key guess and plaintext value
   :type observed_leakage: list[float]
   :param num_traces: number of traces in each trace set
   :type num_traces: int
   :param num_samples: the number of samples per trace
   :type num_samples: int
   :return: The correlation trace corresponding to the predicted leakage
   :rtype: list[float]