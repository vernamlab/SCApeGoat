import sys
sys.path.append("../../../WPI_SCA_LIBRARY")
from WPI_SCA_LIBRARY.FileFormat import *
from WPI_SCA_LIBRARY.Metrics import *
from WPI_SCA_LIBRARY.LeakageModels import *
import numpy
import time

def snr3_intermediate(rout):
    return rout

def snr_benchmarking():
    num_of_samples = [1000, 5000, 10000, 15000, 20000, 50000]
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

def t_test_benchmarking():
    num_of_samples = [1000, 5000, 10000, 15000, 20000, 50000]
    num_of_traces = [100, 1000, 10000, 20000, 30000, 50000, 100000]
    benchmarking_results = []
    for samples in num_of_samples:
        for traces in num_of_traces:
            dataOne = np.random.random_sample((traces,samples))
            dataTwo = np.random.random_sample((traces, samples))
            start = time.time()
            t_test_tvla(dataOne, dataTwo)
            end = time.time()
            print(end - start)
            del dataOne
            del dataTwo
            benchmarking_results.append([traces, samples, end-start])
    print(benchmarking_results)

def correlation_metric():
    num_of_samples = [1000, 5000, 10000, 15000, 20000, 50000]
    num_of_traces = [100, 1000, 10000, 20000, 30000, 50000, 100000]
    benchmarking_results = []
    for samples in num_of_samples:
        for traces in num_of_traces:
            leakage = np.random.randint(16, size = (traces,))
            unmasked_random = np.random.random_sample((traces, samples))
            start = time.time()
            pearson_correlation(leakage, unmasked_random)
            end = time.time()
            print(end - start)
            del leakage
            del unmasked_random
            benchmarking_results.append([traces, samples, end - start])
    print(benchmarking_results)

def score_and_rank_benchmarking():
    num_of_samples = [1000, 5000, 10000, 20000]
    num_of_traces = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 9000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000]
    benchmarking_results = []
    for samples in num_of_samples:
        for traces in num_of_traces:
            key_candidates = range(255)
            unmasked_random = np.random.random_sample((traces, samples))
            texts = np.random.randint(16, size=(traces,16))
            start = time.time()
            score_and_rank(key_candidates, 0, unmasked_random, score_with_correlation, texts, leakage_model_hamming_distance)
            end = time.time()
            print(end - start)
            del unmasked_random
            del texts
            benchmarking_results.append([traces, samples, end - start])
    print(benchmarking_results)