import chipwhisperer as cw
import cwtvla.ktp
import matplotlib.pyplot as plt
import numpy as np
from WPI_SCA_LIBRARY.FileFormat import *
import os
import tqdm as tqdm


# TODO: Implement changes in the Capture procedure in order to make them more generic

class CWScope:

    def __init__(self, firmware_name, gain=25, num_samples=5000, offset=0, simple_serial_version="1"):
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
        if simple_serial_version == "1":
            self.target = cw.target(self.scope, cw.targets.SimpleSerial)
        elif simple_serial_version == "2":
            self.target = cw.target(self.scope, cw.targets.SimpleSerial2)
        else:
            raise Exception("Unknown Simple Serial Version: {}".format(simple_serial_version))

        # configure scope parameters
        self.scope.gain.db = gain
        self.scope.adc.samples = num_samples
        self.scope.offset = offset

        # upload encryption algorithm firmware to the board
        cw.program_target(self.scope, cw.programmers.STM32FProgrammer,
                          os.path.dirname(os.path.abspath(__file__)) + "\\firmware\\{}".format(
                              firmware_name))

    def disconnect(self):
        """Disconnect CW Scope and Target"""
        self.scope.dis()
        self.target.dis()

    # TODO: It would probably be better to return the waves, texts, and keys separately
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
        power_traces = np.empty([num_traces], dtype=object)

        # configure plaintext, key generation
        ktp = cw.ktp.Basic()
        ktp.fixed_key = fixed_key
        ktp.fixed_text = fixed_pt

        for i in tqdm.tqdm(range(num_traces), desc="Capturing {} Traces".format(num_traces)):
            # get key, text pair, if fixed they will remain the same
            key, pt = ktp.next()

            # capture trace
            trace = cw.capture_trace(self.scope, self.target, pt, key)

            # append arrays if trace successfully captured
            if trace is None:
                continue

            power_traces[i] = trace

        return power_traces

    def capture_traces_tvla(self, num_traces, ktp=cwtvla.ktp.FixedVRandomText()):
        """
        Captures fixed and random trace set needed for TVLA
        :param num_traces: the number of traces to capture for each set
        :param ktp: the key text pair algorithm, defaults to cwtvla.ktp.FixedVRandomText()
        :return: (fixed_traces, random_traces)
        """
        rand_traces = np.empty([num_traces], dtype=object)
        fixed_traces = np.empty([num_traces], dtype=object)

        for i in tqdm.tqdm(range(num_traces), desc='Capturing Fixed and Random Trace Sets'):
            # capture trace from fixed group
            key, pt = ktp.next_group_A()
            trace = cw.capture_trace(self.scope, self.target, pt, key)
            if trace is not None:
                fixed_traces[i] = trace

            # capture trace from random group
            key, pt = ktp.next_group_B()
            trace = cw.capture_trace(self.scope, self.target, pt, key)
            if trace is not None:
                rand_traces[i] = trace

        return fixed_traces, rand_traces
