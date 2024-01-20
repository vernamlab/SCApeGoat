Metric Solver API
=================

.. py:function:: signal_to_noise_ratio(labels)

   The signal-to-noise ratio of a power trace is defined as the ratio of a signal's data component to the signal's noise
   component. For side-channel analysis, the SNR of a power trace relates to the ability for an attacker to obtain
   information from a power trace during an attack. The effectiveness of side channel attack increases for larger SNR
   values since the signal leakage is more prominent relative to the noise of the signal. Typically recorded power traces
   need to be partitioned into different sets called labels.

   :param label: SNR label set where label[l] are power traces associated with label l
   :type kind: lst[lst[float]]
   :return: The SNR trace of the supplied trace set
   :rtype: list[float]