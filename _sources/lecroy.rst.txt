Lecroy Oscilloscope Interface
=============================

.. class:: LecroyScope

    .. method:: __init__(self, scope_ip='TCPIP0::192.168.1.79::inst0::INSTR'):

        Create a LecroyScope object

        :param scope_ip: The IP of the scope that you want to connect to

    .. method:: __del__(self):

        Close the scope on object deletion.

        :return: None

    .. method:: open(self, scope_ip, scope_timeout=5000):

        Opens a Lecroy scope using the PyVisa library

        :param scope_ip: The ip of the Lecroy scope
        :param scope_timeout: The amount of time to wait for the Lecroy until timeout
        :return: None

    .. method:: close(self):

        Closes the Lecroy scope using the PyVisa library

        :return: None

    .. method:: setup(self, v_div, timebase, samplerate, duration, v_offset, channel):

        Sets up the Lecroy scope for trace capture

        :param v_div: voltage scale per division
        :param timebase: the timescale for the scope
        :param samplerate: the rate in which measurements are sampled
        :param duration: the duration of capture
        :param v_offset: the voltage offset for the measurement
        :param channel: the channel to capture the traces on
        :return: None

    .. method:: set_trigger(self, delay, level, channel='C1'):

        Set the trigger for the trace capture

        :param delay: the trigger delay
        :param level: the trigger level
        :param channel: the trigger channel
        :return: None


    .. method:: start_trigger(self)

        Tells the LecroyScope to start the trigger based on the parameters set in LecroyScope.set_trigger


    .. method:: get_trigger(self):

        Returns the trigger status

        :return: A string representing the trigger status

    .. method:: wait_for_trigger(self):

        Waits for the Lecroy trigger

        :return: True if successful, False if the trigger timeout

    .. method:: get_channel(self, samples, short, channel='C3'):

        Get the measurement data from the Lecroy from specified channel

        :param samples: The number of samples to record
        :param short:
        :param channel: The channel to collect data from
        :return: The data from the scope

    .. method:: reset(self):

        Resets the scope

    .. method:: scope_setup(channel='C3', trig_channel='C1', num_of_samples=200, sample_rate=500E6, short=False, v_div=2.5E-3, trg_delay="0", trg_level="1.65V", v_offset='0'):

        Higher level setup function. Sets up a Lecroy Scope object for power trace collection.

        :param channel: the channel that records power trace measurements
        :param trig_channel: the trigger channel
        :param num_of_samples: the number of samples to capture
        :param sample_rate: the rate in which samples are captured
        :param short:
        :param v_div: the voltage scale per division
        :param trg_delay: the trigger delay
        :param trg_level: the trigger level
        :param v_offset: the voltage offset
        :return: the fully configured scope object

    .. method:: dut_setup(board="CW305", fpga_id='100t', bitfile=None)

        Sets up a target board for trace capture
        :param board: The DUT type (CW305 or pico)
        :param fpga_id: the FPGA id for CW305 target
        :param bitfile: the bitfile for CW305 target
        :return: The configured target


    .. method:: capture_cw305(scope, target, num_of_samples=600, short=False, channel='C3', plaintext=None, key=None):

        Captures traces on the CW305 target board

        :param scope: The configured LecroyScope object
        :param target: The configured CW305 target board
        :param num_of_samples: The number of samples to capture
        :param short:
        :param channel: The channel to collect traces on
        :param plaintext: The plaintext for the encryption algorithm
        :param key: The key for the encryption algorithm
        :return: the recorded trace and algorithm output
