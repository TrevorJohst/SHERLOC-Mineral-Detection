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
        self.figure = plt.Figure(figsize=(6, 4), dpi=100, facecolor="#2B2B2B")
        self.plot_area = self.figure.add_subplot(111)
        self.plot_area.set_facecolor("#363636")
        self.plot_area.set_title(self.title, color="white")
        self.plot_area.tick_params(axis='x', colors='white')
        self.plot_area.tick_params(axis='y', colors='white')

        # Create a canvas to display the plot
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)

    @abstractmethod
    def update_data(self, ramanshift, spectrum):
        pass

class BaselinePlot(PlotObject):
    def __init__(self, master):
        self.title = "BASELINE REMOVAL"
        super().__init__(master)
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=0, ipadx=0, pady=20)

    def update_data(self, ramanshift, spectrum, baseline):
        """
        Updates the baseline plot data

        ramanshift: x axis data, the ramanshift array
        spectrum: y axis data, the intensity, after the baseline was removed
        baseline: the baseline of the spectrum passed above
        """
        self.plot_area.clear()
        self.plot_area.plot(ramanshift, spectrum + baseline, label="Original Spectrum", lw=0.5, color="white")
        self.plot_area.plot(ramanshift, baseline, label="Baseline", lw=0.5, color="#B00020")
        self.plot_area.set_xlim(0, 4000)
        self.plot_area.set_ylim(-800, 800)
        self.plot_area.set_title(self.title, color="white")
        self.plot_area.tick_params(axis='x', colors='white')
        self.plot_area.tick_params(axis='y', colors='white')
        self.plot_area.legend(facecolor="#2B2B2B", edgecolor="white", labelcolor="white")
        self.canvas.draw()

class ZoomedBaselinePlot(PlotObject):
    def __init__(self, master):
        self.title = "ZOOMED BASELINE REMOVAL"
        super().__init__(master)
        self.canvas.get_tk_widget().grid(row=1, column=0, padx=0, ipadx=0, pady=5)

    def update_data(self, ramanshift, spectrum, baseline, ind1, ind2):
        """
        Updates the zoomed baseline plot data

        ramanshift: x axis data, the ramanshift array
        spectrum: y axis data, the intensity, after the baseline was removed
        baseline: the baseline of the spectrum passed above
        ind1: lower bound of focus range
        ind2: upper bound of focus range
        """
        # Isolate all x values that fall within the indices
        ind = (ramanshift > ind1 - 1500) & (ramanshift < ind2 + 1500)

        self.plot_area.clear()
        self.plot_area.plot(ramanshift[ind], spectrum[ind] + baseline[ind], label="Original Spectrum", lw=0.5, color="white")
        self.plot_area.plot(ramanshift[ind], baseline[ind], label="Baseline", lw=0.5, color="#B00020")
        self.plot_area.set_xlim(max(ind1 - 1500, 0), ind2 + 1500)
        self.plot_area.set_title(self.title, color="white")
        self.plot_area.tick_params(axis='x', colors='white')
        self.plot_area.tick_params(axis='y', colors='white')
        self.plot_area.legend(facecolor="#2B2B2B", edgecolor="white", labelcolor="white")
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
        self.plot_area.legend(facecolor="#2B2B2B", edgecolor="white", labelcolor="white")
        self.canvas.draw()

class PeakfitPlot(PlotObject):
    def __init__(self, master):
        self.title = "PEAKFITTING"
        super().__init__(master)
        self.canvas.get_tk_widget().grid(row=1, column=1, padx=0, ipadx=0, pady=5)

    def update_data(self, ramanshift, spectrum, peak_params, ind1, ind2):
        """
        Update the peakfit plot data

        ramanshift: x axis data, the ramanshift array
        spectrum: y axis data, the intensity, after the baseline was removed
        gauss_y: y axis data for the gaussian fit
        ind1: lower bound of focus range
        ind2: upper bound of focus range
        """
        # Isolate all x values that fall within the indices
        ind = (ramanshift > ind1) & (ramanshift < ind2)
            
        #x data for plotting gaussian curve
        gauss_x = np.arange(ind1, ind2, 1)
        gauss_y = Helper.gauss(gauss_x, peak_params[0], peak_params[1], peak_params[2])

        self.plot_area.clear()
        self.plot_area.plot(ramanshift[ind], spectrum[ind], label="Spectrum", lw=0.5, color="white")
        self.plot_area.axhline(peak_params[0], color="#03DAC5", lw=0.5, label="Peak Location")
        self.plot_area.axvline(peak_params[1], color="#03DAC5", lw=0.5)
        self.plot_area.plot(gauss_x, gauss_y, label="Gaussian Fit", lw=1, color="#B00020")
        self.plot_area.set_xlim(ind1, ind2)
        self.plot_area.set_title(self.title, color="white")
        self.plot_area.tick_params(axis='x', colors='white')
        self.plot_area.tick_params(axis='y', colors='white')
        self.plot_area.legend(facecolor="#2B2B2B", edgecolor="white", labelcolor="white")
        self.canvas.draw()