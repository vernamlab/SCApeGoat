from Testing.MetricVerification import read_bin_file_traces
from WPI_SCA_LIBRARY.FileFormat import *
from WPI_SCA_LIBRARY.Metrics import *
import h5py

# fixed = read_bin_file_traces("unprotected_sbox\\single\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_fixed_positive_uint8_t.bin")
# random = read_bin_file_traces("unprotected_sbox\\single\\traces\\oscilloscope_traces\\oscilloscope_traces_50k_3000_samples_random_positive_uint8_t.bin")
#
# file = FileParent("AnotherFile", "C:\\Users\\samka\\PycharmProjects\\SCLA_API_MQP\\", existing=False)
#
# experiment_1 = file.add_experiment(name="Experiment1")
# dataset_1 = experiment_1.add_dataset(name="random", data_to_add=random, datatype="float32")
# dataset_2 = experiment_1.add_dataset(name="fixed", data_to_add=fixed, datatype="float32")
# dataset_1.update_metadata("temp", "70C")
# dataset_2.update_metadata("temp", "20C")
# datasets = experiment_1.query_datasets_with_metadata("temp", "70C")

# with h5py.File(os.path.dirname(__file__) + "\\ExampleData\\ASCAD\\ATMega8515_raw_traces.h5", "r") as file:
#     # obtain data from HDF5 file
#     metadata = np.array(file['metadata'][:10000])
#     traces = file['traces'][:10000, :]
#     keys = metadata['key'][:, 2]
#     plaintexts = metadata['plaintext'][:, 2]
#     rout = metadata['masks'][:, 15]
#
#     def snr2_intermediate(keys, plaintexts, rout):
#         return Sbox[keys ^ plaintexts] ^ rout
#
#     file = FileParent("AnotherFile", "C:\\Users\\samka\\PycharmProjects\\SCLA_API_MQP\\", existing=False)
#     experiment_1 = file.add_experiment(name="Experiment1")
#     dataset_1 = experiment_1.add_dataset(name="traces", data_to_add=traces, datatype="float32")
#     dataset_2 = experiment_1.add_dataset(name="keys", data_to_add=keys, datatype="uint8")
#     dataset_3 = experiment_1.add_dataset(name="plaintexts", data_to_add=plaintexts, datatype="uint8")
#     dataset_4 = experiment_1.add_dataset(name="rout", data_to_add=rout, datatype="uint8")
#
#     experiment_1.calculate_snr("traces", snr2_intermediate, "keys", "plaintexts", "rout", visualize=True, save_data=True, save_graph=True)
# def snr2_intermediate(keys, plaintexts, rout):
#     return Sbox[keys ^ plaintexts] ^ rout
#
# file = FileParent("AnotherFile-2", "C:\\Users\\samka\\PycharmProjects\\SCLA_API_MQP\\", existing=True)
# file.get_experiment("Experiment1").calculate_snr("traces", snr2_intermediate, "keys", "plaintexts", "rout", visualize=True, save_data=True, save_graph=True)
