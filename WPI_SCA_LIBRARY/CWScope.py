import sys

import chipwhisperer as cw
import matplotlib.pyplot as plt
import numpy as np
from WPI_SCA_LIBRARY.FileFormat import *
import os


class CWScope:

    def __init__(self, firmware_name, gain=25, num_samples=5000, offset=0):
        # setup scope
        self.scope = cw.scope()
        self.scope.default_setup()

        # configure target
        self.target = cw.target(self.scope)

        # configure scope parameters
        self.scope.gain.db = gain
        self.scope.adc.samples = num_samples
        self.scope.offset = offset

        # upload encryption algorithm firmware to the board
        cw.program_target(self.scope, cw.programmers.STM32FProgrammer, str(os.path.abspath(firmware_name)))

    def disconnect(self):
        self.scope.dis()
        self.target.dis()

    def standard_capture_traces(self, num_traces, fixed_key=False, fixed_pt=False):
        # init return values
        power_traces = []

        # configure plaintext, key generation
        ktp = cw.ktp.Basic()
        ktp.fixed_key = fixed_key
        ktp.fixed_pt = fixed_pt

        for i in range(num_traces):
            # get key, text pair, if fixed they will remain the same
            key, pt = ktp.next()

            # capture trace
            trace = cw.capture_trace(self.scope, self.target, pt, key)

            # append arrays if trace successfully captured
            if trace:
                power_traces.append(trace)

        return power_traces

    def cw_to_hdf5(self, file_name, experiment_name, num_traces, fixed_key=False, fixed_pt=False):

        # capture traces
        traces = self.standard_capture_traces(num_traces, fixed_key, fixed_pt)

        # configure hdf5 file class
        fileClass = HDF5FileClass(file_name)
        fileClass.addExperiment(experiment_name)
        experiment = fileClass.experiments[experiment_name]

        # add plaintext, trace, and label dataset to file
        experiment.addDataset("plaintext", (num_traces, 16), definition="Plaintext Input To the Algorithm", dtype='uint8')
        plaintextDataset = experiment.dataset["plaintext"]

        experiment.addDataset("key", (num_traces, 16), definition="Key To the Algorithm", dtype='uint8')
        keyDataset = experiment.dataset["key"]

        experiment.addDataset("traces", (num_traces, self.scope.adc.samples), definition="Traces", dtype='float64')
        tracesDataset = experiment.dataset["traces"]

        for i in range(len(traces)):
            plaintextDataset.addData(i, traces[i].textin)
            tracesDataset.addData(i, traces[i].wave)
            keyDataset.addData(i, traces[i].key)