from __future__ import annotations

import json
import os
import re
import shutil
from datetime import date

import numpy as np

from WPI_SCA_LIBRARY.Metrics import *

"""
File: FileFormat.py
Authors: Samuel Karkache (swkarkache@wpi.edu), Trey Marcantonio (tmmarcantonio@wpi.edu)
Date: 2024-28-02
Description: File Format API for side-channel analysis experiments.
"""


class FileParent:
    def __init__(self, name: str, path: str, existing: bool = False):
        """
        Initialize FileFormatParent class. Creates the basic file structure including JSON metadata holder. If the file
        already exists it simply returns a reference to that file.
        :param name: Name of file
        :type name: str
        :param path: Absolute path to where you want to save the file. Leaving black will put it into current directory.
        :type path: str
        :param existing: Whether the file exists
        :type existing: bool
        :return: FileParent object corresponding to the specified file.
        """
        if not existing:
            self.name = name
            if path[-1:] == "\\":
                self.path = path + name
            else:
                self.path = path + "\\" + name
            self.experiments_path = f"{self.path}\\Experiments"

            dir_created = False

            while not dir_created:
                try:
                    os.mkdir(self.path)
                    os.mkdir(self.experiments_path)
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
            self.name = name
            if path[-1:] == "\\":
                path = path + name
            else:
                path = path + "\\" + name
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
            self.experiments = {}
            self.metadata = self.json_data["metadata"]

            for experiment in self.json_data["experiments"]:
                if os.path.exists(self.path + experiment["path"]):
                    self.add_experiment_internal(exp_name=experiment.get('name'), existing=True,
                                                 index=experiment.get('index'),
                                                 experiment=experiment)
                else:
                    for experiment_json in self.json_data["experiments"]:
                        if experiment_json["name"] == experiment["name"]:
                            self.json_data["experiments"].remove(experiment_json)

                    with open(f"{self.path}\\metadataHolder.json", 'w') as json_file:
                        json.dump(self.json_data, json_file, indent=4)

    def update_json(self) -> None:
        """
        Dump new json data. Do not call this, call update metadata instead.
        """
        with open(f"{self.path}\\metadataHolder.json", 'w') as json_file:
            json.dump(self.json_data, json_file, indent=4)

    def update_metadata(self, key: str, value: str) -> None:
        """
        Update file JSON metadata with key value pair
        :param key: metadata key
        :param value: metadata value
        """
        key = sanitize_input(key)
        self.metadata[key] = value
        self.update_json()

    def read_metadata(self) -> dict:
        """
        Read JSON metadata from file
        :return: The JSON metadata
        """
        return self.metadata

    def add_experiment(self, name: str) -> 'Experiment':
        """
        Adds a new experiment to the file
        :param name: The experiment name
        :return: The newly added experiment class.
        :rtype: Experiment
        """
        return self.add_experiment_internal(name, existing=False, index=0, experiment=None)

    def add_experiment_internal(self, exp_name: str, existing: bool = False, index: int = 0,
                                experiment: dict = None) -> 'Experiment':
        """
        Internal Function for adding experiments used when getting a reference to an existing file. Call add_experiment
        to add a new experiment instead of this.
        """
        if experiment is None:
            experiment = {}

        exp_name = sanitize_input(exp_name)
        exp_path = f'\\Experiments\\{exp_name}'

        if not existing:
            dir_created = False
            while not dir_created:
                try:
                    os.mkdir(self.path + exp_path)
                    os.mkdir(f"{self.path + exp_path}\\visualization")
                    dir_created = True
                except FileExistsError:
                    if bool(re.match(r'.*-\d$', exp_name)):
                        ver_num = int(exp_name[len(exp_name) - 1]) + 1
                        new_name = exp_name[:-1] + str(ver_num)
                        new_path = exp_path[:-1] + str(ver_num)
                    else:
                        new_name = exp_name + "-1"
                        new_path = exp_path + "-1"
                    exp_name = new_name
                    exp_path = new_path

            json_to_save = {
                "name": exp_name,
                "path": exp_path,
                "metadata": {},
                "datasets": [],
            }

            self.json_data["experiments"].append(json_to_save)
            idx = len(self.json_data["experiments"]) - 1
            self.json_data["experiments"][idx]["index"] = idx
            self.experiments[exp_name] = Experiment(exp_name, exp_path, self, existing=False, index=idx)
            self.update_json()

        else:
            self.experiments[exp_name] = (
                Experiment(exp_name, exp_path, self, existing=True, index=index, experiment=experiment))

        return self.experiments[exp_name]

    def get_experiment(self, experiment_name: str) -> 'Experiment':
        """
        Get an experiment from the file
        :param experiment_name: The name of the experiment
        :return: The requested experiment
        """
        experiment_name = sanitize_input(experiment_name)
        return self.experiments[experiment_name]

    def delete_file(self) -> None:
        """
        Deletes the entire file. Confirmation required.
        """
        res = sanitize_input(
            input("You are about to delete file {}. Do you want to proceed? [Y/N]: ".format(self.name)))

        if res == "y" or res == "yes":
            print("Deleting file {}".format(self.name))
            shutil.rmtree(self.path)
        else:
            print("Deletion of file {} cancelled.".format(self.name))

    def delete_experiment(self, experiment_name: str) -> None:
        """
        Deletes an experiment and all of its contents
        :param experiment_name: The name of the experiment to be deleted
        """
        experiment_name = sanitize_input(experiment_name)
        res = sanitize_input(input(
            "You are about to delete {} in file {}. Do you want to proceed? [Y/N]: ".format(experiment_name,
                                                                                            self.name)))

        if res == "y" or res == "yes":
            print("Deleting experiment {}".format(experiment_name))

            shutil.rmtree(self.path + self.experiments[experiment_name].path)
            self.experiments.pop(experiment_name)
            for experiment_json in self.json_data["experiments"]:
                if experiment_json["name"] == experiment_name:
                    self.json_data["experiments"].remove(experiment_json)

            with open(f"{self.path}\\metadataHolder.json", 'w') as json_file:
                json.dump(self.json_data, json_file, indent=4)
        else:
            print("Deletion of experiment {} cancelled.".format(experiment_name))

    def query_experiments_with_metadata(self, key: str, value: str, regex: bool = False) -> list['Experiment']:
        """
        Get all experiments in the file with specific metadata.
        :param key: the key of the metadata you are searching
        :param value: The value of the metadata you are searching for. Providing "*" will return all experiments that have
                      metadata with the given key.
        :param regex: Whether the value is a regular expression
        :return: A list of experiments having the key value pair supplied
        """
        experiments = []

        for exp in self.experiments.values():
            try:
                res = exp.metadata[key]
                if not regex:
                    if value == res or value == "*":
                        experiments.append(exp)
                else:
                    if bool(re.match(value, res)):
                        experiments.append(exp)
            except KeyError:
                continue
        return experiments


