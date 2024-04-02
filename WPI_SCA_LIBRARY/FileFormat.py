import json
import os
from datetime import date
import re
import warnings
from WPI_SCA_LIBRARY.Metrics import *

"""
File: FileFormat.py
Authors: Samuel Karkache (swkarkache@wpi.edu), Trey Marcantonio (tmmarcantonio@wpi.edu)
Date: 2024-28-02
Description: File Format API for side-channel analysis experiments.
"""


class FileParent:
    def __init__(self, name, path, existing=False):
        """
        Initialize FileFormatParent class.
        :param name: Relative path to base file
        :type name: str
        :param path: Absolute path to where you want to save the file. Leaving black will put it into current directory
        :type path: str
        :param existing: Whether the file exists
        :type existing: bool
        """
        if not existing:
            self.name = name
            self.path = path
            self.experiments_path = f"{self.path}\\Experiments"
            self.visualizations_path = f"{self.path}\\Visualizations"

            dir_created = False

            while not dir_created:
                try:
                    os.mkdir(self.path)
                    os.mkdir(self.experiments_path)
                    os.mkdir(self.visualizations_path)
                    dir_created = True
                except FileExistsError:
                    if bool(re.match(r'.*-\d$', self.name)):
                        ver_num = int(self.name[len(self.name) - 1]) + 1
                        new_name = self.name[:-1] + str(ver_num)
                        new_path = self.path[:-1] + str(ver_num)
                    else:
                        new_name = self.name + "-1"
                        new_path = self.path + "-1"
                    self.name = new_name
                    self.path = new_path
                    self.experiments_path = f"{self.path}\\Experiments"
                    self.visualizations_path = f"{self.path}\\Visualizations"

            self.json_data = {
                "fileName": sanitize_input(name),
                "metadata": {"dateCreated": date.today().strftime('%Y-%m-%d')},
                "path": self.path,
                "experiments": []
            }

            with open(f"{self.path}\\metadataHolder.json", 'w') as json_file:
                json.dump(self.json_data, json_file, indent=4)

            self.experiments = {}
            self.metadata = self.json_data['metadata']

        else:
            with open(f"{path}\\metadataHolder.json", 'r') as json_file:
                self.json_data = json.load(json_file)
            path_from_json = self.json_data["path"]

            # check if file has been moved
            if path_from_json != path:
                self.path = path
                self.json_data["path"] = path
                self.update_json()
            else:
                self.path = path_from_json

            self.experiments_path = f"{self.path}\\Experiments"
            self.visualizations_path = f"{self.path}\\Visualizations"
            self.experiments = {}
            self.metadata = self.json_data["metadata"]

            for experiment in self.json_data["experiments"]:
                self.add_experiment(name=experiment.get('name'), path=experiment.get('path'), existing=True,
                                    index=experiment.get('index'),
                                    experiment=experiment)

    def update_json(self):
        """
        Dump new json data. Do not call this, call update metadata instead.
        """
        with open(f"{self.path}\\metadataHolder.json", 'w') as json_file:
            json.dump(self.json_data, json_file, indent=4)

    def update_metadata(self, key, value):
        """
        Update file JSON metadata with key value pair
        :param key: metadata key
        :param value: metadata value
        """
        key = sanitize_input(key)
        self.metadata[key] = value
        self.update_json()

    def read_metadata(self):
        """
        Read JSON metadata from file
        :return: The JSON metadata
        """
        return self.metadata

    def add_experiment(self, name, path=None, existing=False, index=0, experiment=None):
        """
        Add a new experiment to the file.
        :param name: The name of the experiment
        :param existing: Whether the experiment already exists
        :param index: Index to put the experiment in
        :param experiment: TODO: Idk what this is...
        """
        if experiment is None:
            experiment = {}

        name = sanitize_input(name)

        if not existing:
            if path is None:
                path = f'\\Experiments\\{name}'
            else:
                path = f'\\Experiments\\{path}'

            json_to_save = {
                "path": path,
                "name": name,
                "metadata": {},
                "datasets": [],
            }
            self.json_data["experiments"].append(json_to_save)
            index = len(self.json_data["experiments"]) - 1
            self.json_data["experiments"][index]["index"] = index

            self.experiments[name] = Experiment(name, path, self, existing=False, index=index)
            os.mkdir(self.path + path)
            os.mkdir(f"{self.path + path}\\visualization")
            self.update_json()

        else:
            self.experiments[name] = (
                Experiment(name, path, self, existing=True, index=index, experiment=experiment))

        return self.experiments[name]

    def get_experiment(self, experiment_name):
        """
        Get an experiment from the file
        :param experiment_name: The name of the experiment
        :return: The requested experiment
        """
        experiment_name = sanitize_input(experiment_name)
        return self.experiments[experiment_name]


