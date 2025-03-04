Differential Power Analysis (DPA)
================================

.. method:: calculate_dpa(traces, iv, order=1, key_guess=0, window_size_fma=5, num_of_traces=0):

    Unified differential power analysis method that has support for first and second order DPA.

    :param traces: The power traces to be processed
    :param iv: Intermediate algorithm values associated with the power traces
    :param key_guess: The DPA key guess
    :param window_size_fma: The window size of the moving average calculation
    :param num_of_traces: The number of traces being processed
    :returns: The result of the DPA calculation

.. method:: calculate_second_order_dpa_mem_efficient(traces, IV, window_width):

    Efficient implementation of second order DPA

    :param traces: The power traces to be processed.
    :param IV: Intermediate algorithm values associated with the power traces
    :param window_width: The window size of the moving average calculation
    :returns: The result of the DPA calculation