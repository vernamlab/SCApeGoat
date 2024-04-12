Oscilloscope Interface
======================

Researchers at WPI and across the country use ChipWhisperer devices to conduct
side-channel analysis research. ChipWhisperer has an existing library developed to
interface with their devices. However, this library was improved upon by providing
higher-level API calls

.. class:: CWScope

    Initializes the scope object...

    .. method:: __init__

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

    .. method::

        Capture procedure for ChipWhisperer devices. Will return a specified number
        of traces and the data associated with the collection.