class Experiment:
    def __init__(self, name, path, file_format_parent, existing=False, index=0, experiment=None):

        if experiment is None:
            experiment = {}

        name = sanitize_input(name)

        if not existing:
            self.name = name
            self.path = path
            self.dataset = {}
            self.metadata = {}
            self.fileFormatParent = file_format_parent
            self.experimentIndex = index

        else:
            self.name = name
            self.path = path
            self.dataset = {}
            self.metadata = experiment["metadata"]
            self.fileFormatParent = file_format_parent
            self.experimentIndex = index

            for dataset in experiment["datasets"]:
                self.create_dataset(dataset["name"], existing=True, dataset=dataset)

    def update_metadata(self, key, value):
        key = sanitize_input(key)
        self.metadata[key] = value
        self.fileFormatParent.json_data["experiments"][self.experimentIndex]["metadata"][key] = value
        self.fileFormatParent.update_json()

    def read_metadata(self):
        return self.metadata

    def create_dataset(self, name, existing=False, size=(10, 10), datatype='int8', dataset=None):

        if dataset is None:
            dataset = {}

        name = sanitize_input(name)
        path = f'\\{name}.npy'

        if not existing:
            dataToAdd = {"name": name,
                         "path": path,
                         "metadata": {}}

            self.fileFormatParent.json_data["experiments"][self.experimentIndex]["datasets"].append(dataToAdd)
            index = len(self.fileFormatParent.json_data["experiments"][self.experimentIndex]["datasets"]) - 1

            self.fileFormatParent.json_data["experiments"][self.experimentIndex]["datasets"][index]['index'] = index
            self.fileFormatParent.update_json()

            self.dataset[name] = Dataset(name, path, self.fileFormatParent, self, index,
                                         existing=False, size=size, datatype=datatype)

        if existing:
            self.dataset[name] = Dataset(name, path, self.fileFormatParent, self, dataset["index"],
                                         existing=True, dataset=dataset)

        return self.dataset[name]

    def calculate_snr(self, labels_dataset, traces_dataset, visualise=False, save_data=False, save_graph=False):

        labels_dataset = sanitize_input(labels_dataset)
        traces_dataset = sanitize_input(traces_dataset)

        if labels_dataset not in self.dataset:
            raise ValueError(f"{labels_dataset} is not a valid key")

        if traces_dataset not in self.dataset:
            raise ValueError(f"{traces_dataset} is not a valid key")

        # sort labels
        labels = self.dataset[labels_dataset].read_all()
        traces_set = self.dataset[traces_dataset].read_all()

        if len(labels) != len(traces_set):
            raise ValueError(f"Length of {labels_dataset} is {len(labels)} \n "
                             f"Length of {traces_dataset} is {len(traces_set)} \n"
                             f"The two arrays must be of equal length")

        if len(labels[0]) != 1:
            raise ValueError(f"The width of labels must be 1, currently the width"
                             f" of {labels_dataset} is {len(labels[0])}")

        labelsUnique = np.unique(labels)

        # initialize the dictionary
        sorted_labels = {}
        for i in labelsUnique:
            sorted_labels[i] = []

        # add traces to labels
        for index, label in enumerate(labels):
            label = int(label)
            sorted_labels[label].append(np.array(traces_set[index]))

        path = None
        if save_graph:
            path = f"{self.fileFormatParent.path}\\Experiments\\{self.name}\\visualization\\SNR_{labels_dataset}_{traces_dataset}"  # TODO : We need to find a way to prevent this from overwriting other graphs

        results = signal_to_noise_ratio(sorted_labels, visualise, visualization_path=path)

        if save_data:
            self.create_dataset(f"SNR_{labels_dataset}_{traces_dataset}_results", size=results.shape, datatype=results.dtype)

        return results

    def calculate_t_test(self, fixed_dataset, random_dataset, visualize=False, save_data=False, save_graph=False):
        random_dataset = sanitize_input(random_dataset)
        fixed_dataset = sanitize_input(fixed_dataset)

        if random_dataset not in self.dataset:
            raise ValueError(f"{random_dataset} not found as a dataset in experiment {self.name}")

        if fixed_dataset not in self.dataset:
            raise ValueError(f"{fixed_dataset} not found as a dataset in experiment {self.name}")

        rand = self.dataset[random_dataset].read_all()
        fixed = self.dataset[fixed_dataset].read_all()

        path = None
        if save_graph:
            path = (
                f"{self.fileFormatParent.path}\\Experiments\\{self.name}\\visualization\\t_test_{random_dataset}_{fixed_dataset}",
                # TODO : We need to find a way to prevent this from overwriting other graphs
                f"{self.fileFormatParent.path}\\Experiments\\{self.name}\\visualization\\t_max_{random_dataset}_{fixed_dataset}")

        t, t_max = t_test_tvla(fixed, rand, visualize=visualize, visualization_paths=path)

        return t, t_max

    def get_dataset(self, dataset_name):
        dataset_name = sanitize_input(dataset_name)
        return self.dataset[dataset_name]


