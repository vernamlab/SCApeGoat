Leakage Models
==============
This module contains pre-defined leakage models that can be used during side-channel analysis experiments. For example,
these leakage models are useful when generating the predicted leakage for Pearson's correlation coefficient.

.. py:function:: leakage_model_hamming_weight(num_traces, plaintexts, subkey_guess, target_byte)

    Generates hypothetical leakage based on the hamming weight of the AES sbox.

    :param num_traces: The number of traces collected when measuring the observed leakage
    :type num_traces: int
    :param plaintexts: The array of plaintexts used to collect the observed leakage
    :type plaintexts: list | np.ndarray
    :param subkey_guess: the subkey guess
    :type subkey_guess: any
    :param target_byte: the target byte of the key
    :type target_byte: int
    :return: numpy array of the hypothetical leakage
    :rtype: np.ndarray
    :Authors: Samuel Karkache (swkarkche@wpi.edu)

.. py:function:: leakage_model_hamming_distance(num_traces, plaintexts, subkey_guess, target_byte)

    Generates hypothetical leakage using the damming distance leakage model. In this implementation the reference state
    is the output of the sbox at index 0.

    :param num_traces: The number of traces collected when measuring the observed leakage
    :type num_traces: int
    :param plaintexts: The array of plaintexts used to collect the observed leakage
    :type plaintexts: list | np.ndarray
    :param subkey_guess: the subkey guess
    :type subkey_guess: any
    :param target_byte: the target byte of the key
    :type target_byte: int
    :return: numpy array of the hypothetical leakage
    :rtype: np.ndarray
    :Authors: Samuel Karkache (swkarkache@wpi.edu)
