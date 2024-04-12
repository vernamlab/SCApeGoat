from __future__ import annotations

import shutil

import chipwhisperer as cw
import cwtvla.ktp
import numpy as np
from WPI_SCA_LIBRARY.FileFormat import *
import os
import tqdm as tqdm


class CWScope:

    def __init__(self, firmware_path: str, gain: int = 25, num_samples: int = 5000, offset: int = 0,
                 target_type: any = cw.targets.SimpleSerial, target_programmer: any = cw.programmers.STM32FProgrammer) -> None:
        """
        Initializes a CW scope object
        :param firmware_path: The name of the compiled firmware that will be loaded on the CW target board
        :type firmware_path: str
        :param gain: The gain of the CW scope
        :type gain: int
        :param num_samples: The number of samples to collect for each trace on the CW scope
        :type num_samples: int
        :param offset: The tine offset for CW scope trace collection
        :type offset: int
        :param target_type: The target type of the CW scope. This depends on the specific ChipWhisperer device that you are using.
        :type target_type: any
        :param target_programmer: The target programmer of the CW scope. This depends on the specific ChipWhisperer device that you are using.
        :type target_programmer: any
        :return: None
        :Authors: Samuel Karkache (swkarkache@wpi.edu)
        """
        # setup scope
        self.scope = cw.scope()
        self.scope.default_setup()
        self.target = cw.target(self.scope, target_type)

        # configure scope parameters
        self.scope.gain.db = gain
        self.scope.adc.samples = num_samples
        self.scope.offset = offset

        # upload encryption algorithm firmware to the board
        cw.program_target(self.scope, target_programmer, firmware_path)

    def disconnect(self):
        """Disconnect CW Scope and Target"""
        self.scope.dis()
        self.target.dis()

    def standard_capture_traces(self, num_traces: int,
                                experiment_keys: np.ndarray = None,
                                experiment_texts: np.ndarray = None,
                                fixed_key: bool = True,
                                fixed_pt: bool = False) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray):
        """
        Capture procedure for ChipWhisperer devices. Will return a specified number of traces and the data associated
        with the collection.
        :param num_traces: The number of traces to capture
        :type num_traces: int
        :param experiment_keys: A collection of keys to use for the capture of each trace. If not specified, the procedure
                                will use the cw basic key generation `key = cw.ktp.Basic()[0]`
        :type experiment_keys: np.ndarray
        :param experiment_texts: A collection of texts to use for the capture of each trace. If not specified, the procedure
                                will use the cw basic plaintext generation `text = cw.ktp.Basic()[1]`
        :type experiment_texts: np.ndarray
        :param fixed_key: Whether to use a fixed key for cw.ktp key generation. Ignored if a collection of keys are supplied.
        :type fixed_key: bool
        :param fixed_pt: Whether to use a fixed plaintext for cw.ktp text generation. Ignored if a collection of texts are supplied.
        :type fixed_pt: bool
        :return: a tuple containing the power traces, keys, plaintexts, and ciphertexts for the experiment
        :rtype: tuple(np.ndarray, np.ndarray, np.ndarray, np.ndarray)
        :raises TypeError: if the length of the specified experiment keys and experiment texts are not equal to each other or the number of traces
                            to be collected.
        :Authors: Samuel Karkache (swkarkache@wpi.edu)
        """

        # reject bad params
        if experiment_texts is not None and len(experiment_texts) != num_traces:
            raise TypeError("The collection of plaintext must be the same length as the number of traces to be collected")
        if experiment_keys is not None and len(experiment_keys) != num_traces:
            raise TypeError("The collections of keys must be the same length as the number of traces to be collected")
        if experiment_texts is not None and experiment_keys is not None:
            if len(experiment_texts) != len(experiment_keys):
                raise TypeError("The length of the collection keys is not equal to the length of the collection of texts")

        # standard ktp setup, can be bypassed if keys or texts array are None type
        ktp = cw.ktp.Basic()
        ktp.fixed_key = fixed_key
        ktp.fixed_text = fixed_pt

        if experiment_keys is not None:
            key_length = len(experiment_keys[0])
        else:
            key_length = 16

        if experiment_texts is not None:
            text_length = len(experiment_texts[0])
        else:
            text_length = 16

        # init return values
        traces = np.empty([num_traces, self.scope.adc.samples], dtype=object)
        keys = np.empty([num_traces, key_length], dtype=object)
        texts = np.empty([num_traces, text_length], dtype=object)
        ciphertexts = np.empty([num_traces, text_length], dtype=object)

        for i in tqdm.tqdm(range(num_traces), desc="Capturing {} Traces".format(num_traces)):

            if experiment_keys is None:
                key = ktp.next()[0]
            else:
                key = experiment_keys[i]
            if experiment_texts is None:
                text = ktp.next()[1]
            else:
                text = experiment_texts[i]

            # capture trace
            trace = cw.capture_trace(self.scope, self.target, text, key)

            # append arrays if trace successfully captured
            if trace is None:
                continue

            traces[i] = trace.wave
            keys[i] = trace.key
            texts[i] = trace.textin
            ciphertexts[i] = trace.textout

        return traces, keys, texts, ciphertexts

    def capture_traces_tvla(self, num_traces: int, group_a_keys: np.ndarray = None, group_a_texts: np.ndarray = None,
                            group_b_keys: np.ndarray = None, group_b_texts: np.ndarray = None,
                            ktp: any = cwtvla.ktp.FixedVRandomText()) -> (np.ndarray, np.ndarray):
        """
        Captures fixed and random trace set needed for TVLA
        :param group_a_keys: An array of keys for group A
        :param group_a_texts: An array of texts for group A
        :param group_b_keys: An array of keys for group B
        :param group_b_texts: An array of texts for group B
        :param num_traces: The number of traces to capture for each set
        :param ktp: the key text pair algorithm, defaults to cwtvla.ktp.FixedVRandomText(). To use a custom ktp, you would
                    need to provide a class that has methods named `next_group_A()` that specifies the fixed text/key and
                    a method named `next_group_B()` that specifies
        :return: (fixed_traces, random_traces)
        """
        rand_traces = np.empty([num_traces, self.scope.adc.samples], dtype=object)
        fixed_traces = np.empty([num_traces, self.scope.adc.samples], dtype=object)

        for i in tqdm.tqdm(range(num_traces), desc='Capturing Fixed and Random Trace Sets'):
            # capture trace from fixed group
            if group_a_keys is None or group_a_texts is None:
                key, pt = ktp.next_group_A()
            else:
                key = group_a_keys[i]
                pt = group_a_texts[i]

            trace = cw.capture_trace(self.scope, self.target, pt, key)
            if trace is not None:
                fixed_traces[i] = trace.wave

            # capture trace from random group
            if group_b_keys is None or group_b_texts is None:
                key, pt = ktp.next_group_B()
            else:
                key = group_b_keys[i]
                pt = group_b_texts[i]

            trace = cw.capture_trace(self.scope, self.target, pt, key)
            if trace is not None:
                rand_traces[i] = trace.wave

        return fixed_traces, rand_traces

    def cw_to_file_framework(self, num_traces: int,  file_parent: FileParent, experiment_name: str,
                             keys: np.ndarray = None, texts: np.ndarray = None,
                             fixed_key: bool = True, fixed_pt: bool = False) -> None:
        """
        Captures traces on a ChipWhisperer device and saves them directly to the custom file framework.
        :param num_traces: The number of traces to capture
        :param file_parent: The FileParent object to save the file to
        :param experiment_name: The name of the experiment
        :param keys: The keys for the experiment
        :param texts: The plaintexts for the experiment
        :param fixed_key: Whether the key should be fixed (assuming the keys and texts parameters are None)
        :param fixed_pt: Whether the plaintext should be fixed (assuming the keys and texts parameters are None)
        :return: None
        """

        traces, keys, plaintexts, ciphertexts = self.standard_capture_traces(num_traces, keys, texts, fixed_key, fixed_pt)

        experiment_name = sanitize_input(experiment_name)

        if experiment_name not in file_parent.experiments:
            exp = file_parent.add_experiment(experiment_name)
        else:
            exp = file_parent.experiments[experiment_name]

        exp.add_dataset("CW_Capture_Traces", traces, datatype="float32")
        exp.add_dataset("CW_Capture_Keys", keys, datatype="int8")
        exp.add_dataset("CW_Capture_Plaintexts", plaintexts, datatype="int8")
        exp.add_dataset("CW_Capture_Ciphertexts", ciphertexts, datatype="int8")
