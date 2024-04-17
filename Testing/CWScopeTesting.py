import time

import numpy as np

from WPI_SCA_LIBRARY.CWScope import *

firmware_path = "C:\\Users\\samka\\PycharmProjects\\SCLA_API_MQP\\WPI_SCA_LIBRARY\\firmware\\simpleserial-aes-CWLITEARM-SS_2_1.hex"


def benchmark_capture_procedures():
    scope = CWScope(firmware_path, gain=25, num_samples=3000, offset=0, target_type=cw.targets.SimpleSerial2,
                    target_programmer=cw.programmers.STM32FProgrammer)

    num_traces = [100, 1000, 2000, 3000, 4000, 5000, 10000, 20000, 30000, 50000, 75000, 100000]
    # times = []
    #
    # for num_trace in num_traces:
    #     start = time.time()
    #     scope.standard_capture_traces(num_trace)
    #     end = time.time()
    #     times.append(end - start)
    #
    # plt.plot(num_traces, times)
    # plt.title("Standard Capture Procedure Benchmark")
    # plt.xlabel("Number of Traces")
    # plt.grid()
    # plt.ylabel("Time (s)")
    # plt.show()

    times = []

    for num_trace in num_traces:
        start = time.time()
        scope.capture_traces_tvla(num_trace)
        end = time.time()
        times.append(end - start)

    plt.plot(num_traces, times)
    plt.title("T-Test Capture Procedure Benchmark")
    plt.xlabel("Number of Traces")
    plt.grid()
    plt.ylabel("Time (s)")
    plt.show()


def test_cw_to_file_format():
    scope = CWScope(firmware_path, gain=25, num_samples=3000, offset=0, target_type=cw.targets.SimpleSerial2,
                    target_programmer=cw.programmers.STM32FProgrammer)

    file = FileParent("AnotherFile", "C:\\Users\\samka\\PycharmProjects\\SCLA_API_MQP\\", existing=True)
    scope.cw_to_file_framework(1000, file, "TestExperiment")


scope = CWScope(firmware_path, gain=25, num_samples=3000, offset=0, target_type=cw.targets.SimpleSerial2, target_programmer=cw.programmers.STM32FProgrammer)
ktp = cw.ktp.Basic()

# keys = [ktp.next()[0]] * 1000
# texts = [ktp.next()[1]] * 1000
# scope.standard_capture_traces(1000, keys, texts)
