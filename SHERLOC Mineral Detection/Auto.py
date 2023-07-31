#Large data array handling
import numpy as np

#Baselining and curve fitting
import pybaselines
from scipy.optimize import curve_fit

import Helper

def stowed_arm_subtraction(y_data, noise_intensity):
    """
    Subtracts stowed arm (raw noise sample) from data, returns new array with noise sample removed.

    y_data: raw y-axis values we want to remove the noise from
    noise_intensity: numpy array of noise
    """
    new_y = y_data - noise_intensity
    return new_y

def baselining(y_data, mhw, shw):
    """
    Attempts to find a baseline of given data using pybaselines. Returns the baseline and spectrum with the
    baseline removed.
    
    y_data: y-axis of the data, the spectrum intensity
    mhw: max half window, half window size for removing noise in spectrum
    shw: smooth half window, half window size for smoothing the baseline curve
    """

    #Store a local copy of the x and y data
    spectrum = y_data
    
    #Set the first few y values to 0 (prevents massive spikes from ruining baseline)
    for i in range(60):
        spectrum[i] = 0
    
    #Generate a baseline using pybaselines and subtract it from the spectrum
    baseline = pybaselines.smooth.swima(spectrum, mhw, shw)[0]
    spectrum_baseline_removed = spectrum - baseline
        
    return baseline, spectrum_baseline_removed  

def perform_peakfit(x_data, y_data, ind1, ind2, center):
    """
    Attempts to fit a gaussian distribution to the given spectrum. Will return a tuple of fit parameters
    (amplitude, mean, sigma), full width at half max, and R squared if the fitting is successfull. If it
    is not, the function will return all zeros.

    x_data: x-axis of the data, the ramanshift
    y_data: y-axis of the data, the spectrum intensity
    ind1: lower index of the range to search for a peak within
    ind2: upper index of the range to search for a peak within
    center: estimate for the center of our spectrum peak
    """

    #Local constants
    SIGMA_GUESS = 5
    WIDTH_APPROXIMATION = 2.35
    R_SQUARED_CALC_RANGE = 2
    
    #Narrow down x and y values to ones surrounding the peak
    ind = (x_data > ind1) & (x_data < ind2)
    ramanshift = x_data[ind]
    spectrum = y_data[ind]
    
    #Initial guess for gaussian fit parameters (maximum y-value, expected mineral center, 5 sigma)
    p0 = [np.max(spectrum), center, SIGMA_GUESS]
    
    #Try to fit the curve to our data and store parameters if it works
    try:
        params = curve_fit(Helper.gauss, ramanshift, spectrum, p0=p0)[0]
    except:
        params = [0, 0, 0]

    #Extract the fitted curve parameters and caluclate full width at half maximum (FWHM)
    fit_a = params[0]
    fit_mu = params[1]
    fit_sigma = params[2]
    FWHM = WIDTH_APPROXIMATION * fit_sigma
    
    #Narrow down x and y values to ones surrounding the peak
    ind_fit = (x_data > fit_mu - fit_sigma*R_SQUARED_CALC_RANGE) & (x_data < fit_mu + fit_sigma*R_SQUARED_CALC_RANGE)
    peak_ramanshift = x_data[ind_fit]
    peak_spectrum = y_data[ind_fit]
    
    #Calculate R-Squared
    residuals = peak_spectrum - Helper.gauss(peak_ramanshift, fit_a, fit_mu, fit_sigma)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((peak_spectrum - np.mean(peak_spectrum))**2)
    r_squared = 1 - (ss_res / ss_tot) if (ss_res / ss_tot) != 0 else 0
        
    return params, FWHM, r_squared

def perform_double_peakfit(x_data, y_data, ind1, ind2, center1, center2):
    """
    Attempts to fit a double gaussian distribution to the given spectrum. Will return a tuple of fit parameters
    (amplitude1, mean1, sigma1, amplitude2, mean2, sigma2), full width at half max 1, full width at half max 2,
    and R squared if the fitting is successfull. If it is not, the function will return all zeros.

    x_data: x-axis of the data, the ramanshift
    y_data: y-axis of the data, the spectrum intensity
    ind1: lower index of the range to search for a peak within
    ind2: upper index of the range to search for a peak within
    center1: estimate for the center of our leftmost spectrum peak
    center2: estimate for the center of our rightmost spectrum peak
    """

    #Local constants
    SIGMA_GUESS = 5
    WIDTH_APPROXIMATION = 2.35
    R_SQUARED_CALC_RANGE = 2
    
    #Swap the centers if they were passed in the wrong order
    if center2 < center1:
        temp_center = center1
        center1 = center2
        center2 = temp_center
    
    #Isolate the values that fit within the specified indices and truncate both x and y to only include that data
    ind_fit = (x_data > ind1) & (x_data < ind2)
    ramanshift = x_data[ind_fit]
    spectrum = y_data[ind_fit]
   
    #Initial guess for double gaussian fit parameters (maximum y-value, expected carbonate center, 10 sigma)
    p0 = [np.max(spectrum), center1, SIGMA_GUESS, np.max(spectrum), center2, SIGMA_GUESS]
    
    #Try to fit the curve to our data and store parameters if it works
    try:
        params = curve_fit(Helper.double_gauss, ramanshift, spectrum, p0=p0)[0]
    except:
        params = [0, 0, 0, 0, 0, 0]

    #Extract the fitted curve parameters and caluclate full width at half maximum (FWHM)
    fit_a1 = params[0]
    fit_mu1 = params[1]
    fit_sigma1 = params[2]
    FWHM1 = WIDTH_APPROXIMATION * fit_sigma1
    
    fit_a2 = params[3]
    fit_mu2 = params[4]
    fit_sigma2 = params[5]
    FWHM2 = WIDTH_APPROXIMATION * fit_sigma2
    
    #Narrow down x and y values to ones surrounding the peak
    ind_fit = (x_data > fit_mu1 - fit_sigma1*R_SQUARED_CALC_RANGE) & (x_data < fit_mu2 + fit_sigma2*R_SQUARED_CALC_RANGE)
    peak_ramanshift = x_data[ind_fit]
    peak_spectrum = y_data[ind_fit]
    
    #Calculate R-Squared
    residuals = peak_spectrum - Helper.double_gauss(peak_ramanshift, fit_a1, fit_mu1, fit_sigma1, fit_a2, fit_mu2, fit_sigma2)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((peak_spectrum - np.mean(peak_spectrum))**2)
    r_squared = 1 - (ss_res / ss_tot) if (ss_res / ss_tot) != 0 else 0
        
    return params, FWHM1, FWHM2, r_squared

def calculate_SNR_stowed_arm(x_data, noise_intensity, fit_a, ind1, ind2):
    """
    Calculates and returns the signal-to-noise ratio for the given data using a stowed arm noise scan.
    
    x_data: x-axis of the data, the ramanshift
    noise_intensity: numpy array of noise
    fit_a: amplitude of our normal curve we want to compare the noise to
    ind1: lower index of the range to characterize noise within
    ind2: upper index of the range to characterize noise within
    """
    
    #Narrow the noise down to the region around our scan
    delta_ind = ind2 - ind1
    ind_SNR = (x_data > ind1 - delta_ind) & (x_data < ind2 + delta_ind)
    noise = noise_intensity[ind_SNR]
    
    #Calculate standard deviation of the noise and use it to find signal-noise ratio
    sigmay = np.std(noise)
    SNR = fit_a / sigmay
        
    return SNR