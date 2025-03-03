from math import sqrt
import numpy as np
from scipy.stats import ttest_ind

def ttest_experiment_running(experiment, length=0):
    """
    Computes a running Welch's t-test on an experiment's dataset.
    
    Parameters:
    experiment : object
        The experiment object containing datasets.
    length : int, optional
        The number of dataset pairs to process (default is full dataset length).
    
    Returns:
    welsh_t : ndarray
        The final t-test statistic values.
    """
    # Initialize variables
    welsh_t = []
    new_mr, new_mf, new_sf, new_sr = [], [], [], []
    number = 0

    # Determine the number of datasets to process
    if length == 0:
        length = len(experiment.dataset)
    
    # Process datasets in pairs
    for exp_len in range(int(length / 2)):
        fixed_traces = experiment.get_dataset(f"fixed_traces_p{exp_len}").read_all()
        random_traces = experiment.get_dataset(f"random_traces_p{exp_len}").read_all()

        # Compute t-test for each trace in the dataset
        for k in range(len(random_traces)):
            welsh_t, new_mr, new_mf, new_sf, new_sr = running_ttest(
                new_mf, new_mr, new_sf, new_sr, fixed_traces[k], random_traces[k], number
            )
            number += 1

        # Clean up memory
        del fixed_traces
        del random_traces
    
    return welsh_t

def ttest_experiment_standard(experiment, length=0):
    """
    Computes a standard Welch's t-test on an experiment's dataset.
    
    Parameters:
    experiment : object
        The experiment object containing datasets.
    length : int, optional
        The number of dataset pairs to process (default is full dataset length).
    
    Returns:
    t_stat : ndarray
        The t-test statistic values.
    """
    if length == 0:
        length = len(experiment.dataset) // 2
    
    # Process single dataset case
    if length == 1:
        fixed_traces = experiment.get_dataset("fixed_traces_p0").read_all()
        random_traces = experiment.get_dataset("random_traces_p0").read_all()
        return ttest_ind(fixed_traces, random_traces, axis=0, equal_var=False)[0]
    
    # Process multiple datasets
    fixed_tracestack = experiment.get_dataset("fixed_traces_p0").read_all()
    random_tracestack = experiment.get_dataset("random_traces_p0").read_all()
    
    for exp_len in range(1, int(length)):
        fixed_traces = experiment.get_dataset(f"fixed_traces_p{exp_len}").read_all()
        random_traces = experiment.get_dataset(f"random_traces_p{exp_len}").read_all()
        fixed_tracestack = np.vstack((fixed_tracestack, fixed_traces))
        random_tracestack = np.vstack((random_tracestack, random_traces))
    
    return ttest_ind(fixed_tracestack, random_tracestack, axis=0, equal_var=False)[0]

def running_ttest(mf_old, mr_old, sf_old, sr_old, new_tf, new_tr, n):
    """
    Computes a running Welch's t-test statistic for streaming data.
    
    Parameters:
    mf_old, mr_old : ndarray
        Previous mean values for fixed and random traces.
    sf_old, sr_old : ndarray
        Previous sum of squared deviations for fixed and random traces.
    new_tf, new_tr : ndarray
        New data points (fixed and random traces).
    n : int
        The number of previous samples processed.
    
    Returns:
    welsh_t : ndarray
        The current Welch's t-test statistic.
    new_mr, new_mf : ndarray
        Updated mean values.
    new_sf, new_sr : ndarray
        Updated sum of squared deviations.
    """
    if n == 0:
        # Initialize means and sum of squares
        new_mf, new_mr = new_tf, new_tr
        new_sf = new_tf - new_mf
        new_sr = new_tr - new_mr
        welsh_t = new_sf  # Placeholder for initial t-values
    else:
        # Update means
        new_mf = mf_old + (new_tf - mf_old) / (n + 1)
        new_mr = mr_old + (new_tr - mr_old) / (n + 1)
        
        # Update sum of squared deviations
        new_sf = sf_old + (new_tf - mf_old) * (new_tf - new_mf)
        new_sr = sr_old + (new_tr - mr_old) * (new_tr - new_mr)
        
        # Compute standard deviations
        new_stdf = np.sqrt(new_sf / n)
        new_stdr = np.sqrt(new_sr / n)
        
        # Compute Welch's t-test statistic
        welsh_t = (new_mf - new_mr) / np.sqrt((new_stdf**2) / (n + 1) + (new_stdr**2) / (n + 1))
    
    return welsh_t, new_mr, new_mf, new_sf, new_sr
