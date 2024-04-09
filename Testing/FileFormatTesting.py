from Testing.MetricVerification import read_bin_file_traces
from WPI_SCA_LIBRARY.FileFormat import *


fixed = read_bin_file_traces("unprotected_sbox\\single\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_fixed_positive_uint8_t.bin")
random = read_bin_file_traces("unprotected_sbox\\single\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")

file = FileParent("AnotherFile", "C:\\Users\\samka\\PycharmProjects\\SCLA_API_MQP\\", existing=False)

experiment_1 = file.add_experiment(name="Experiment1")
dataset_1 = experiment_1.add_dataset(name="random", data_to_add=random, datatype="float32")
dataset_2 = experiment_1.add_dataset(name="random", data_to_add=fixed, datatype="float32")
dataset_3 = experiment_1.add_dataset(name="random", data_to_add=fixed, datatype="float32")
dataset_1.update_metadata("temp", "70C")
dataset_2.update_metadata("temp", "20C")

datasets = experiment_1.query_datasets_with_metadata("temp", "70C")
print(datasets)
