import time

import h5py
import numpy as np
import trsfile

sampleNumber = 509000

''''' with h5py.File(filename, "r") as f:
    # Print all root level object names (aka keys)
    # these can be group or dataset names
    print("Keys: %s" % f.keys())
    Attack_traces = (list(f.keys())[1])
    goodStuff = f[Attack_traces]

    print(goodStuff)
    print(goodStuff.keys())
    labels = (list(goodStuff.keys())[1])
    gooderStuff = goodStuff[labels]
    print(gooderStuff[0])
    print(gooderStuff[1])
    #gooderStuff is a dataset '''


class HDF5FileClass:
    def __init__(self, path, fileInputType="undefined", data_file=0):
        if fileInputType == "existing":
            self.path = path

            self.hdf5Object = data_file
            self.experiments = {}
            self.metadata = {}
            # check for and add experiments
            for attIndex in list(self.hdf5Object.attrs.keys()):
                self.metadata[attIndex] = self.hdf5Object.attrs[attIndex]

            for key in list(data_file.keys()):
                self.addExperiment(key, existing=1, groupPath=data_file[key], definition=self.metadata[f'{key}_experiment_description'])

        if fileInputType == "undefined":
            self.path = path
            self.hdf5Object = h5py.File(path, 'w')
            self.experiments = {}
            self.metadata = {}
        elif fileInputType == "trs":
            with trsfile.open(path, 'r') as traces:
                # create experiment and main file
                path = path.replace(".trs", ".hdf5", 1)
                self.experiments = {}
                self.metadata = {}
                self.hdf5Object = h5py.File(path, 'a', rdcc_nbytes=2060000000)
                self.addExperiment("ExperimentOne", self.hdf5Object)

                # add hdf5 metadata
                for header, value in traces.get_headers().items():
                    print(header, '=', value)
                    if isinstance(value, str) or isinstance(value, int):
                        self.experiments["ExperimentOne"].addMetadata(header.name, value)
                print(self.experiments["ExperimentOne"].metadata)

                # add dataset
                experiment = self.experiments["ExperimentOne"]
                experiment.addDataset("traces", experiment.groupPath)
                tracesDataset = experiment.dataset["traces"]

                start = time.perf_counter()
                for i, trace in enumerate(traces[0:sampleNumber]):
                    tracesDataset.addData(i, trace[:])
                # traceData = traces[1]
                # traceData = traceData[:]
                # for i in range(sampleNumber):
                #     tracesDataset.addData(i,traceData)
                print(time.perf_counter() - start)

        elif fileInputType == "WPI_lab":
            with h5py.File(path, "a") as data_file:
                print("you tried")

            ''' self.path = path
            self.hdf5Object = h5py.File(path, 'w')
            self.experiments = {}
            self.metadata = {}'''

    def addExperiment(self, experimentName, existing=0, groupPath=0, definition=""):
        self.experiments[experimentName] = ExperimentClass(experimentName, self.hdf5Object, existing, groupPath, definition = definition)
        self.addMetadata(f'{experimentName}_experiment_description', definition)

    def getMetadata(self):
        return self.metadata

    def addMetadata(self, metadataName, metadataContents):
        self.metadata[metadataName] = metadataContents
        self.hdf5Object.attrs[metadataName] = metadataContents

    def getExperimentDefinitions(self):
        definitionReturn = {}
        for key in self.experiments.keys():
            definition = self.metadata[f'{key}_experiment_description']
            definitionReturn[key] = definition
        return definitionReturn

    def redefine(self, experimentName, newDefinition):
        self.addMetadata(f'{experimentName}_experiment_description', newDefinition)



