from WPI_SCA_LIBRARY.CWScope import *

scope = CWScope("simpleserial-aes-CWLITEARM.hex")
scope.cw_to_file_format(1000, file_name="TestFile", experiment_name="CWCapture1")
