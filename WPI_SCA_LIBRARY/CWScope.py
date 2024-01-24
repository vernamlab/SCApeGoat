import sys

import chipwhisperer as cw
import matplotlib.pyplot as plt
import numpy as np
from WPI_SCA_LIBRARY.FileFormat import *
import os
import struct


class CWScope:

    def __init__(self, firmware_name, gain=25, num_samples=5000, offset=0, segmented=False):
        """
        Initializes a CW scope object
        :param firmware_name: The name of the compiled firmware that will be loaded on the CW device.
        :param gain: The gain of the CW scope
        :param num_samples: The number of samples to collect for each trace on the CW scope
        :param offset: The offset of the trace collection
        """
        # setup scope
        self.scope = cw.scope()
        self.scope.default_setup()

        # configure target
        self.target = cw.target(self.scope)

        # configure scope parameters
        self.scope.gain.db = gain
        self.scope.adc.samples = num_samples
        self.scope.offset = offset
        self.segmented = segmented

        if segmented:
            self.scope.adc.fifo_fill_mode = "segment"

        # upload encryption algorithm firmware to the board
        cw.program_target(self.scope, cw.programmers.STM32FProgrammer, str(os.path.abspath(firmware_name)))

    def disconnect(self):
        """Disconnect CW Scope and Target"""
        self.scope.dis()
        self.target.dis()

    def standard_capture_traces(self, num_traces, fixed_key=False, fixed_pt=False):
        """
        Capture traces from CW Device and return as an array. Ensure that the scope as been properly configured using
        the constructor.

        :param num_traces: The number of traces to capture
        :param fixed_key: Whether to use a fixed key in trace capture
        :param fixed_pt: Whether to use a fixed plaintext in trace capture
        :return: A 2D array representing the collected power traces.
        """
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

    def arr_to_hdf5(self, file_name, experiment_name, traces, plaintexts, keys, num_traces):
        """
        Converts arrays/lists containing traces, pt, and keys to hdf5 file format
        :param file_name: The name of the file that will be saved
        :param experiment_name: The name of the experiment that will be associated with the trace collection
        :param traces: a list of power traces
        :param plaintexts: a list of plaintexts
        :param keys: a list of keys
        :param num_traces: the number of traces
        :return: None (a file is generated in working directory)
        """

        # enforce that all lists have the same length
        if len(traces) != len(plaintexts) or len(plaintexts) != len(keys) or len(plaintexts) != len(experiment_name):
            raise Exception("Malformed trace, pt, key data")

        # configure hdf5 file class
        file_class = HDF5FileClass(file_name)
        file_class.addExperiment(experiment_name)
        experiment = file_class.experiments[experiment_name]

        # add plaintext, trace, and label dataset to file
        experiment.addDataset("plaintext", (num_traces, 16), definition="Plaintext Input To the Algorithm",
                              dtype='uint8')
        plaintext_dataset = experiment.dataset["plaintext"]

        experiment.addDataset("keys", (num_traces, 16), definition="Key To the Algorithm", dtype='uint8')
        key_dataset = experiment.dataset["keys"]

        experiment.addDataset("traces", (num_traces, self.scope.adc.samples), definition="Traces", dtype='float64')
        traces_dataset = experiment.dataset["traces"]

        for i in range(num_traces):
            plaintext_dataset.addData(i, traces[i])
            traces_dataset.addData(i, plaintexts[i])
            key_dataset.addData(i, keys[i])

    def cw_to_hdf5(self, file_name, experiment_name, num_traces, fixed_key=False, fixed_pt=False):
        """
        Captures traces from the CW device and saves them and related metadata to an hdf5 file.
        :param file_name: The name of the file that will be saved
        :param experiment_name: The name of the experiment that will be associated with the trace collection
        :param num_traces: The number of traces to capture
        :param fixed_key: Whether to use a fixed key in trace capture
        :param fixed_pt: Whether to use a fixed plaintext in trace capture
        :return: None (a file is generated in working directory)
        """

        # capture traces
        traces = self.standard_capture_traces(num_traces, fixed_key, fixed_pt)

        # configure hdf5 file class
        file_class = HDF5FileClass(file_name)
        file_class.addExperiment(experiment_name)
        experiment = file_class.experiments[experiment_name]

        # add plaintext, trace, and label dataset to file
        experiment.addDataset("plaintext", (num_traces, 16), definition="Plaintext Input To the Algorithm",
                              dtype='uint8')
        plaintext_dataset = experiment.dataset["plaintext"]

        experiment.addDataset("keys", (num_traces, 16), definition="Key To the Algorithm", dtype='uint8')
        key_dataset = experiment.dataset["keys"]

        experiment.addDataset("traces", (num_traces, self.scope.adc.samples), definition="Traces", dtype='float64')
        traces_dataset = experiment.dataset["traces"]

        for i in range(len(traces)):
            plaintext_dataset.addData(i, traces[i].textin)
            traces_dataset.addData(i, traces[i].wave)
            key_dataset.addData(i, traces[i].key)

    # TODO: Still need to verify the functionality here
    def segmented_capture_traces(self, num_traces):
        """
        Captures traces using the segmented fifo fill mode. Multiple encryption are performed for a fixed key
        and plaintext and stored in the ChipWhisperer buffer. Each traces corresponds to a segment in the buffer.
        The procedure finished once greater than num_traces segments are captured.
        :param num_traces: the number of traces to capture
        :return: an array of the captured power traces
        """

        seg_max = round(self.scope.adc.oa.hwMaxSamples / self.scope.adc.samples + 1)
        done = False

        # configure plaintext, key generation
        ktp = cw.ktp.Basic()
        key, pt = ktp.next()

        segments = []

        self.target.simpleserial_write('s', struct.pack(">H", seg_max))

        while not done:
            self.scope.arm()
            self.target.simpleserial_write('f', pt)
            self.scope.capture_segmented()
            buffer = self.scope.get_last_trace_segmented()
            segments.extend(buffer)

            self.target.flush()

            if len(segments) > num_traces:
                done = True

        return segments, key, pt