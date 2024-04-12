Custom File Framework
==================
The file framework is split into three separate classes.

.. class:: FileParent

    The base directory for

    .. method:: __init__(self, name: str, path: str, existing: bool = False):

        Initialize FileFormatParent class. Creates the basic file structure including JSON metadata holder. If the file
        already exists it simply returns a reference to that file.

    .. method:: update_metadata(self, key: str, value: str) -> None:

        Update file JSON metadata with key value pair


    .. method:: read_metadata(self) -> dict:

        Read JSON metadata from file

    .. methood:: add_experiment(self, name: str) -> 'Experiment':

        Adds a new experiment to the FileParent object

    .. method:: get_experiment(self, experiment_name: str) -> 'Experiment':

        Get an existing experiment from the FileParent

    .. method:: delete_file(self) -> None:

        Deletes the entire file. Confirmation required.

    .. method:: delete_experiment(self, experiment_name: str) -> None:

        Deletes an experiment and all of its datasets from a FileParent. Confirmation Required.

    .. method:: query_experiments_with_metadata(self, key: str, value: str, regex: bool = False) -> list['Experiment']:

        Query all experiments in the FileParent object based on exact metadata key-value pair or using regular expressions.

.. class:: Experiment

    .. method:: __init__(self, name: str, path: str, file_format_parent: FileParent, existing: bool = False, index: int = 0, experiment: dict = None):

        Creates an Experiment object. Do not call this constructor. Please use `FileParent.add_experiment()` to
        create a new Experiment object.

    .. method:: update_metadata(self, key: str, value: str) -> None:

        Update experiment metadata with a new key value pair

    .. method:: read_metadata(self) -> dict:

        Reads experiment metadata

    .. method:: add_dataset(self, name: str, data_to_add: np.ndarray | list, datatype: any) -> 'Dataset':

        Adds a new Dataset to a given Experiment

    .. method:: get_dataset(self, dataset_name: str) -> 'Dataset':

        Get a dataset from a given experiment.

    .. method:: delete_dataset(self, dataset_name: str) -> None:

        Deletes a dataset and all its contents. Confirmation required.

    .. method:: query_datasets_with_metadata(self, key: str, value: str, regex: bool = False) -> list['Dataset']:

        Query all experiments in the Experiment object based on exact metadata key-value pair or using regular expressions.

    .. method:: get_visualization_path(self) -> str:

        Get the path to the visualization directory for the Experiment object.

    .. method:: calculate_snr(self, traces_dataset: str, intermediate_fcn: Callable, *args: any,  visualize: bool = False, save_data: bool = False, save_graph: bool = False) -> np.ndarray:

        Integrated signal-to-noise ratio metric.

    .. method:: calculate_t_test(self, fixed_dataset: str, random_dataset: str, visualize: bool = False, save_data: bool = False, save_graph: bool = False) -> (np.ndarray, np.ndarray):

        Integrated t-test metric.

    .. method:: calculate_correlation(self, predicted_dataset_name: str, observed_dataset_name: str, visualize: bool = False, save_data: bool = False, save_graph: bool = False) -> np.ndarray:

        Integrated correlation metric.




