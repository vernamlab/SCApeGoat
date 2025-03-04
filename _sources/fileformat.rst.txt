Custom File Framework
==================
The file framework is split into three separate classes.

.. class:: FileParent

    .. method:: __init__(self, name: str, path: str, existing: bool = False):

        Initialize FileFormatParent class. Creates the basic file structure including JSON metadata holder. If the file
        already exists it simply returns a reference to that file. To create a file named "ExampleFile" in your downloads
        directory set the name parameter to `name="ExampleFile` and the path to `path="C:\\users\\username\\\desktop`. The
        path needs to be structured as shown with double back slashes.

        :param name: The name of the file parent directory
        :type name: str
        :param path: The path to the file parent.
        :type path: str
        :param existing: whether the file already exists
        :type existing: bool
        :returns: None

    .. method:: update_metadata(self, key: str, value: any) -> None:

        Update file JSON metadata with key-value pair

        :param key: The key of the metadata
        :type key: str
        :param value: The value of the metadata. Can be any datatype supported by JSON
        :type value: any
        :returns: None


    .. method:: read_metadata(self) -> dict:

        Read JSON metadata from file

        :returns: The metadata dictionary for the FileParent object
        :rtype: dict

    .. methood:: add_experiment(self, name: str) -> 'Experiment':

        Adds a new experiment to the FileParent object

        :param name: The desired name of the new experiment
        :type name: str
        :returns: The newly created Experiment object
        :rtype: Experiment

    .. method:: get_experiment(self, experiment_name: str) -> 'Experiment':

        Get an existing experiment from the FileParent.

        :param experiment_name: The name of the requested experiment
        :type experiment_name: str
        :returns: The requested experiment. None if it does not exist.
        :rtype: Experiment. None if not found.

    .. method:: delete_file(self) -> None:

        Deletes the entire file. Confirmation required.

        :returns: None

    .. method:: delete_experiment(self, experiment_name: str) -> None:

        Deletes an experiment and all of its datasets from a FileParent. Confirmation Required.

        :param experiment_name: The name of the experiment
        :type experiment_name: str
        :returns: None

    .. method:: query_experiments_with_metadata(self, key: str, value: any, regex: bool = False) -> list['Experiment']:

        Query all experiments in the FileParent object based on exact metadata key-value pair or using regular expressions.

        :param key: The key to be queried
        :type key: str
        :param value: The value to be queried. Supply a regular expression if the `regex` parameter is set to true. Supplying
                        a value of "*" will return all experiments with the `key` specified in the key parameter.
        :type value: any
        :returns: A list of queried experiments
        :rtype: list['Experiment']


