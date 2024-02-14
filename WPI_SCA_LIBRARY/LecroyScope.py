import time
import pyvisa as visa
import numpy as np
import chipwhisperer as cw
import regex as re
import serial.tools.list_ports
from serial import Serial
from serial.tools import list_ports


class LecroyScope(object):
    """
    Lecroy oscilloscope interface module. Use this class when collecting traces using a Lecroy scope.
    """

    def __init__(self, scope_ip='TCPIP0::192.168.1.79::inst0::INSTR'):
        """
        Initialize LecroyScope object.
        :param scope_ip: The scope IP of the Lecroy scope
        """
        self.scope = None
        self.rm = None
        self.scope_ip = scope_ip
        self.open(self.scope_ip)
        self.valid_trigger_states = ['AUTO', 'NORM', 'SINGLE', 'STOP']

    def __del__(self):
        self.close()

    def open(self, scope_ip, scope_timeout=5000):
        """
        Opens a Lecroy scope using the PyVisa library
        :param scope_ip: The ip of the Lecroy scope
        :param scope_timeout: The amount of time to wait for the Lecroy until timeout
        """
        self.rm = visa.ResourceManager()
        try:
            self.scope = self.rm.open_resource(scope_ip)
            self.reset()
            self.scope.timeout = scope_timeout
            self.scope.clear()
            self.scope.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        except IOError:
            self.scope = None
            print("Unable to locate the scope VISA interface")

    def close(self):
        """
        Closes the Lecroy scope using the PyVisa library
        :return:
        """
        try:
            if self.scope is not None:
                self.scope.close()
            if self.rm is not None:
                self.rm.close()
        except IOError:
            print("PyVisa error in closing resource")

    def setup(self, v_div, timebase, samplerate, duration, v_offset, channel):
        """
        Sets up the Lecroy scope for trace capture
        :param v_div: voltage scale per division
        :param timebase: the timescale for the scope
        :param samplerate: the rate in which measurements are sampled
        :param duration: the duration of capture
        :param v_offset: the voltage offset for the measurement
        :param channel: the channel to capture the traces on
        """
        if self.scope:
            self.scope.write("{}:TRA ON".format(channel))
            self.scope.write(r"""vbs 'app.Acquisition.ClearSweeps' """)
            self.scope.write("TDIV " + timebase)
            self.scope.write("{}:VDIV {}".format(channel, v_div))
            self.scope.write("CFMT DEF9,WORD,BIN")
            self.scope.write(r"""vbs 'app.Acquisition.Horizontal.Maximize = "FixedSampleRate" '""")
            self.scope.write(r"""vbs 'app.Acquisition.Horizontal.SampleRate = "%s" '""" % samplerate)
            self.scope.write(r"""vbs 'app.Acquisition.Horizontal.AcquisitionDuration = "%s" '""" % duration)
            self.scope.write(r"""vbs 'app.Acquisition.%s.VerOffset = "%s" '""" % (channel, v_offset))

    def set_trigger(self, delay, level, channel='C1'):
        """
        Set the trigger for the trace capture
        :param delay: the trigger delay
        :param level: the trigger level
        :param channel: the trigger channel
        """
        if self.scope is None:
            self.open(self.scope_ip)
        if self.scope:
            self.scope.write("{}:TRA ON".format(channel))
            self.scope.write("{}:TRCP DC".format(channel))
            self.scope.write("TRDL " + delay)
            self.scope.write("{}:TRLV {}".format(channel, level))
            self.scope.write("{}:TRSL POS".format(channel))

    def start_trigger(self):
        """
        Tells the LecroyScope to start the trigger based on the parameters set in LecroyScope.set_trigger
        """
        if self.scope:
            self.scope.write("TRMD SINGLE")
            self.scope.write(r"""vbs 'app.acquisition.triggermode = "stopped" ' """)
            self.scope.query(r"""vbs? 'return=app.WaitUntilIdle(.01)' """)
            self.scope.write(r"""vbs 'app.acquisition.triggermode = "single" ' """)
            self.scope.query(r"""vbs? 'return=app.WaitUntilIdle(.01)' """)

    def get_trigger(self):
        """
        Returns the trigger status
        :return: A string representing the trigger status
        """
        if self.scope is None:
            self.open(self.scope_ip)
        if self.scope:
            ret = self.scope.query("TRMD?")
            return ret.split()[1]

    def wait_for_trigger(self):
        """
        Waits for the Lecroy trigger
        :return: True if successful, False if the trigger timeout
        """
        if self.scope is None:
            self.open(self.scope_ip)

        if self.scope:
            for tries in range(10):
                if self.get_trigger() == 'STOP':
                    return True
                else:
                    time.sleep(0.5)
        print("Trigger timout!")
        return False

    def get_channel(self, samples, short, channel='C3'):
        """
        Get the measurement data from the Lecroy from specified channel
        :param samples: The number of samples to record
        :param short:
        :param channel: The channel to collect data from
        :return: The data from the scope
        """
        if self.scope is None:
            self.open(self.scope_ip)
        if self.scope:
            if short:
                self.scope.write('{0}:WF? DATA1'.format(channel))
                trc = self.scope.read_raw()
                hsh = trc.find(b'#', 0)
                skp = int(trc[hsh + 1:hsh + 2])
                trc = trc[hsh + skp + 2:-1]
                ret = np.frombuffer(trc, dtype='<h', count=samples)
                return ret
            else:
                self.scope.write('{0}:INSPECT? "SIMPLE"'.format(channel))
                trc = self.scope.read_raw()
                hsh = trc.find(b'\n', 0)
                trc = trc[hsh + 2:-1]
                text = str(trc)
                float_pattern = r'-?\d+\.\d*(?:[eE][-+]?\d+)?'
                matches = re.findall(float_pattern, text)
                float_list = [float(match) for match in matches]
                return float_list
        else:
            return None

    def reset(self):
        """
        Resets the scope
        """
        if self.scope is not None:
            print("Resetting oscilloscope!")
            time.sleep(1)
            not_ready = True
            while not_ready:
                ret = self.scope.query("INR?")
                ret = ret.split()[1]
                not_ready = (0x01 == ((int(ret) >> 13) & 0x01))
                time.sleep(0.5)
        return


