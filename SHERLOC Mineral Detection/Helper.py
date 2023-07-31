import pandas as pd
import numpy as np

def gauss(x, A, mu, sigma):
    """
    Evaluates a gaussian distribution at a given point from a set of parameters.
    
    x: x-axis value you want the function evaluated at
    A: amplitude
    mu: mean/center of the distribution
    sigma: standard deviation
    """
    return A * np.exp(-(x-mu)**2 / (2. * sigma**2))

def double_gauss(x, A1, mu1, sigma1, A2, mu2, sigma2):
    """
    Evaluates a double gaussian distribution at a given point from a set of parameters.
    
    x: x-axis value you want the function evaluated at
    A1: amplitude of the first gaussian
    mu1: mean/center of the first distribution
    sigma1: standard deviation of the first gaussian
    A2: amplitude of the second gaussian
    mu2: mean/center of the second distribution
    sigma2: standard deviation second
    """
    return gauss(x, A1, mu1, sigma1) + gauss(x, A2, mu2, sigma2)

def process_ZNZ_dataframe(file_path):
    """
    Takes in a file path to a Full Map ZNZ csv file. Returns an array of ramanshift 
    and a dataframe of spectrums for that file. Assumes the file path does exist.

    file_path: string with directory to a ZNZ csv file
    """
    sample_df = pd.read_csv(file_path)

    # First columns we can drop to only access data
    drop_list = ['CCD pixel','wavelength (nm)','Raman shift (cm-1)']

    # Store ramanshift for x-axis usage, same for all data sets
    ramanshift = np.array(sample_df['Raman shift (cm-1)'])

    # Prepare sample dataframe for use
    sample_df.drop(drop_list, axis=1, inplace=True)

    samples = np.array(sample_df.values.T.tolist())

    return ramanshift, samples