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
    baseline = pybaselines.smooth.swima(spectrum, max_half_window=mhw, smooth_half_window=shw)[0]
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

def perform_double_peakfit(x_data, y_data, ind1, ind2, focus_center, other_center):
    """
    Attempts to fit a double gaussian distribution to the given spectrum. Will return tuples of fit parameters
    (amplitude, mean, sigma) for the focus peak, (amplitude, mean, sigma) for the other peak, 
    focus full width at half max, and R squared if the fitting is successfull. 
    If it is not, the function will return all zeros.

    x_data: x-axis of the data, the ramanshift
    y_data: y-axis of the data, the spectrum intensity
    ind1: lower index of the range to search for a peak within
    ind2: upper index of the range to search for a peak within
    focus_center: estimate for the center of our focused spectrum peak
    other_center: estimate for the center of our other spectrum peak
    """

    #Local constants
    SIGMA_GUESS = 5
    WIDTH_APPROXIMATION = 2.35
    R_SQUARED_CALC_RANGE = 2
    
    #Swap the centers if they were passed in the wrong order
    if other_center < focus_center:
        center1 = other_center
        center2 = focus_center
        focus_left = False
    else:
        center1 = focus_center
        center2 = other_center
        focus_left = True
    
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
        
    if focus_left:
        return [fit_a1, fit_mu1, fit_sigma1], [fit_a2, fit_mu2, fit_sigma2], FWHM1, r_squared
    else:
        return [fit_a2, fit_mu2, fit_sigma2], [fit_a1, fit_mu1, fit_sigma1], FWHM2, r_squared

def calculate_SNR_stowed_arm(x_data, noise_intensity, fit_a, center):
    """
    Calculates and returns the signal-to-noise ratio for the given data using a stowed arm noise scan.
    
    x_data: x-axis of the data, the ramanshift
    noise_intensity: numpy array of noise
    fit_a: amplitude of our normal curve we want to compare the noise to
    center: location of the peak center
    """
    
    #Narrow the noise down to the region around our scan
    ind_SNR = (x_data > max(center - 200, 700)) & (x_data < center + 200)
    noise = noise_intensity[ind_SNR]
    
    #Calculate standard deviation of the noise and use it to find signal-noise ratio
    sigmay = np.std(noise)
    SNR = fit_a / sigmay
        
    return SNR

def calculate_SNR_silent_region(x_data, y_data, fit_a):
    """
    Calculates and returns the signal-to-noise ratio for the given data using the silent region.
    
    x_data: x-axis of the data, the ramanshift
    y_data: y-axis of the data, the spectrum intensity
    fit_a: amplitude of our normal curve we want to compare the noise to
    """
    
    #Isolate all x values that fall within the silent region
    ind_silent = (x_data > 2000) & (x_data < 2100)
    spectrum = y_data[ind_silent]
    
    #Calculate standard deviation of the noise and use it to find signal-noise ratio
    sigmay = np.std(spectrum)
    SNR = fit_a / sigmay
        
    return SNR