def scope_setup(channel='C3', trig_channel='C1', num_of_samples=200, sample_rate=500E6, short=False, v_div=2.5E-3, trg_delay="0",
                trg_level="1.65V", v_offset='0'):
    """
    Sets up a Lecroy Scope object for power trace collection
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
    """
    xscale = 1 / sample_rate
    duration = xscale * num_of_samples

    if short:
        y_scale = v_div / (65536 / 10.0)
    else:
        y_scale = 1

    timebase = str(xscale * num_of_samples / 10) + "S"
    scope = LecroyScope()
    scope.setup(str(v_div) + "V", timebase, str(sample_rate / 1E6) + "MS/s", str(duration) + "S", v_offset, channel)
    scope.set_trigger(trg_delay, trg_level, trig_channel)
    return scope


def dut_setup(board="CW305", fpga_id='100t', bitfile=None):
    """
    Sets up a target board for trace capture
    :param board: The DUT type (CW305 or pico)
    :param fpga_id: the FPGA id for CW305 target
    :param bitfile: the bitfile for CW305 target
    :return: The configured target
    """
    if board == "CW305":
        target = cw.target(None, cw.targets.CW305, fpga_id=fpga_id, force=True, bsfile=bitfile)
        target.pll.pll_enable_set(True)
        target.pll.pll_outenable_set(False, 0)
        target.pll.pll_outenable_set(True, 1)
        target.pll.pll_outenable_set(False, 2)
        target.pll.pll_outfreq_set(100E6, 1)
        return target
    elif board == "pico":
        port_list = list(serial.tools.list_ports.comports())
        print(port_list)
        if len(port_list) == 0:
            print('No Available Serial Port')
        else:
            for i in range(0, len(port_list)):
                print(port_list[i])
        comports = []
        for x in list_ports.comports():
            cp = Serial()
            cp.port = x[0]
            comports.append(cp)
        print(comports)
        serialPort = 'COM3'
        serialBaud = 115200
        print('Trying to connect to ' + str(serialPort) +
              ' at ' + str(serialBaud) + ' BAUD.')
        try:
            ser = serial.Serial(serialPort, serialBaud, timeout=4)
            return ser
        except IOError:
            print("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')


def capture_cw305(scope, target, num_of_samples=600, short=False, channel='C3', plaintext=None, key=None):
    """
    Captures traces on the CW305 target board
    :param scope: The configured LecroyScope object
    :param target: The configured CW305 target board
    :param num_of_samples: The number of samples to capture
    :param short:
    :param channel: The channel to collect traces on
    :param plaintext: The plaintext for the encryption algorithm
    :param key: The key for the encryption algorithm
    :return: the recorded trace and algorithm output
    """

    if key is None:
        key = [0]
    if plaintext is None:
        plaintext = [0]

    if scope.start_trigger() is not False:
        target.fpga_write(target.REG_CRYPT_KEY, key[::-1])
        target.fpga_write(target.REG_CRYPT_TEXTIN, plaintext[::-1])
        target.usb_trigger_toggle()

        if scope.wait_for_trigger() is False:
            return None, [0]

        trc = scope.get_channel(num_of_samples, short, channel)

        output = target.fpga_read(target.REG_CRYPT_CIPHEROUT, 16)

        return trc, output

    else:
        raise Exception("Trigger Error!")


def capture_nopt(scope, num_of_samples=600, short=False, channel='C3'):
    """
    Captures traces with no input
    :param scope: the configured LecroyScope object
    :param num_of_samples: The number of samples to capture
    :param short:
    :param channel: The channel to collect traces on
    :return: The resulting trace
    """
    if scope.start_trigger() is not False:
        if scope.wait_for_trigger() is False:
            return
        trc = scope.get_channel(num_of_samples, short, channel)
        return trc
    else:
        raise Exception("Trigger Error!")


def capture_pico(scope, ser, num_of_samples=600, short=False, channel='C3', plain_text=None):

    if plain_text is None:
        plain_text = [0]

    ser.write([82])
    print('Send soft reset(R) to clear variables')
    Ack = ser.read(1)
    print('Acknowledgement(A) from DUT:', Ack)
    print('plaintext', bytearray(plain_text))

    if scope.start_trigger() is False:
        print("Triggering Error!")
        return
    ser.write(plain_text)

    if scope.wait_for_trigger() is False:
        return

    trc = scope.get_channel(num_of_samples, short, channel)
    ciphertext = bytearray(ser.read(2))
    print('AES Sbox output', ciphertext)

    return trc
