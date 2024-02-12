import time
import logging
import pyvisa as visa
import numpy as np
import chipwhisperer as cw
import regex as re
import serial.tools.list_ports
from serial import Serial
from serial.tools import list_ports


class Scope(object):

    def __init__(self):
        self.open()
        self.valid_trigger_states = ['AUTO', 'NORM', 'SINGLE', 'STOP']

    def __del__(self):
        self.close()

    def open(self):
        #  get all resources connected to PC
        self.rm = visa.ResourceManager()
        #  open vcip protocol
        try:
            self.scope = self.rm.open_resource('TCPIP0::192.168.1.79::inst0::INSTR')  # insert your scope IP here
            self.reset()
            self.scope.timeout = 5000
            self.scope.clear()
            r = self.scope.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        except:
            self.scope = None
            logging.info("Unable to locate the scope VISA interface")

    def close(self):
        # disconnect the oscilloscope
        # there is a bug in the pyvisa impl. so we'll wrap in
        # a try/catch
        try:
            if (self.scope is not None):
                self.scope.close()

            if (self.rm is not None):
                self.rm.close()

        except:
            logging.info("pyvisa error in closing resource")

    # Set up for a certain trace acquisition process --- Si 2017.12.5 Added
    # vdiv:         vertical resolution (V/div)
    # timebase:     horizontal resolution (S/div)
    # samplerate:   Fixed sample rate (Sa/s)
    # duration:     Measure Duration (usually set as 10*timebase, might not work otherwise)
    # voffset:      Vertical offset
    def setup(self, vdiv, timebase, samplerate, duration, voffset):
        # setup for the trace acquisition
        # set time base
        if (self.scope):
            self.scope.write("C3:TRA ON")
        if (self.scope):
            self.scope.write(r"""vbs 'app.Acquisition.ClearSweeps' """)  # clear
        if (self.scope):
            self.scope.write("TDIV " + timebase)
        if (self.scope):
            self.scope.write("C3:VDIV " + vdiv)
        # set waveform format
        if (self.scope):
            self.scope.write("CFMT DEF9,WORD,BIN")
        # set Sampling Rate
        if (self.scope):
            self.scope.write(r"""vbs 'app.Acquisition.Horizontal.Maximize = "FixedSampleRate" '""")
            self.scope.write(r"""vbs 'app.Acquisition.Horizontal.SampleRate = "%s" '""" % samplerate)
            self.scope.write(r"""vbs 'app.Acquisition.Horizontal.AcquisitionDuration = "%s" '""" % duration)
            self.scope.write(r"""vbs 'app.Acquisition.C3.VerOffset = "%s" '""" % voffset)

    # Set up trigger condition
    # delay: negative means start acuisition at post trigger xx s; positive shows the percent of trace before trigger
    # level: the level of trigger which counts as one valid trace
    def set_trigger(self, delay, level):
        # set trigger mod to single
        if (None == self.scope):
            self.open()
        # set trigger delay9

        if (self.scope):
            self.scope.write("C1:TRA ON")
        if (self.scope):
            self.scope.write("C1:TRCP DC")
        if (self.scope):
            self.scope.write("TRDL " + delay)
        # set trigger level
        if (self.scope):
            self.scope.write("C1:TRLV " + level)
        # set triggr positive edge
        if (self.scope):
            self.scope.write("C1:TRSL POS")

    # Stop the previous capture and start a new one
    def start_trigger(self):
        # set trigger state
        if (self.scope):
            self.scope.write("TRMD SINGLE")  # Used for single waveform capture. To save querying time
            # stop
            self.scope.write(r"""vbs 'app.acquisition.triggermode = "stopped" ' """)
            r = self.scope.query(r"""vbs? 'return=app.WaitUntilIdle(.01)' """)
            self.scope.write(r"""vbs 'app.acquisition.triggermode = "single" ' """)
            r = self.scope.query(r"""vbs? 'return=app.WaitUntilIdle(.01)' """)

    # get the triggering status
    def get_trigger(self):
        # read trigger state from the oscilloscope
        if (None == self.scope):
            self.open()

        if (self.scope):
            ret = self.scope.query("TRMD?")
            return ret.split()[1]

    # check whether Lecroy has already been triggered
    # This is poor-mans timeout. There
    # doesn't seem to be a good platform independant
    # way to raise a timeout exception so this will
    # have to do
    # wait untill the trigger is activated and the capture stops
    def wait_for_trigger(self):
        if (None == self.scope):
            self.open()

        if (self.scope):
            for tries in range(10):
                if (self.get_trigger() == 'STOP'):
                    return True
                else:
                    time.sleep(0.5)

        print("Trigger timout")
        return False

    # Read one trace back
    # samples: number of samples on that trace
    # isshort: short or float

    def get_channel(self, samples, isshort, channel='C3'):
        # read channel data
        if (None == self.scope):
            self.open()
        if (self.scope):
            if (isshort):
                cmd = self.scope.write('{0}:WF? DATA1'.format(channel))
                trc = self.scope.read_raw()
                # print(trc)
                hsh = trc.find(b'#', 0)
                skp = int(trc[hsh + 1:hsh + 2])
                trc = trc[hsh + skp + 2:-1]
                # et = np.fromstring(trc, dtype='<h', count=samples)
                # ret = np.fromstring(trc, dtype='<h', count=samples)
                ret = np.frombuffer(trc, dtype='<h', count=samples)
                return ret
            else:
                cmd = self.scope.write('{0}:INSPECT? "SIMPLE"'.format(channel))
                trc = self.scope.read_raw()
                #             print(f"trc_raw = {trc}" )
                hsh = trc.find(b'\n', 0)
                #             print(hsh)
                trc = trc[hsh + 2:-1]
                #             trcs = trc.strip("\n\r")
                #             print(f"trc = {trc}")

                #             ret = np.fromstring(trc, dtype='float', sep=' ', count=samples)
                #             ret = np.frombuffer(trc, dtype='float', count = -1)
                #             return trc

                text = str(trc)

                # Match floating-point numbers with an optional negative sign, optional decimal part, and optional exponent part
                float_pattern = r'-?\d+\.\d*(?:[eE][-+]?\d+)?'

                # Find all matches of the float pattern in the text
                matches = re.findall(float_pattern, text)

                float_list = [float(match) for match in matches]

                return float_list


        else:
            return None

    def reset(self):  # reset the ocssiloscope
        if (self.scope is not None):

            logging.info("resetting oscilloscope!")
            #         self.scope.write("*RCL 6") # Reseting the set panel to 6.

            time.sleep(1)
            not_ready = True

            while (not_ready):
                ret = self.scope.query("INR?")
                ret = ret.split()[1]
                not_ready = (0x01 == ((int(ret) >> 13) & 0x01))
                time.sleep(0.5)

        return


