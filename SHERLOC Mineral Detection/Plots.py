import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from abc import ABC, abstractmethod

import Helper

class PlotObject(ABC):
    def __init__(self, master):

        # Store the master object
        self.master = master

        # Create a figure and subplot for the plot
        self.figure = plt.Figure(figsize=(6, 5), dpi=100, facecolor="#2B2B2B")
        self.figure.subplots_adjust(bottom=0.15)
        self.plot_area = self.figure.add_subplot(111)
        self.plot_area.set_facecolor("#363636")
        self.plot_area.set_title(self.title, color="white")
        self.plot_area.tick_params(axis='x', colors='white')
        self.plot_area.tick_params(axis='y', colors='white')
        self.plot_area.set_xlabel("Ramanshift (cm⁻¹)", color="white")

        # Create a canvas to display the plot
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)

    @abstractmethod
    def update_data(self, ramanshift, spectrum):
        pass

class BaselinePlot(PlotObject):
    def __init__(self, master):
        self.title = "BASELINE REMOVAL"        

        # Store the master object
        self.master = master
        
        self.figure = plt.Figure(figsize=(6, 4), dpi=100, facecolor="#2B2B2B")
        self.figure.subplots_adjust(bottom=0.15, hspace=0.3)
        self.plot_area = self.figure.add_subplot(211)
        self.plot_area.set_facecolor("#363636")
        self.plot_area.set_title(self.title, color="white")
        self.plot_area.tick_params(axis='x', colors='white')
        self.plot_area.tick_params(axis='y', colors='white')
        self.bottom_plot_area = self.figure.add_subplot(212)
        self.bottom_plot_area.set_facecolor("#363636")
        self.bottom_plot_area.tick_params(axis='x', colors='white')
        self.bottom_plot_area.tick_params(axis='y', colors='white')     
        self.bottom_plot_area.set_xlabel("Ramanshift (cm⁻¹)", color="white")
        
        # Create a canvas to display the plot
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=0, ipadx=0, pady=20)

    def update_data(self, ramanshift, spectrum, baseline, ind1, ind2):
        """
        Updates the baseline plot data

        ramanshift: x axis data, the ramanshift array
        spectrum: y axis data, the intensity, after the baseline was removed
        baseline: the baseline of the spectrum passed above
        ind1: lower bound of focus range
        ind2: upper bound of focus range
        """
        self.plot_area.clear()
        self.plot_area.plot(ramanshift, spectrum + baseline, label="Original Spectrum", lw=0.5, color="white")
        self.plot_area.plot(ramanshift, baseline, label="Baseline", lw=0.5, color="#B00020")
        self.plot_area.set_xlim(250, 4000)
        self.plot_area.set_ylim(-800, 800)
        self.plot_area.set_title(self.title, color="white")
        self.plot_area.tick_params(axis='x', colors='white')
        self.plot_area.tick_params(axis='y', colors='white')
        self.plot_area.legend(framealpha=0.0, labelcolor="white", loc="lower right")

        # Isolate all x values that fall within the indices
        ind = (ramanshift > max(ind1 - 1500, 250)) & (ramanshift < ind2 + 1500)

        self.bottom_plot_area.clear()
        self.bottom_plot_area.plot(ramanshift[ind], spectrum[ind] + baseline[ind], label="Original Spectrum", lw=0.5, color="white")
        self.bottom_plot_area.plot(ramanshift[ind], baseline[ind], label="Baseline", lw=0.5, color="#B00020")
        self.bottom_plot_area.set_xlim(max(ind1 - 1500, 250), ind2 + 1500)
        self.bottom_plot_area.tick_params(axis='x', colors='white')
        self.bottom_plot_area.tick_params(axis='y', colors='white')
        self.bottom_plot_area.set_xlabel("Ramanshift (cm⁻¹)", color="white")
        self.canvas.draw()

