import os
import time

import h5py
import numpy as np
import trsfile

from datetime import date
import json

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