# Scope setup function to initilise Lecroy. Please setup the IP address in the Scope.open() method above
# look for this statement: self.scope = self.rm.open_resource('TCPIP0::192.168.1.79::inst0::INSTR')

def scope_setup(trig_channel='C1', num_of_samples=200, sample_rate=500E6, isshort='False', vdiv=2.5E-3, trg_delay="0",
                trg_level="1.65V", voffset='0'):
    # Acquisition setup: find this setting through the capturing traces from the setup program
    # num_of_traces=10000                                          # number of traces
    # num_of_samples=600                                      # number of samples
    # sample_rate=10E9                                           # Sample Rate
    # isshort=False                                             # Type of the samples: short or float
    # vdiv=2.5E-3 #1.8E-2                                                 # Vertical resolution: V/div
    # trg_delay ="0"# "-311.2US"                                      # Trigger delay: negative means post trigger (S)
    # trg_level = "1.65V"                                            # Trigger level: start capture when trigger passes it
    # #isenc = True                                                # Perform encryption/decryption
    # voffset="0"#"-11.4 mV"                                          # Vertical Offset

    # In most common cases, you do not have to change anything below this line
    # Compute the setup parameters from above
    xscale = 1 / sample_rate  # sampling interval (s)
    duration = xscale * num_of_samples  # sample duration (s)
    # For short type of acquisition, the captured trace is scaled in order to store in a 16 bit integer
    # yscale saves the scale value, in case you need to reconstruct the real traces
    # For float type of acquisition, the samples are exactly the real samples on the trace, so yscale=1
    if (isshort):
        yscale = vdiv / (65536 / 10.0)
        print("isshort")
    else:
        yscale = 1
        print("False")
    timebase = str(xscale * num_of_samples / 10) + "S"  # timebase: s/div

    # Open scope
    oscope = Scope()
    # setup the scope
    oscope.setup(str(vdiv) + "V", timebase, str(sample_rate / 1E6) + "MS/s", str(duration) + "S", voffset)
    # set trigger
    oscope.set_trigger(trg_delay, trg_level)
    return oscope