class NoisePlot(PlotObject):
    def __init__(self, master):
        self.title = "NOISE SAMPLING"

        # Store the master object
        self.master = master
        
        self.figure = plt.Figure(figsize=(6, 4), dpi=100, facecolor="#2B2B2B")
        self.figure.subplots_adjust(bottom=0.15, hspace=0.3)
        self.plot_area = self.figure.add_subplot(211)
        self.plot_area.set_facecolor("#363636")
        self.plot_area.set_title(self.title, color="white")
        self.plot_area.tick_params(axis='x', colors='white')
        self.plot_area.tick_params(axis='y', colors='white')
        self.bottom_plot_area = self.figure.add_subplot(212)
        self.bottom_plot_area.set_facecolor("#363636")
        self.bottom_plot_area.tick_params(axis='x', colors='white')
        self.bottom_plot_area.tick_params(axis='y', colors='white')     
        self.bottom_plot_area.set_xlabel("Ramanshift (cm⁻¹)", color="white")

        self.ax_right = self.plot_area.twinx()
        self.ax_right.tick_params(axis='y', colors="#03DAC5", which='both')
        self.ax_right.set_yticks([])
        self.bottom_ax_right = self.bottom_plot_area.twinx()
        self.bottom_ax_right.set_yticks([])
        self.bottom_ax_right.tick_params(axis='y', colors="#03DAC5", which='both')
        
        # Create a canvas to display the plot
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.get_tk_widget().grid(row=1, column=0, padx=0, ipadx=0, pady=20)

    def update_data(self, ramanshift, spectrum, noise, center):
        """
        Updates the zoomed baseline plot data

        ramanshift: x axis data, the ramanshift array
        spectrum: y axis data, the intensity, after the baseline was removed
        noise: y axis data for the noise sample
        center: location of the peak center
        """
        # Isolate all x values that fall within the silent region
        ind_silent = (ramanshift > 2000) & (ramanshift < 2100)
        
        # Isolate all x values that fall in the region around our scan
        ind_stowed = (ramanshift > max(center - 200, 700)) & (ramanshift < center + 200)

        self.plot_area.clear()
        self.plot_area.plot(ramanshift[ind_silent], spectrum[ind_silent], label="Silent Region", lw=0.5, color="white")
        self.plot_area.axhline(np.std(spectrum[ind_silent]), color="#03DAC5", lw=0.5, label="STD")
        self.plot_area.set_xlim(2000, 2100)
        self.plot_area.set_title(self.title, color="white")
        self.plot_area.tick_params(axis='x', colors='white')
        self.plot_area.tick_params(axis='y', colors='white')
        self.plot_area.legend(framealpha=0.0, labelcolor="white", loc="lower right")

        self.ax_right.set_yticks([np.std(spectrum[ind_silent])])
        self.ax_right.yaxis.tick_right()
        self.ax_right.set_ylim(self.plot_area.get_ylim())

        self.bottom_plot_area.clear()
        self.bottom_plot_area.plot(ramanshift[ind_stowed], noise[ind_stowed], label="Stowed Arm", lw=0.5, color="white")
        self.bottom_plot_area.axhline(np.std(noise[ind_stowed]), color="#03DAC5", lw=0.5, label="STD")
        self.bottom_plot_area.set_xlim(max(center - 200, 700), center + 200)
        self.bottom_plot_area.tick_params(axis='x', colors='white')
        self.bottom_plot_area.tick_params(axis='y', colors='white')
        self.bottom_plot_area.legend(framealpha=0.0, labelcolor="white", loc="lower right")
        self.bottom_plot_area.set_xlabel("Ramanshift (cm⁻¹)", color="white")        
        
        self.bottom_ax_right.set_yticks([np.std(noise[ind_stowed])])
        self.bottom_ax_right.yaxis.tick_right()
        self.bottom_ax_right.set_ylim(self.bottom_plot_area.get_ylim())

        self.canvas.draw()

