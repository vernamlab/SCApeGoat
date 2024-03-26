import matplotlib.pyplot as plt
from WPI_SCA_LIBRARY.DPA import *

traces = np.load("TestFile//Experiments//CWCapture1//CWCapture1Traces.npy")
ciphertext = np.load("TestFile//Experiments//CWCapture1//CWCapture1Ciphertexts.npy")
plaintext = np.load("TestFile//Experiments//CWCapture1//CWCapture1Plaintexts.npy")

cpaoutput, guess_corr, guess = calculate_dpa(traces, plaintext, order=2, window_size_dpa=20, num_of_traces=100)
print(traces.shape)
print(cpaoutput.shape)

plt.plot(cpaoutput,'black')
up = np.zeros(len(cpaoutput))
up.fill(0.004)
down = np.zeros(len(cpaoutput))
down.fill(-0.004)
plt.plot(up,'r')
plt.plot(down,'r')
plt.show()