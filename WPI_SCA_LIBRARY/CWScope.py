import sys

import chipwhisperer as cw
import matplotlib.pyplot as plt
import numpy as np
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