class Dataset:
    def __init__(self, name, path, file_format_parent, experiment_parent, index, existing=False, size=(10, 10),
                 datatype='int8', dataset=None):
        if dataset is None:
            dataset = {}

        name = sanitize_input(name)
        if not existing:
            self.name = name
            self.size = size
            self.path = path
            self.index = index
            self.fileFormatParent = file_format_parent
            self.experimentParent = experiment_parent
            self.metadata = \
                self.fileFormatParent.json_data["experiments"][self.experimentParent.experimentIndex]["datasets"][
                    self.index]["metadata"]
            self.modify_metadata("date_created", date.today().strftime('%Y-%m-%d'))

            array = np.zeros(size, dtype=datatype)
            np.save(self.fileFormatParent.path + self.experimentParent.path + self.path, array)

        if existing:
            self.name = name
            self.path = path
            self.index = index
            self.fileFormatParent = file_format_parent
            self.experimentParent = experiment_parent
            self.metadata = dataset["metadata"]

    def read_data(self, index):
        data = np.load(self.fileFormatParent.path + self.experimentParent.path + self.path)
        return data[index]

    def read_all(self):
        data = np.load(self.fileFormatParent.path + self.experimentParent.path + self.path)
        return data[:]

    def add_data(self, data_to_add):
        data = np.load(self.fileFormatParent.path + self.experimentParent.path + self.path)
        data[:self.size[0], :self.size[1]] = data_to_add
        np.save(self.fileFormatParent.path + self.experimentParent.path + self.path, data)

    def modify_metadata(self, key, value):
        key = sanitize_input(key)
        self.metadata[key] = value
        self.fileFormatParent.update_json()

    def delete_metadata(self, key):
        self.metadata.pop(key)
        self.fileFormatParent.update_json()


def sanitize_input(input_string: str):
    if type(input_string) is not str:
        raise ValueError("The input to this function must be of type string")
    return input_string.lower()
