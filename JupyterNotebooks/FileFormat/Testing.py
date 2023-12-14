from testTime import HDF5FileClass
import testTime
import h5py
'''
with h5py.File('ATMega8515_raw_traces.h5', 'r') as f:
    print("Keys: %s" % f.keys())
    a_group_key = list(f.keys())[0]
    b_group_key = list(f.keys())[1]

    for k in f[a_group_key].attrs.keys():
        print(f"{k} => {f[a_group_key].attrs[k]}")

    # get the object type for a_group_key: usually group or dataset
    fileClass = HDF5FileClass("test_output_55.hdf5")
    fileClass.addExperiment("experimentOne")
    experimentOne = fileClass.experiments["experimentOne"]
    experimentOne.addDataset("plaintext", (60000, 16), definition="Plaintext Input To the Algorithem", dtype='uint16')
    plaintextDataset = experimentOne.dataset["plaintext"]
    experimentOne.addDataset("ciphertext", (60000, 16), definition="Ciphertext Input To the Algorithem", dtype='uint16')
    ciphertextDataset = experimentOne.dataset["ciphertext"]
    experimentOne.addDataset("key", (60000, 16), definition="Key Input To the Algorithem", dtype='uint16')
    keyDataset = experimentOne.dataset["key"]
    experimentOne.addDataset("mask", (60000, 16), definition="Mask Input To the Algorithem", dtype='uint16')
    maskDataset = experimentOne.dataset["mask"]
    print("Beginging making dataset")
    experimentOne.addDataset("traces", (60000,100000), definition="Traces of the algorithem", dtype= 'int16')
    tracesDataset = experimentOne.dataset["traces"]
    print("Done making dataset")



    for i in range(60000):
        plaintextDataset.addData(i, f[a_group_key][i][0])
        ciphertextDataset.addData(i, f[a_group_key][i][1])
        keyDataset.addData(i, f[a_group_key][i][2])
        tracesDataset.datasetPath[i] = f[b_group_key][i]
        print(i)



'''
with h5py.File('test_output_55.hdf5', "a") as data_file:
    fileClass = HDF5FileClass('test_output_55.hdf5',fileInputType="existing", data_file=data_file)
    print(fileClass.experiments)
    expOne = fileClass.experiments['experimentOne']
    print(expOne.dataset)
    ciphertext = expOne.dataset['ciphertext']
    print(ciphertext.readData(1))