.. class:: Experiment

    .. method:: __init__(self, name: str, path: str, file_format_parent: FileParent, existing: bool = False, index: int = 0, experiment: dict = None):

        Creates an Experiment object. Do not call this constructor. Please use `FileParent.add_experiment()` to
        create a new Experiment object. DO NOT USE.

    .. method:: update_metadata(self, key: str, value: any) -> None:

        Update the experiment metadata using a new key value pair.

        :param key: The key of the metadata
        :type key: str
        :param value: The value of the metadata. Can be any datatype supported by JSON.
        :type value: any
        :returns: None


    .. method:: read_metadata(self) -> dict:

        Reads experiment metadata

        :returns: The experiment's metadata dictionary
        :rtype: dict

    .. method:: add_dataset(self, name: str, data_to_add: np.ndarray, datatype: any) -> 'Dataset':

        Adds a new Dataset to a given Experiment

        :param name: The desired name of the new dataset
        :type name: str
        :param data_to_add: The NumPy array of data to be added to the new dataset
        :type data_to_add: np.ndarray
        :returns: The newly created dataset
        :rtype: Dataset

    .. method:: get_dataset(self, dataset_name: str) -> 'Dataset':

        Get a dataset from a given experiment.

        :param dataset_name: The name of the requested dataset
        :type dataset_name: str
        :returns: The requested dataset. None if it is not found.
        :rtype: Dataset. None if not found.


    .. method:: delete_dataset(self, dataset_name: str) -> None:

        Deletes a dataset and all its contents. Confirmation required.

        :param dataset_name: The name of the dataset to be deleted
        :type dataset_name: str
        :returns: None

    .. method:: query_datasets_with_metadata(self, key: str, value: any, regex: bool = False) -> list['Dataset']:

        Query all datasets in the Experiment object based on exact metadata key-value pair or using regular expressions.

        :param key: The key to be queried
        :type key: str
        :param value: The value to be queried. Supply a regular expression if the `regex` parameter is set to true. Supplying
                        a value of "*" will return all experiments with the `key` specified in the key parameter.
        :type value: any
        :returns: A list of queried datasets
        :rtype: list['Dataset']

    .. method:: get_visualization_path(self) -> str:

        Get the path to the visualization directory for the Experiment object.

        :returns: The visualization path of the experiment
        :rtype: str

    .. method:: calculate_snr(self, traces_dataset: str, intermediate_fcn: Callable, *args: any,  visualize: bool = False, save_data: bool = False, save_graph: bool = False) -> np.ndarray:

        Integrated signal-to-noise ratio metric.

        :param traces_dataset: The name of the traces dataset
        :type traces_dataset: str
        :param intermediate_fcn: A callback function that determines how the intermediate values for SNR labels are calculated.
        :type intermediate_fcn: Callable
        :param *args: Additonal datasets needed for the parameters of the intermediate_fnc.
        :type *args: any
        :param visualize: Whether to visualize the result or not
        :type visualize: bool
        :param save_data: Whether to save the metric result as a new dataset or not
        :type save_data: bool
        :param save_graph: Whether to save the visualization to the experiments visualization folder or not
        :type save_graph: bool
        :returns: The SNR metric result
        :rtype: np.ndarray

    .. method:: calculate_t_test(self, fixed_dataset: str, random_dataset: str, visualize: bool = False, save_data: bool = False, save_graph: bool = False) -> (np.ndarray, np.ndarray):

        Integrated t-test metric.

        :param fixed_dataset: The name of the dataset containing the fixed trace set
        :type fixed_dataset: str
        :param random_dataset: The name of the dataset containing the random trace set
        :type random_dataset: str
        :param visualize: Whether to visualize the result or not
        :type visualize: bool
        :param save_data: Whether to save the metric result as a new dataset or not
        :type save_data: bool
        :param save_graph: Whether to save the visualization to the experiments visualization folder or not
        :type save_graph: bool
        :returns: The t-test metric result
        :rtype: np.ndarray

    .. method:: calculate_correlation(self, predicted_dataset_name: str, observed_dataset_name: str, visualize: bool = False, save_data: bool = False, save_graph: bool = False) -> np.ndarray:

        Integrated correlation metric.

        :param predicted_dataset_name: The name of the dataset containing the predicted leakage
        :type predicted_dataset_name: str
        :param observed_dataset_name: The name of the dataset containing the observed leakage
        :type observed_dataset_name: str
        :param visualize: Whether to visualize the result or not
        :type visualize: bool
        :param save_data: Whether to save the metric result as a new dataset or not
        :type save_data: bool
        :param save_graph: Whether to save the visualization to the experiments visualization folder or not
        :type save_graph: bool
        :returns: The correlation metric result
        :rtype: np.ndarray



.. class:: Dataset

    .. method:: __init__(self, name: str, path: str, file_format_parent: FileParent, experiment_parent: Experiment, index: int, existing: bool = False, dataset: dict = None):

        Creates an Dataset object. Do not call this constructor. Please use `Experiment.add_dataset()` to
        create a new Dataset object. DO NOT USE.

    .. method:: read_data(self, start: int, end: int) -> np.ndarray:

        Read data from the dataset a specific start and end index.

        :param start: the start index of the data
        :type start: int
        :param end: the end index of the data
        :type end: int
        :returns: An NumPy array containing the requested data over the specified interval
        :rtype: np.ndarray

    .. method:: read_all(self) -> np.ndarray:

        Read all data from the dataset

        :returns: All data contained in the dataset
        :rtype: np.ndarray

    .. method:: add_data(self, data_to_add: np.ndarray, datatype: any) -> None:

        Add data to an existing dataset

        :param data_to_add: The data to be added to the dataset as a NumPy array
        :type data_to_add: np.ndarray
        :param datatype: The datatype of the data being added
        :type datatype: any
        :returns: None

    .. method:: update_metadata(self, key: str, value: any) -> None:

        Update the dataset metadata using a new key value pair.

        :param key: The key of the metadata
        :type key: str
        :param value: The value of the metadata. Can be any datatype supported by JSON.
        :type value: any
        :returns: None




