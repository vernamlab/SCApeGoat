from Testing.MetricVerification import read_bin_file_traces
from WPI_SCA_LIBRARY.FileFormat import *
from WPI_SCA_LIBRARY.Metrics import *
import h5py
import time
import matplotlib.pyplot as plt

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


def benchmark_file_format():

    num_traces = [1000, 5000, 10000, 15000, 20000, 25000, 30000, 40000, 50000, 75000, 80000, 100000]
    times_save = []
    time_load = []
    h5_times_save = []
    h5_time_load = []

    for num_trace in num_traces:
        data = np.array(np.random.random(size=(num_trace, 3000)), dtype="float32")

        start_save = time.time()
        file = FileParent(name="AnotherFile", path="C:\\Users\\samka\\OneDrive\\Desktop\\", existing=True)
        exp = file.get_experiment("Experiment1")
        exp.add_dataset("dataset_{}".format(num_trace), data, datatype="float32")
        end_save = time.time()

        times_save.append(end_save - start_save)

        # load the data, measure the time
        start_load = time.time()
        file = FileParent(name="AnotherFile", path="C:\\Users\\samka\\OneDrive\\Desktop\\", existing=True)
        exp = file.get_experiment("Experiment1")
        loaded = exp.get_dataset("dataset_{}".format(num_trace)).read_all()
        end_load = time.time()
        time_load.append(end_load - start_load)

        # hdf5, save the data
        start_save_h5 = time.time()
        with h5py.File("data.h5", "w") as file:
            file.create_dataset("dataset_{}".format(num_trace), data=data)
        end_save_h5 = time.time()

        h5_times_save.append(end_save_h5 - start_save_h5)

        start_load_h5 = time.time()
        with h5py.File('data.h5', 'r') as hf:
            loaded1 = hf["dataset_{}".format(num_trace)][:]
        end_load_h5 = time.time()

        h5_time_load.append(end_load_h5 - start_load_h5)

        print("Done with {} traces".format(num_trace))

    plt.plot(num_traces, times_save, label="Custom File Framework")
    plt.plot(num_traces, h5_times_save, label="HDF5")
    plt.legend()
    plt.ylabel("Time (s)")
    plt.xlabel("Number of traces")
    plt.title("File Framework Saving Benchmark: Varying Traces")
    plt.grid()
    plt.show()

    plt.plot(num_traces, time_load, label="Custom File Framework")
    plt.plot(num_traces, h5_time_load, label="HDF5")
    plt.legend()
    plt.ylabel("Time (s)")
    plt.xlabel("Number of traces")
    plt.title("File Framework Loading Benchmark: Varying Traces")
    plt.grid()
    plt.show()


file = FileParent(name="AnotherFile", path="C:\\Users\\samka\\OneDrive\\Desktop\\", existing=True)
