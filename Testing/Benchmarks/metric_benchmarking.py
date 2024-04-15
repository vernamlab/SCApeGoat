import sys
sys.path.append("../../../WPI_SCA_LIBRARY")
from WPI_SCA_LIBRARY.FileFormat import *
from WPI_SCA_LIBRARY.Metrics import *
import numpy
import time

def snr3_intermediate(rout):
    return rout

def snr_benchmarking():
    num_of_samples = [1000, 5000, 10000, 15000, 20000]
    num_of_traces = [100, 1000, 10000, 20000, 30000, 50000, 100000]
    benchmarking_results = []
    for samples in num_of_samples:
        for traces in num_of_traces:
            print(traces)
            print(samples)
            data = np.random.random_sample((traces,samples))
            print(data.itemsize)
            plaintext = np.random.randint(2, size=(traces,))
            print(plaintext.itemsize)
            sorted = organize_snr_label(data, snr3_intermediate, plaintext)
            start = time.time()
            signal_to_noise_ratio(sorted)
            end = time.time()
            print(end - start)
            del data
            del plaintext
            del sorted
            benchmarking_results.append([traces, samples, end-start])
    print(benchmarking_results)