# DUT setup for communication start and bit stream program for CW305 and Picochip
def dut_setup(board="CW305", key=[0], bitfile=None):
    if (board == "CW305"):
        target = cw.target(None, cw.targets.CW305, fpga_id='35t', force=True, bsfile=bitfile)

        # Configuration of the PLL Clocks
        target.pll.pll_enable_set(True)  # Enable PLL chip
        target.pll.pll_outenable_set(False, 0)  # Disable unused PLL0
        target.pll.pll_outenable_set(True, 1)  # Enable PLL
        target.pll.pll_outenable_set(False, 2)  # Disable unused PLL2
        # set PLL 0 to 10MHz
        target.pll.pll_outfreq_set(100E6, 1)

        return target
    elif (board == "pico"):
        # -------------- Serial object -----------------
        port_list = list(serial.tools.list_ports.comports())
        print(port_list)
        if len(port_list) == 0:
            print('No Available Serial Port')
        else:
            for i in range(0, len(port_list)):
                print(port_list[i])

        # ----------------------------------------------
        comports = []
        for x in list_ports.comports():
            cp = Serial()
            cp.port = x[0]
            comports.append(cp)
        print(comports)
        # ---------------------------------------------
        serialPort = 'COM3'  # '/dev/ttyUSB2'#
        serialBaud = 115200

        # Connect to serial port
        print('Trying to connect to ' + str(serialPort) +
              ' at ' + str(serialBaud) + ' BAUD.')
        try:
            ser = serial.Serial(serialPort, serialBaud, timeout=4)
            print('Connected!')
        except:
            print("Failed to connect with " + str(serialPort) +
                  ' at ' + str(serialBaud) + ' BAUD.')
    # ----------------------------------------------
    return ser


# Capture single trace
def capture_cw305(oscope, target, num_of_samples=600, isshort=False, channel='C3', board="CW305", plain_text=[0],
                  key=[0]):
    if (oscope.start_trigger() == False):
        print("Triggering Error!")
        return

    target.fpga_write(target.REG_CRYPT_KEY, key[::-1])  # write key
    target.fpga_write(target.REG_CRYPT_TEXTIN, plain_text[::-1])  # write plaintext
    target.usb_trigger_toggle()

    # Get trace: if Lecroy has not stopped yet, discard this trace
    if (oscope.wait_for_trigger() == False):
        return None, [0]

    trc = oscope.get_channel(num_of_samples, isshort, channel)  # Capture trace

    output = target.fpga_read(target.REG_CRYPT_CIPHEROUT, 16)  # read ciphertext
    return trc, output


# Capture without sending the inputs
def capture_nopt(oscope, num_of_samples=600, isshort=False, channel='C3'):
    if (oscope.start_trigger() == False):
        print("Triggering Error!")
        return

    # Get trace: if Lecroy has not stopped yet, discard this trace
    if (oscope.wait_for_trigger() == False):
        # i=i-1;
        # continue;
        return

    trc = oscope.get_channel(num_of_samples, isshort, channel)
    return trc


# Capture for Picochip board
def capture_pico(oscope, ser, num_of_samples=600, isshort=False, channel='C3', plain_text=[0]):
    ser.write([82])
    print('Send soft reset(R) to clear variables')
    Ack = ser.read(1)
    print('Acknowledgement(A) from DUT:', Ack)

    print('plaintext', bytearray(plain_text))

    if (oscope.start_trigger() == False):
        print("Triggering Error!")
        return
    ser.write(plain_text)

    # Get trace: if Lecroy has not stopped yet, discard this trace
    # for i in range(10):
    if (oscope.wait_for_trigger() == False):
        # i=i-1;
        # continue;
        return

    trc = oscope.get_channel(num_of_samples, isshort, channel)
    ciphertext = bytearray(ser.read(2))
    print('AES sbox output', ciphertext)

    return trc
