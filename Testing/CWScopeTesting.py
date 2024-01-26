import numpy as np
from matplotlib import pyplot as plt
import time

from WPI_SCA_LIBRARY.CWScope import *


class CWScopeTesting:
    def __init__(self):
        self.cw_scope = CWScope("firmware\\simpleserial-aes-CWLITEARM-SS_2_1.hex", 25, 5000, 0,
                                simple_serial_version="2")

    def capture_one_trace(self):
        traces = self.cw_scope.standard_capture_traces(1, True, False)
        plt.plot(traces[0].wave)
        plt.title("Power Trace Collected From Chip Whisperer")
        plt.xlabel("Sample")
        plt.ylabel("Power")
        plt.show()

    def standard_trace_collection_timing(self, num_traces):
        start_time = time.time()
        self.cw_scope.standard_capture_traces(num_traces, True, True)
        end_time = time.time()
        return end_time - start_time

    def plot_collection_timings(self):
        timings = [self.standard_trace_collection_timing(1), self.standard_trace_collection_timing(10),
                   self.standard_trace_collection_timing(50), self.standard_trace_collection_timing(100),
                   self.standard_trace_collection_timing(1000), self.standard_trace_collection_timing(10000)]
        num_traces = [1, 10, 50, 100, 1000, 10000]

        plt.plot(num_traces, timings)
        plt.title("Trace Collection C-Term Optimizations")
        plt.xlabel("Num Traces")
        plt.ylabel("Time (seconds)")
        plt.show()


# CWScopeTesting().plot_collection_timings()