class CosmicRayPlot(PlotObject):
    def __init__(self, master):
        self.title = "COSMIC RAY REMOVAL"
        super().__init__(master)
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=0, ipadx=0, pady=20)
        self.ax_top = self.plot_area.twiny()
        self.ax_top.tick_params(axis='x', colors="#B00020", which='both', pad=50, bottom=False, top=False, rotation=90)

    def update_data(self, ramanshift, spectrum, lower_display, upper_display, lower_ray_index, upper_ray_index):
        """
        Updates the cosmic ray plot data

        ramanshift: x axis data, the ramanshift array
        spectrum: y axis data, the intensity, before the baseline was removed
        lower_ray_index: lower x value index of the cosmic ray
        upper_ray_index: upper x value index of the cosmic ray
        """
        # Isolate all x values that fall within the indices
        ind = (ramanshift > lower_display) & (ramanshift < upper_display)

        self.plot_area.clear()
        self.plot_area.plot(ramanshift[ind], spectrum[ind], label="Spectrum", lw=0.5, color="white")
        self.plot_area.axvspan(ramanshift[lower_ray_index], ramanshift[upper_ray_index], label="Ray", facecolor="#B00020", alpha=0.3)
        
        self.ax_top.set_xticks([round(ramanshift[lower_ray_index], 0), round(ramanshift[upper_ray_index], 0)])
        x_tick_labels = self.ax_top.get_xticklabels()
        x_tick_labels[0].set_y(-0.26)
        x_tick_labels[1].set_y(-0.26)
        self.ax_top.tick_params(axis='x', colors="#B00020", which='both', pad=50, bottom=False, top=False, rotation=90)
        self.ax_top.set_xlim(lower_display, upper_display)

        self.plot_area.set_xlim(lower_display, upper_display)
        self.plot_area.set_title(self.title, color="white")
        self.plot_area.tick_params(axis='x', colors='white')
        self.plot_area.tick_params(axis='y', colors='white')
        self.plot_area.legend(framealpha=0.0, labelcolor="white", loc="upper right")
        self.plot_area.set_xlabel("Ramanshift (cm⁻¹)", color="white")
        self.canvas.draw()

class PeakfitPlot(PlotObject):
    def __init__(self, master):
        self.title = "PEAKFITTING"
        super().__init__(master)
        self.canvas.get_tk_widget().grid(row=1, column=1, padx=0, ipadx=0, pady=20)

    def update_data(self, ramanshift, spectrum, peak_params, ind1, ind2, other_params=None):
        """
        Update the peakfit plot data

        ramanshift: x axis data, the ramanshift array
        spectrum: y axis data, the intensity, after the baseline was removed
        peak_params: gaussian curve fit parameters for the curve
        ind1: lower bound of focus range
        ind2: upper bound of focus range
        other_params: optional parameters to display a double curve fit instead
        """
        # Isolate all x values that fall within the indices
        lower = max(ind1 - 250, 250)
        upper = min(ind2 + 250, 4000)
        ind = (ramanshift > lower) & (ramanshift < upper)
            
        #x data for plotting gaussian curve
        gauss_x = np.arange(lower, upper, 1)
        gauss_y = Helper.gauss(gauss_x, peak_params[0], peak_params[1], peak_params[2])

        self.plot_area.clear()
        self.plot_area.plot(ramanshift[ind], spectrum[ind], label="Spectrum", lw=0.5, color="white")
        self.plot_area.axhline(peak_params[0], color="#03DAC5", lw=0.5, label="Peak Location")
        self.plot_area.axvline(peak_params[1], color="#03DAC5", lw=0.5)
        
        # Plot like normal if no other parameters, otherwise plot double
        if other_params is None:
            self.plot_area.plot(gauss_x, gauss_y, label="Gaussian Fit", lw=1, color="#B00020")
        else:
            gauss_y2 = Helper.gauss(gauss_x, other_params[0], other_params[1], other_params[2])
            double_gauss = Helper.double_gauss(gauss_x, peak_params[0], peak_params[1], peak_params[2], other_params[0], other_params[1], other_params[2])
            
            self.plot_area.plot(gauss_x, gauss_y, lw=0.5, color="#BB86FC", linestyle='--')
            self.plot_area.plot(gauss_x, gauss_y2, lw=0.5, color="#BB86FC", linestyle='--') 
            self.plot_area.plot(gauss_x, double_gauss, lw=1, label="Double Gaussian Fit", color="#B00020") 

        self.plot_area.set_xlim(lower, upper)
        self.plot_area.set_ylim(-150, None)
        self.plot_area.set_title(self.title, color="white")
        self.plot_area.tick_params(axis='x', colors='white')
        self.plot_area.tick_params(axis='y', colors='white')
        self.plot_area.legend(framealpha=0.0, labelcolor="white", loc="upper right")
        self.plot_area.set_xlabel("Ramanshift (cm⁻¹)", color="white")
        self.canvas.draw()