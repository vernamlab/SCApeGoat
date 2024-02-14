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
            if self.scope is not None:
                self.scope.close()

            if self.rm is not None:
                self.rm.close()

        except:
            logging.info("pyvisa error in closing resource")

    def setup(self, vdiv, timebase, samplerate, duration, voffset):
        # setup for the trace acquisition
        # set time base
        if self.scope:
            self.scope.write("C3:TRA ON")
        if self.scope:
            self.scope.write(r"""vbs 'app.Acquisition.ClearSweeps' """)  # clear
        if self.scope:
            self.scope.write("TDIV " + timebase)
        if self.scope:
            self.scope.write("C3:VDIV " + vdiv)
        if self.scope:
            self.scope.write("CFMT DEF9,WORD,BIN")
        if self.scope:
            self.scope.write(r"""vbs 'app.Acquisition.Horizontal.Maximize = "FixedSampleRate" '""")
            self.scope.write(r"""vbs 'app.Acquisition.Horizontal.SampleRate = "%s" '""" % samplerate)
            self.scope.write(r"""vbs 'app.Acquisition.Horizontal.AcquisitionDuration = "%s" '""" % duration)
            self.scope.write(r"""vbs 'app.Acquisition.C3.VerOffset = "%s" '""" % voffset)

    def set_trigger(self, delay, level):
        if self.scope is None:
            self.open()
        if self.scope:
            self.scope.write("C1:TRA ON")
        if self.scope:
            self.scope.write("C1:TRCP DC")
        if self.scope:
            self.scope.write("TRDL " + delay)
        if self.scope:
            self.scope.write("C1:TRLV " + level)
        if self.scope:
            self.scope.write("C1:TRSL POS")

    def start_trigger(self):
        if self.scope:
            self.scope.write("TRMD SINGLE")
            self.scope.write(r"""vbs 'app.acquisition.triggermode = "stopped" ' """)
            r = self.scope.query(r"""vbs? 'return=app.WaitUntilIdle(.01)' """)
            self.scope.write(r"""vbs 'app.acquisition.triggermode = "single" ' """)
            r = self.scope.query(r"""vbs? 'return=app.WaitUntilIdle(.01)' """)

    def get_trigger(self):
        if self.scope is None:
            self.open()
        if self.scope:
            ret = self.scope.query("TRMD?")
            return ret.split()[1]

    def wait_for_trigger(self):
        if self.scope is None:
            self.open()

        if self.scope:
            for tries in range(10):
                if self.get_trigger() == 'STOP':
                    return True
                else:
                    time.sleep(0.5)
        print("Trigger timout")
        return False

    def get_channel(self, samples, isshort, channel='C3'):
        # read channel data
        if self.scope is None:
            self.open()
        if self.scope:
            if isshort:
                cmd = self.scope.write('{0}:WF? DATA1'.format(channel))
                trc = self.scope.read_raw()
                hsh = trc.find(b'#', 0)
                skp = int(trc[hsh + 1:hsh + 2])
                trc = trc[hsh + skp + 2:-1]
                ret = np.frombuffer(trc, dtype='<h', count=samples)
                return ret
            else:
                cmd = self.scope.write('{0}:INSPECT? "SIMPLE"'.format(channel))
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
        if self.scope is not None:
            logging.info("resetting oscilloscope!")
            time.sleep(1)
            not_ready = True
            while not_ready:
                ret = self.scope.query("INR?")
                ret = ret.split()[1]
                not_ready = (0x01 == ((int(ret) >> 13) & 0x01))
                time.sleep(0.5)
        return


def scope_setup(trig_channel='C1', num_of_samples=200, sample_rate=500E6, isshort='False', vdiv=2.5E-3, trg_delay="0",
                trg_level="1.65V", voffset='0'):
    xscale = 1 / sample_rate  # sampling interval (s)
    duration = xscale * num_of_samples  # sample duration (s)
    if (isshort):
        yscale = vdiv / (65536 / 10.0)
        print("isshort")
    else:
        yscale = 1
        print("False")
    timebase = str(xscale * num_of_samples / 10) + "S"  # timebase: s/div
    oscope = Scope()
    oscope.setup(str(vdiv) + "V", timebase, str(sample_rate / 1E6) + "MS/s", str(duration) + "S", voffset)
    oscope.set_trigger(trg_delay, trg_level)
    return oscope


def dut_setup(board="CW305", key=[0], bitfile=None):
    if board == "CW305":
        target = cw.target(None, cw.targets.CW305, fpga_id='100t', force=True, bsfile=bitfile)
        target.pll.pll_enable_set(True)  # Enable PLL chip
        target.pll.pll_outenable_set(False, 0)  # Disable unused PLL0
        target.pll.pll_outenable_set(True, 1)  # Enable PLL
        target.pll.pll_outenable_set(False, 2)  # Disable unused PLL2
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
        serialPort = 'COM3'  # '/dev/ttyUSB2'#
        serialBaud = 115200
        print('Trying to connect to ' + str(serialPort) +
              ' at ' + str(serialBaud) + ' BAUD.')
        try:
            ser = serial.Serial(serialPort, serialBaud, timeout=4)
            print('Connected!')
        except:
            print("Failed to connect with " + str(serialPort) +
                  ' at ' + str(serialBaud) + ' BAUD.')
    return ser


# Capture single trace
def capture_cw305(oscope, target, num_of_samples=600, isshort=False, channel='C3', board="CW305", plain_text=[0],
                  key=[0]):
    if oscope.start_trigger() == False:
        print("Triggering Error!")
        return

    target.fpga_write(target.REG_CRYPT_KEY, key[::-1])  # write key
    target.fpga_write(target.REG_CRYPT_TEXTIN, plain_text[::-1])  # write plaintext
    target.usb_trigger_toggle()

    if oscope.wait_for_trigger() == False:
        return None, [0]

    trc = oscope.get_channel(num_of_samples, isshort, channel)  # Capture trace

    output = target.fpga_read(target.REG_CRYPT_CIPHEROUT, 16)  # read ciphertext
    return trc, output


def capture_nopt(oscope, num_of_samples=600, isshort=False, channel='C3'):
    if oscope.start_trigger() == False:
        print("Triggering Error!")
        return

    # Get trace: if Lecroy has not stopped yet, discard this trace
    if oscope.wait_for_trigger() == False:
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

    if oscope.start_trigger() == False:
        print("Triggering Error!")
        return
    ser.write(plain_text)

    # Get trace: if Lecroy has not stopped yet, discard this trace
    # for i in range(10):
    if oscope.wait_for_trigger() == False:
        # i=i-1;
        # continue;
        return

    trc = oscope.get_channel(num_of_samples, isshort, channel)
    ciphertext = bytearray(ser.read(2))
    print('AES sbox output', ciphertext)

    return trc
