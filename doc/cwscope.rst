Oscilloscope Interface
======================

Researchers at WPI and across the country use ChipWhisperer devices to conduct
side-channel analysis research. ChipWhisperer has an existing library developed to
interface with their devices. However, this library was improved upon by providing
higher-level API calls

.. class:: CWScope

    .. method:: __init__(self, firmware_path: str, gain: int = 25, num_samples: int = 5000, offset: int = 0, target_type: any = cw.targets.SimpleSerial, target_programmer: any = cw.programmers.STM32FProgrammer) -> None:

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

    .. method:: disconnect(self)

        Disconnect CW Scope and Target

    .. method:: standard_capture_traces(self, num_traces: int, experiment_keys: np.ndarray = None, experiment_texts: np.ndarray = None, fixed_key: bool = True, fixed_pt: bool = False) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray):

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