class Experiment:
    def __init__(self, name: str, path: str, file_format_parent: FileParent, existing: bool = False, index: int = 0,
                 experiment: dict = None):

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
                if os.path.exists(self.fileFormatParent.path + self.path + dataset["path"]):
                    self.add_dataset_internal(dataset["name"], existing=True, dataset=dataset)
                else:
                    for experiment_json in self.fileFormatParent.json_data["experiments"]:
                        if experiment_json["name"] == self.name:

                            for _dataset in experiment_json["datasets"]:
                                if dataset["name"] == _dataset["name"]:
                                    experiment_json["datasets"].remove(dataset)

                    with open(f"{self.fileFormatParent.path}\\metadataHolder.json", 'w') as json_file:
                        json.dump(self.fileFormatParent.json_data, json_file, indent=4)

    def update_metadata(self, key: str, value: str) -> None:
        key = sanitize_input(key)
        self.metadata[key] = value
        self.fileFormatParent.json_data["experiments"][self.experimentIndex]["metadata"][key] = value
        self.fileFormatParent.update_json()

    def read_metadata(self) -> None:
        return self.metadata

    def add_dataset(self, name: str, data_to_add: np.ndarray | list, datatype: any) -> 'Dataset':
        """
        Adds a dataset to an experiment.
        :param datatype: Datatype of the dataset
        :param data_to_add: The data to be added as a list or Numpy array.
        :param name: The name of the dataset.
        :return: The newly created dataset
        """
        dataset = self.add_dataset_internal(name, existing=False, dataset=None)
        dataset.add_data(data_to_add, datatype)
        return dataset

    def add_dataset_internal(self, name: str, existing: bool = False, dataset: dict = None) -> 'Dataset':

        if dataset is None:
            dataset = {}

        name = sanitize_input(name)

        while name in self.dataset:
            if bool(re.match(r'.*-\d$', name)):
                ver_num = int(name[len(name) - 1]) + 1
                name = name[:-1] + str(ver_num)
            else:
                name = name + "-1"

        path = f'\\{name}.npy'

        if not existing:
            dataToAdd = {
                "name": name,
                "path": path,
                "metadata": {}
            }

            self.fileFormatParent.json_data["experiments"][self.experimentIndex]["datasets"].append(dataToAdd)
            index = len(self.fileFormatParent.json_data["experiments"][self.experimentIndex]["datasets"]) - 1

            self.fileFormatParent.json_data["experiments"][self.experimentIndex]["datasets"][index]['index'] = index
            self.fileFormatParent.update_json()

            self.dataset[name] = Dataset(name, path, self.fileFormatParent, self, index, existing=False)

        if existing:
            self.dataset[name] = Dataset(name, path, self.fileFormatParent, self, dataset["index"], existing=True,
                                         dataset=dataset)

        return self.dataset[name]

    def get_dataset(self, dataset_name: str) -> 'Dataset':
        dataset_name = sanitize_input(dataset_name)
        return self.dataset[dataset_name]

    def delete_dataset(self, dataset_name: str) -> None:
        """
        Deletes a dataset and all of its contents
        :param dataset_name: The name of the experiment to be deleted
        """
        dataset_name = sanitize_input(dataset_name)
        res = sanitize_input(input(
            "You are about to delete {} in experiment {}. Do you want to proceed? [Y/N]: ".format(dataset_name,
                                                                                                  self.name)))
        if res == "y" or res == "yes":
            print("Deleting dataset {}".format(dataset_name))
            os.remove(self.fileFormatParent.path + self.path + "\\" + dataset_name + ".npy")
            self.dataset.pop(dataset_name)

            for experiment_json in self.fileFormatParent.json_data["experiments"]:
                if experiment_json["name"] == self.name:
                    for dataset in experiment_json["datasets"]:
                        if dataset["name"] == dataset_name:
                            experiment_json["datasets"].remove(dataset)

            with open(f"{self.fileFormatParent.path}\\metadataHolder.json", 'w') as json_file:
                json.dump(self.fileFormatParent.json_data, json_file, indent=4)

        else:
            print("Deletion of experiment {} cancelled.".format(dataset_name))

    def query_datasets_with_metadata(self, key: str, value: str, regex: bool = False) -> list['Dataset']:
        """
        Queries datasets with using the associated metadata.
        :param key: The key of the metadata you are querying
        :param value: The value of the metadata you are querying. Providing "*" will return all with the specified key
                      and any value.
        :param regex: Whether the provided value is a regular expression.
        :return: A list of datasets with the provided metadata.
        """
        datasets = []
        for dset in self.dataset.values():
            try:
                res = dset.metadata[key]
                if not regex:
                    if res == value or value == "*":
                        datasets.append(dset)
                else:
                    if bool(re.match(value, res)):
                        datasets.append(dset)
            except KeyError:
                continue
        return datasets

    def get_visualization_path(self):
        return self.fileFormatParent.path + self.path + "\\" + "visualization" + "\\"

    def calculate_snr(self, traces_dataset: str, intermediate_fcn: Callable, *args: any,  visualize: bool = False, save_data: bool = False, save_graph: bool = False) -> np.ndarray:
        """
        Integrated SNR metric with file format
        :param traces_dataset: The name of the traces dataset
        :type traces_dataset: str
        :param intermediate_fcn: The intermediate function used to calculate SNR labels
        :type intermediate_fcn: Callable
        :param visualize: Whether to visualize the SNR values
        :type visualize: bool
        :param save_data: Whether to save the SNR values as a dataset
        :type save_data: bool
        :param save_graph: Whether to save the SNR graph to the visualization directory
        :type save_graph: bool
        :return: The SNR trace
        :rtype: np.ndarray
        """

        traces_dataset = sanitize_input(traces_dataset)
        args = tuple(self.dataset[sanitize_input(x)].read_all() for x in args)

        traces = self.dataset[traces_dataset].read_all()
        labels = organize_snr_label(traces, intermediate_fcn, *args)

        if save_graph:
            path_created = False
            image_name = "{}_snr".format(traces_dataset)
            path = self.get_visualization_path() + image_name

            while not path_created:
                if os.path.exists(self.get_visualization_path() + image_name + ".png"):
                    if bool(re.match(r'.*-\d$', image_name)):
                        ver_num = int(image_name[len(image_name) - 1]) + 1
                        image_name = image_name[:-1] + str(ver_num)
                    else:
                        image_name = image_name + "-1"
                else:
                    path = self.get_visualization_path() + image_name + ".png"
                    path_created = True
        else:
            path = None

        snr = signal_to_noise_ratio(labels, visualize=visualize, visualization_path=path)

        if save_data:
            self.add_dataset("{}_snr".format(traces_dataset), snr, "float32")

        return snr

    def calculate_t_test(self, fixed_dataset: str, random_dataset: str, visualize: bool = False, save_data: bool = False, save_graph: bool = False) -> (np.ndarray, np.ndarray):
        """
        Integrated t-test metric with file format.
        :param fixed_dataset: The name of the fixed traces dataset
        :type fixed_dataset: str
        :param random_dataset: The name of the random traces dataset
        :type random_dataset: str
        :param visualize: Whether to visualize the t-test values
        :type visualize: bool
        :param save_data: Whether to save the t-test values as a dataset
        :type save_data: bool
        :param save_graph: Whether to save the t-test graph to the visualization directory
        :type save_graph: bool
        :return: Tuple containing t-statistic and t-max NumPy arrays
        :rtype: (np.ndarray, np.ndarray)
        """

        rand = self.dataset[sanitize_input(random_dataset)].read_all()
        fixed = self.dataset[sanitize_input(fixed_dataset)].read_all()

        if save_graph:
            path_created_t = False
            t_name = f"t_test_{random_dataset}_{fixed_dataset}"
            t_path = self.get_visualization_path() + t_name

            while not path_created_t:
                if os.path.exists(self.get_visualization_path() + t_name + ".png"):
                    if bool(re.match(r'.*-\d$', t_name)):
                        ver_num = int(t_name[len(t_name) - 1]) + 1
                        t_name = t_name[:-1] + str(ver_num)
                    else:
                        t_name = t_name + "-1"
                else:
                    t_path = self.get_visualization_path() + t_name + ".png"
                    path_created_t = True

            path_created_max = False
            t_max_name = f"t_max_{random_dataset}_{fixed_dataset}"
            t_max_path = self.get_visualization_path() + t_max_name

            while not path_created_max:
                if os.path.exists(self.get_visualization_path() + t_max_name + ".png"):
                    if bool(re.match(r'.*-\d$', t_max_name)):
                        ver_num = int(t_max_name[len(t_max_name) - 1]) + 1
                        t_max_name = t_max_name[:-1] + str(ver_num)
                    else:
                        t_max_name = t_max_name + "-1"
                else:
                    t_max_path = self.get_visualization_path() + t_max_name + ".png"
                    path_created_max = True
            path = (t_path, t_max_path)
        else:
            path = None

        t, t_max = t_test_tvla(fixed, rand, visualize=visualize, visualization_paths=path)

        if save_data:
            self.add_dataset(f"t_test_{random_dataset}_{fixed_dataset}", t, datatype="float32")
            self.add_dataset(f"t_max_{random_dataset}_{fixed_dataset}", t_max, datatype="float32")

        return t, t_max

    def calculate_correlation(self, predicted_dataset_name: str, observed_dataset_name: str, visualize: bool = False, save_data: bool = False, save_graph: bool = False) -> np.ndarray:
        """
        Integrated correlation metric with file format.
        :param predicted_dataset_name: The name of the dataset containing the predicted leakage generated via some leakage model
        :type predicted_dataset_name: str
        :param observed_dataset_name: The name of the dataset containing the observed leakage
        :type observed_dataset_name: str
        :param visualize: Whether to visualize the correlation values
        :type visualize: bool
        :param save_data: Whether to save the correlation values as a dataset
        :type save_data: bool
        :param save_graph: Whether to save the correlation graph to the visualization directory
        :type save_graph: bool
        :return: The correlation trace
        :rtype: np.ndarray
        """

        predicted = self.get_dataset(predicted_dataset_name).read_all()
        observed = self.get_dataset(observed_dataset_name).read_all()

        if save_graph:
            path_created = False
            image_name = f"corr_{predicted_dataset_name}_{observed_dataset_name}"
            path = self.get_visualization_path() + image_name

            while not path_created:
                if os.path.exists(self.get_visualization_path() + image_name + ".png"):
                    if bool(re.match(r'.*-\d$', image_name)):
                        ver_num = int(image_name[len(image_name) - 1]) + 1
                        image_name = image_name[:-1] + str(ver_num)
                    else:
                        image_name = image_name + "-1"
                else:
                    path = self.get_visualization_path() + image_name + ".png"
                    path_created = True
        else:
            path = None

        corr = pearson_correlation(predicted, observed, visualize=visualize, visualization_path=path)

        if save_data:
            self.add_dataset(f"corr_{predicted_dataset_name}_{observed_dataset_name}", corr, datatype="float32")

        return corr


