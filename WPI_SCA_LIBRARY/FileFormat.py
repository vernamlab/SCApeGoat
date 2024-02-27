import os
import time

import h5py
import numpy as np
import trsfile

from datetime import date
import json

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

            #create file structure
            os.mkdir(path)

            experimentsPath = f"{path}\\Experiments"
            visulizationsPath = f"{path}\\Visualizations"
            os.mkdir(experimentsPath)
            os.mkdir(visulizationsPath)

            self.JSONdata = {"fileName" : path,
                             "dateCreated" : date.today().strftime('%Y-%m-%d'),
                             "path" : os.path.abspath(path),
                             "experiments" : []}
            with open(f"{path}\\metadataHolder.json", 'w') as json_file:
                json.dump(self.JSONdata, json_file, indent=4)

            experimentsVizPath = f"{experimentsPath}\\Visualizations"
            os.mkdir(experimentsVizPath)

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
        self.experiments[experimentName] = ExperimentClass(experimentName, existing, groupPath, definition = definition, masterClass= self, jsonData=self.JSONdata)
        self.metadata[f'{experimentName}_experiment_description'] = definition
        experimentData = {
            "experimentTitle" : experimentName,
            "dateCreated" : date.today().strftime('%Y-%m-%d'),
            "path" : f"{self.path}\\Experiments\\{experimentName}",
            "datasets" : []
        }
        self.experiments[experimentName] = ExperimentClass(experimentName, existing, groupPath, definition=definition, masterClass=self, jsonData = experimentData)
        os.mkdir(experimentData["path"])
        self.JSONdata["experiments"].append(experimentData)
        self.saveJSONdata()

    def getMetadata(self):
        return self.metadata

    def saveJSONdata(self):
        with open(f"{self.path}\\metadataHolder.json", 'w') as json_file:
            json.dump(self.JSONdata, json_file, indent=4)

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
    def __init__(self, experimentName, existing=0, groupPath=0, definition = "", masterClass = "", jsonData = ""):
        self.dataset = {}
        self.metadata = {}
        self.definition = definition
        self.masterClass = masterClass
        self.path = jsonData["path"]

    def prepareSnrWithLabels(self, tracesName, labelsName, size):
        tracesClass = self.dataset[tracesName]
        labelsClass = self.dataset[labelsName]
        traces = tracesClass.readData(range(size))
        labels = labelsClass.readData(range(size))

        # find unique labels
        labelsUnique = np.unique(labels)

        # initialize the dictionary
        sortedLabels = {}
        for i in labelsUnique:
            sortedLabels[i] = []

        # add traces to labels
        for index, label in enumerate(labels):
            sortedLabels[label[0]].append(traces[index])

        return sortedLabels

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

    def addDataset(self, name, path, size, type):
        array = np.zeros((size), dtype=type)
        np.save(f"{self.path}\\{path}",array)
        self.dataset[name] = DatasetClass(name, f"{self.path}\\{path}", size, type)


    def resizeDataset(self, datasetName, newDatasetSize):
        self.dataset[datasetName].resizeDataset(newDatasetSize)

    def readMetadata(self):
        return self.metadata
    def redefine(self, datasetName, newDefinition):
        self.addMetadata(f'{datasetName}_dataset_description', newDefinition)


class DatasetClass:
    def __init__(self, name, path, size, type):
        self.name = name
        self.path = path
        self.size = size
        self.type = type

    def addMetadata(self, metadataName, metadataContents):
        self.metadata[metadataName] = metadataContents
        self.datasetPath.attrs[metadataName] = metadataContents

    def addData(self, index, dataToAdd):
        data = np.load(self.path)
        data[index] = dataToAdd
        np.save(self.path,data)

    def readData(self, index):
        data = np.load(self.path)
        return data[index]

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

