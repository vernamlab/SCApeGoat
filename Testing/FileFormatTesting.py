from WPI_SCA_LIBRARY.CWScope import *

# scope = CWScope("simpleserial-aes-CWLITEARM.hex")
# scope.cw_to_file_format(1000, file_name="TestFile", experiment_name="CWCapture1")

# create parent folder
file_parent = FileFormatParent("TestFile", existing=True)

# add experiment
exp = file_parent.experiments["CWCapture1"]
print(exp.dataset["CWCapture1Traces"].readAll())