class ExperimentClass:
    def __init__(self, experimentName, hdf5Object, existing=0, groupPath=0, definition = ""):
        self.hdf5Object = hdf5Object
        self.dataset = {}
        self.metadata = {}
        self.definition = definition
        if existing == 0:
            self.groupPath = hdf5Object.create_group(experimentName)
        else:
            # set group path
            self.groupPath = groupPath

            for attIndex in list(self.groupPath.attrs.keys()):
                self.metadata[attIndex] = self.groupPath.attrs[attIndex]
            # create datasets from what is present
            for datasetID in list(self.groupPath.keys()):
                self.addDataset(datasetID, 0, 0, definition=self.groupPath.attrs[f'{datasetID}_dataset_description'],
                                existing=1, datasetPathIn=self.groupPath[datasetID])

    def prepareSnrWithLabels(self, tracesName, labelsName, size):
        tracesClass = self.dataset[tracesName]
        labelsClass = self.dataset[labelsName]
        traces = tracesClass.readData(range(size))
        labels = labelsClass.readData(range(size))

        labelsUnique = np.unique(labels)
        # initialize the dictionary
        sortedLabels = {}
        for i in labelsUnique:
            sortedLabels[i] = []

        for index, label in enumerate(labels):
            sortedLabels[label[0]].append(traces[index])
        return sortedLabels, labelsUnique

    def addMetadata(self, metadataName, metadataContents):
        self.metadata[metadataName] = metadataContents
        self.groupPath.attrs[metadataName] = metadataContents

    def deleteMetadata(self, metadataName):
        self.groupPath.attrs.pop(metadataName)
        self.metadata.pop(metadataName)

    def handleDatasetRename(self, oldDatasetName, newDatasetName):
        stringHolderOld = f'{oldDatasetName}_dataset_description'
        stringHolderNew = f'{newDatasetName}_dataset_description'
        definition = self.metadata[stringHolderOld]
        self.deleteMetadata(stringHolderOld)
        self.addMetadata(stringHolderNew, definition)
        self.dataset[newDatasetName] = self.dataset.pop(oldDatasetName)

    def readAll(self, index):
        keys = {}
        values = []
        keyIndex = 0
        for key in self.dataset.keys():
            keys[key] = keyIndex
            values.append(self.dataset[key].readData(index))
            keyIndex = keyIndex + 1
        return keys, values

    def getDatasetNames(self):
        return self.dataset.keys()

    def getSpecifiedDatasets(self, datasets, index):
        keys = {}
        values = []
        keyIndex = 0
        for key in datasets:
            keys[key] = keyIndex
            values.append(self.dataset[key].readData(index))
            keyIndex = keyIndex + 1
        return keys, values

    def getDatasetDefinitions(self):
        definitionReturn = {}
        for key in self.dataset.keys():
            definition = self.metadata[f'{key}_dataset_description']
            definitionReturn[key] = definition
        return definitionReturn

    def addDataset(self, datasetName, datasetSize, chunksIn=(400, 110000), definition="", dtype='f', existing=0,
                   datasetPathIn=0):
        self.dataset[datasetName] = DatasetClass(datasetName, self.groupPath, datasetSize, chunksIn, definition, dtype,
                                                 existing=existing, datasetPathIn=datasetPathIn)
        if existing == 0:
            self.addMetadata(f'{datasetName}_dataset_description', definition)

    def resizeDataset(self, datasetName, newDatasetSize):
        self.dataset[datasetName].resizeDataset(newDatasetSize)

    def readMetadata(self):
        return self.metadata
    def redefine(self, datasetName, newDefinition):
        self.addMetadata(f'{datasetName}_dataset_description', newDefinition)


class DatasetClass:
    def __init__(self, datasetName, groupObject, datasetSize, chunksIn=(100000, 1730), definition="", dtype='f',
                 existing=0, datasetPathIn=0):
        self.groupPath = groupObject
        if existing == 0:
            self.datasetPath = groupObject.create_dataset(datasetName, datasetSize, maxshape=(None, None),
                                                          chunks=chunksIn, dtype=dtype)
        else:
            self.datasetPath = datasetPathIn
        self.metadata = {}
        self.definition = definition
        self.datasetName = datasetName

    def addMetadata(self, metadataName, metadataContents):
        self.metadata[metadataName] = metadataContents
        self.datasetPath.attrs[metadataName] = metadataContents

    def addData(self, index, dataToAdd):
        self.datasetPath[index] = dataToAdd

    def readData(self, index):
        return self.datasetPath[index]

    def resizeDataset(self, newDatasetSize):
        self.datasetPath.resize(newDatasetSize)

    def getDatasetSize(self):
        return self.datasetPath.shape

    def rename(self, newName, experimentClass):
        #first rename the dataset
        oldName = self.datasetName
        experimentClass.groupPath[newName] = experimentClass.groupPath[oldName]
        del experimentClass.groupPath[oldName]
        self.datasetName = newName
        experimentClass.handleDatasetRename(oldName, newName)