class FileFormatParent:
    def __init__(self, path, existing = False):
        if not existing:
            self.path = path

            # create file structure
            os.mkdir(path)

            self.experimentsPath = f"{path}\\Experiments"
            self.visulizationsPath = f"{path}\\Visualizations"

            os.mkdir(self.experimentsPath)
            os.mkdir(self.visulizationsPath)

            self.JSONdata = {"fileName": path,
                             "metadata" : {"dateCreated": date.today().strftime('%Y-%m-%d')},
                             "path": os.path.abspath(path),
                             "experiments": []}
            with open(f"{path}\\metadataHolder.json", 'w') as json_file:
                json.dump(self.JSONdata, json_file, indent=4)

            self.experiments = {}
            self.metadata = self.JSONdata['metadata']

        if existing:
            #open json file
            with open(f"{path}\\metadataHolder.json", 'r') as json_file:
                self.JSONdata = json.load(json_file)

            self.path = path
            self.experimentsPath = f"{path}\\Experiments"
            self.visulizationsPath = f"{path}\\Visualizations"
            self.experiments = {}
            self.metadata = self.JSONdata["metadata"]

            #read experiments
            for experiment in self.JSONdata["experiments"]:
                self.addExperiment(experiment["name"], experiment["path"], True, index = experiment["index"], experiment=experiment)




    def updateJSON(self):
        with open(f"{self.path}\\metadataHolder.json", 'w') as json_file:
            json.dump(self.JSONdata, json_file, indent=4)

    def updateMetadata(self, key, value):
        #get rid of case sensitivity (filter to all be lowercase b4 entering)
        self.metadata[key] = value
        #TODO: update JSON var
        self.updateJSON()

    def readMetadata(self):
        return self.metadata

    def addExperiment(self, name, path, existing, index = 0, experiment = {}):
        if not existing:
            path = f'{self.experimentsPath}\\{path}'
            #TODO: Add more preset metadata params (date/time etc...)
            JsonToSave = {
                "path" : path,
                "name" : name,
                "metadata" : {},
                "datasets" : [],
            }
            self.JSONdata["experiments"].append(JsonToSave)
            index = len(self.JSONdata["experiments"]) - 1
            self.JSONdata["experiments"][index]["index"] = index

            self.experiments[name] = ExperimentJsonClass(name, path, self, existing = False)
            os.mkdir(path)
            os.mkdir(f"{path}\\visualization")
            self.updateJSON()

        if existing:
            self.experiments[name] = ExperimentJsonClass(name, path, self, existing=True, index=index, experiment=experiment)



class ExperimentJsonClass:
    def __init__(self, name, path, fileFormatParent, existing = False, index = 0, experiment = {}):
        if not existing:
            self.name = name
            self.path = path
            self.dataset = {}
            self.metadata = {}
            self.fileFormatParent = fileFormatParent
            self.experimentIndex = index

        if existing:
            self.name = name
            self.path = path
            self.dataset = {}
            self.metadata = experiment["metadata"]
            self.fileFormatParent = fileFormatParent
            self.experimentIndex = index

            #create datasets
            for dataset in experiment["datasets"]:
                self.createDataset(dataset["name"], dataset["path"], existing=True, dataset=dataset)

    def updateMetadata(self, key, value):
        self.metadata[key] = value
        self.fileFormatParent.JSONdata["experiments"][self.index]["metadata"][key] = value
        self.fileFormatParent.updateJSON()
    def readMetadata(self):
        return self.metadata

    def createDataset(self, name, path, existing = False, size = (10,10), type = 'int8', dataset = {}):
        if not existing:
            dataToAdd = {"name" : name,
                         "path" : f'{self.path}\\{path}',
                         "metadata" : {}}
            self.fileFormatParent.JSONdata["experiments"][self.experimentIndex]["datasets"].append(dataToAdd)
            index = len(self.fileFormatParent.JSONdata["experiments"][self.experimentIndex]["datasets"]) - 1

            self.fileFormatParent.JSONdata["experiments"][self.experimentIndex]["datasets"][index]['index'] = index
            self.fileFormatParent.updateJSON()

            self.dataset[name] = DatasetJsonClass(name, f"{self.path}\\{path}", self.fileFormatParent, self, index, existing = False, size = size, type = type)

        if existing:
            self.dataset[name] = DatasetJsonClass(name, path, self.fileFormatParent, self, dataset["index"], existing=True, dataset = dataset)

class DatasetJsonClass:
    def __init__(self, name, path, fileFormatParent, experimentParent, index, existing = False, size = (10,10), type = 'int8', dataset = {}):
        if not existing:
            self.name = name
            self.path = path
            self.index = index
            self.fileFormatParent = fileFormatParent
            self.experimentParent = experimentParent
            self.metadata = {}

            array = np.zeros((size), dtype=type)
            np.save(path, array)

        if existing:
            self.name = name
            self.path = path
            self.index = index
            self.fileFormatParent = fileFormatParent
            self.experimentParent = experimentParent
            self.metadata = dataset["metadata"]

    def readData(self, index):
        data = np.load(self.path)
        return data[index]

    def readAll(self):
        data = np.load(self.path)
        return data[:]
    def addData(self, index, dataToAdd):
        data = np.load(self.path)
        data[index] = dataToAdd
        np.save(self.path,data)