class Dataset:
    def __init__(self, name: str, path: str, file_format_parent: FileParent, experiment_parent: Experiment, index: int,
                 existing: bool = False, dataset: dict = None):
        if dataset is None:
            dataset = {}

        name = sanitize_input(name)
        if not existing:
            self.name = name
            self.path = path
            self.index = index
            self.fileFormatParent = file_format_parent
            self.experimentParent = experiment_parent
            self.metadata = \
                self.fileFormatParent.json_data["experiments"][self.experimentParent.experimentIndex]["datasets"][
                    self.index]["metadata"]
            self.update_metadata("date_created", date.today().strftime('%Y-%m-%d'))

        if existing:
            self.name = name
            self.path = path
            self.index = index
            self.fileFormatParent = file_format_parent
            self.experimentParent = experiment_parent
            self.metadata = dataset["metadata"]

    def read_data(self, start: int, end: int) -> np.ndarray:
        data = np.load(self.fileFormatParent.path + self.experimentParent.path + self.path)
        return data[start:end]

    def read_all(self) -> np.ndarray:
        data = np.load(self.fileFormatParent.path + self.experimentParent.path + self.path)
        return data[:]

    def add_data(self, data_to_add: np.ndarray, datatype: any) -> None:
        data_to_add = np.array(data_to_add, dtype=datatype)
        np.save(self.fileFormatParent.path + self.experimentParent.path + self.path, data_to_add)

    def update_metadata(self, key: str, value: str) -> None:
        key = sanitize_input(key)
        self.metadata[key] = value
        self.fileFormatParent.update_json()

    def delete_metadata(self, key: str) -> None:
        self.metadata.pop(key)
        self.fileFormatParent.update_json()


def sanitize_input(input_string: str) -> str:
    if type(input_string) is not str:
        raise ValueError("The input to this function must be of type string")
    return input_string.lower()
