"""
File: FileFormat.py
Authors: Samuel Karkache (swkarkache@wpi.edu), Trey Marcantonio (tmmarcantonio@wpi.edu)
Date: 2024-28-02
Description: File Format API for side-channel analysis experiments. Includes SNR, t-test, correlation, score and rank, and success rate and guessing entropy.
"""

"""
Filler Functions for file format metric wrappers
Dynamic Typing on Dataset input
Save metric output as a dataset
"""

import os
import numpy as np
from datetime import date
import json
from WPI_SCA_LIBRARY.Metrics import *

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

            self.JSONdata = {"fileName": sanatiseInput(path),
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
        key = sanatiseInput(key)
        self.metadata[key] = value
        self.updateJSON()

    def readMetadata(self):
        return self.metadata

    def addExperiment(self, name, path, existing, index = 0, experiment = {}):
        name = sanatiseInput(name)
        if not existing:
            path = f'{self.experimentsPath}\\{path}'
            JsonToSave = {
                "path" : path,
                "name" : name,
                "metadata" : {},
                "datasets" : [],
            }
            self.JSONdata["experiments"].append(JsonToSave)
            index = len(self.JSONdata["experiments"]) - 1
            self.JSONdata["experiments"][index]["index"] = index

            self.experiments[name] = ExperimentJsonClass(name, path, self, existing = False, index = index)
            os.mkdir(path)
            os.mkdir(f"{path}\\visualization")
            self.updateJSON()

        if existing:
            self.experiments[name] = ExperimentJsonClass(name, path, self, existing=True, index=index, experiment=experiment)

    def getExperiment(self, experimentName):
        experimentName = sanatiseInput(experimentName)
        return self.experiments[experimentName]

class ExperimentJsonClass:
    def __init__(self, name, path, fileFormatParent, existing = False, index = 0, experiment = {}):
        name = sanatiseInput(name)
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
        key = sanatiseInput(key)
        self.metadata[key] = value
        self.fileFormatParent.JSONdata["experiments"][self.index]["metadata"][key] = value
        self.fileFormatParent.updateJSON()
    def readMetadata(self):
        return self.metadata

    def createDataset(self, name, path, existing = False, size = (10,10), type = 'int8', dataset = {}):
        name = sanatiseInput(name)
        if not existing:
            dataToAdd = {"name" : name,
                         "path" : f'{self.path}\\{path}.npy',
                         "metadata" : {}}
            self.fileFormatParent.JSONdata["experiments"][self.experimentIndex]["datasets"].append(dataToAdd)
            index = len(self.fileFormatParent.JSONdata["experiments"][self.experimentIndex]["datasets"]) - 1

            self.fileFormatParent.JSONdata["experiments"][self.experimentIndex]["datasets"][index]['index'] = index
            self.fileFormatParent.updateJSON()

            self.dataset[name] = DatasetJsonClass(name, f"{self.path}\\{path}.npy", self.fileFormatParent, self, index, existing = False, size = size, type = type)

        if existing:
            self.dataset[name] = DatasetJsonClass(name, path, self.fileFormatParent, self, dataset["index"], existing=True, dataset = dataset)

    def calculateSNR(self, labelsDataset, tracesDataset, visualise = False, saveData = False, saveGraph = False):

        labelsDataset = sanatiseInput(labelsDataset)
        tracesDataset = tracesDataset(tracesDataset)

        if labelsDataset not in self.dataset:
            raise ValueError(f"{labelsDataset} is not a valid key")

        if tracesDataset not in self.dataset:
            raise ValueError(f"{tracesDataset} is not a valid key")


        #sort labels
        labels = self.dataset[labelsDataset].readAll()
        traces_set = self.dataset[tracesDataset].readAll()

        if len(labels) != len(traces_set):
            raise ValueError(f"Length of {labelsDataset} is {len(labels)} \n "
                             f"Length of {tracesDataset} is {len(traces_set)} \n"
                             f"The two arrays must be of equal length")

        if len(labels[0]) != 1:
            raise ValueError(f"The width of labels must be 1, currently the width"
                             f" of {labelsDataset} is {len(labels[0])}")

        labelsUnique = np.unique(labels)

        # initialize the dictionary
        sorted_labels = {}
        for i in labelsUnique:
            sorted_labels[i] = []

        # add traces to labels
        for index, label in enumerate(labels):
            label = int(label)
            sorted_labels[label].append(np.array(traces_set[index]))


        print(sorted_labels)
        #calc results
        path = ""
        if saveGraph:
            path = f"{self.fileFormatParent.path}\\Experiments\\{self.name}\\visualization\\SNR_{labelsDataset}_{tracesDataset}"

        results = signal_to_noise_ratio(sorted_labels, visualise, visualization_path=path)

        return results

    def getDataset(self, datasetName):
        datasetName = sanatiseInput(datasetName)
        return self.dataset[datasetName]

class DatasetJsonClass:
    def __init__(self, name, path, fileFormatParent, experimentParent, index, existing = False, size = (10,10), type = 'int8', dataset = {}):
        name = sanatiseInput(name)
        if not existing:
            self.name = name
            self.path = path
            self.index = index
            self.fileFormatParent = fileFormatParent
            self.experimentParent = experimentParent
            self.metadata = self.fileFormatParent.JSONdata["experiments"][self.experimentParent.experimentIndex]["datasets"][self.index]["metadata"]
            self.modifyMetadata("date_created", date.today().strftime('%Y-%m-%d'))

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

    def modifyMetadata(self, key, value):
        key = sanatiseInput(key)
        self.metadata[key] = value
        self.fileFormatParent.updateJSON()

    def deleteMetadata(self, key):
        self.metadata.pop(key)
        self.fileFormatParent.updateJSON()

def sanatiseInput(inputString: str):
    if type(inputString) != str:
        raise ValueError("The input to this function must be of type string")
    return inputString.lower()
