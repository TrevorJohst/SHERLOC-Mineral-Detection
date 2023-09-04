import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FuncFormatter
import copy
import os

from abc import ABC, abstractmethod

class ResultObject(ABC):
    def __init__(self):
        # Create a figure and subplot for the plot
        self.figure = plt.Figure(figsize=(5, 5), dpi=100)
        self.figure.subplots_adjust(bottom=0.15, left=0.15)
        self.result_area = self.figure.add_subplot(111)
        self.result_area.set_title(self.title)

    def export(self, save_path):
        path = os.path.join(save_path, self.title)
        self.figure.savefig(path + '.png')

class MetricPlot(ResultObject):
    def __init__(self, metric_num):
        self.title = "METRIC PLOT"
        super().__init__()

        # Visual style dictionaries
        self.facecolor = "lightcoral" if metric_num == 1 else "lightseagreen"

        self.boxprops = dict(edgecolor="black", facecolor=self.facecolor, linewidth=1.5)
        self.medianprops = dict(color="black", linewidth=1.5)
        self.whiskerprops = dict(linewidth=1.5)

    def update_boxplot(self, metric_name, metrics, metrics_labels, dark=False):
        """
        Updates the metric plot to be a boxplot.

        metric_name: string name of the metric being passed in (ex: SNR, Center, Sigma, etc)
        metrics: numpy array of numpy arrays, each inner array is a flattened array of scan location metrics
        metrics_labels: array of string labels corresponding to each metric array (ex: Dourbes, Garde, etc)
        dark: boolean flag of whether the boxplot should be light mode or dark mode defaults to False
        """
        metrics_copy = copy.deepcopy(metrics)
        # Append an additional array to the end which includes all metric data
        if len(metrics_labels) > 1:
            metrics_copy.append(np.ravel(metrics))
            metrics_labels.append("All")

        textcolor = "black"

        # Dark mode handling
        if dark:
            self.figure.set_facecolor("#2B2B2B")
            self.result_area.set_facecolor("#363636")
            self.result_area.set_title(self.title, color="white")
            self.result_area.tick_params(axis='x', colors='white')
            self.result_area.tick_params(axis='y', colors='white')

            textcolor = "white"

        # Plotting
        self.result_area.clear()

        self.result_area.boxplot(metrics_copy, boxprops=self.boxprops, medianprops=self.medianprops, whiskerprops=self.whiskerprops, capprops=self.whiskerprops, patch_artist=True)
        self.title = f"{metric_name.upper()} BOXPLOT"
        self.result_area.set_title(self.title, color=textcolor)
        self.result_area.set_ylabel(metric_name, color=textcolor)
        self.result_area.set_xticks(np.arange(1, len(metrics_labels) + 1, 1), metrics_labels, rotation=45)
        self.result_area.grid(axis='y', alpha=0.5)
        self.figure.tight_layout()

    def update_histogram(self, metric_name, metrics, bins, dark=False):
        """
        Updates the metric plot to be a histogram.

        metric_name: string name of the metric being passed in (ex: SNR, Center, Sigma, etc)
        metrics: flattened array of data that will be included in the histogram
        bins: number of bins to display the histogram with
        dark: boolean flag of whether the boxplot should be light mode or dark mode defaults to False
        """
        textcolor = "black"
        edgecolor = "white"

        # Dark mode handling
        if dark:
            self.figure.set_facecolor("#2B2B2B")
            self.result_area.set_facecolor("#363636")
            self.result_area.set_title(self.title, color="white")
            self.result_area.tick_params(axis='x', colors='white')
            self.result_area.tick_params(axis='y', colors='white')

            textcolor = "white"
            edgecolor = "#363636"

        # Plotting
        self.result_area.clear()
        
        self.result_area.hist(metrics, bins=bins, edgecolor=edgecolor, color=self.facecolor)
        self.title = f"{metric_name.upper()} HISTOGRAM"
        self.result_area.set_title(self.title, color=textcolor)
        self.result_area.set_ylabel("Count", color=textcolor)
        self.result_area.set_xlabel(metric_name, color=textcolor)
        self.result_area.grid(axis='y', alpha=0.5)
        self.result_area.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x)}"))
        self.figure.tight_layout()

class MetricHeatmap(ResultObject):
    def __init__(self, metric_num):
        self.title = "METRIC HEATMAP"
        self.metric_num = metric_num
        super().__init__()

        self.figure.subplots_adjust(bottom=0.15, left=0)

    def update_data(self, heatmap_name, metric_name, metrics, approved, image_path, loc_array, linear=True, dark=False):
        """
        Updates the heatmap with new data.

        heatmap_name: string name of the heatmap (ex: Dourbes SNR, Garde Peak Centers, etc)
        metric_name: string name of the metric being passed in (ex: SNR, Center, Sigma, etc)
        metrics: array of metric results for a single scan
        approved: list of which points were approved for the given metric array
        image_path: directory to the appropriate image in the form of a string
        loc_array: array of arrays, first array in the outer array is x coordinates and second is y coordinates
        linear: boolean value indicating if the heatmap should be linear or diverging
        dark: boolean flag of whether the boxplot should be light mode or dark mode defaults to False
        """
        textcolor = "black"

        # Dark mode handling
        if dark:
            self.figure.set_facecolor("#2B2B2B")
            self.result_area.set_facecolor("#363636")
            self.result_area.set_title(self.title, color="white")
            self.result_area.tick_params(axis='x', colors='white')
            self.result_area.tick_params(axis='y', colors='white')

            textcolor = "white"

        self.result_area.clear()

        # Set the desired minimum and maximum values for the colorbar scale
        colorbar_min = np.min(metrics)
        colorbar_max = np.max(metrics)

        # Pre-defined colormap based on position and linear vs diverging
        if linear:
            cmap = cm.plasma if self.metric_num == 1 else cm.viridis
        else:
            cmap = cm.RdBu if self.metric_num == 1 else cm.PRGn

        # Unpack locations
        x_values = loc_array[0]
        y_values = loc_array[1]

        # Plot the image
        image = plt.imread(image_path)
        self.result_area.imshow(image, aspect='auto', cmap='gray')
        self.title = heatmap_name.upper()
        self.result_area.set_title(self.title, color=textcolor)
    
        # Get the color for each value from the colormap
        normalized = (metrics - colorbar_min) / (colorbar_max - colorbar_min)
        colors = cmap(normalized)

        # Create a colorbar for the circles' colormap
        colorbar = plt.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(vmin=colorbar_min, vmax=colorbar_max), cmap=cmap), ax=self.result_area)
        colorbar.ax.tick_params(axis='both', colors=textcolor)
        colorbar.set_label(metric_name, color=textcolor, rotation=270, labelpad=10)

        # Radius of each circle, adjusted such that they will fill take up the most visual space
        heatmap_radius = (np.max(x_values) - np.min(x_values)) / 18

        # Size of padding around the points
        padding = heatmap_radius + 10

        # Calculate the extent for cropping
        extent = [np.min(x_values) - padding, np.max(x_values) + padding,
                    np.min(y_values) - padding, np.max(y_values) + padding]

        # Plot the circles
        for point_ind, x in enumerate(x_values):

            # Add a point if it is in the approved list
            if np.isin(point_ind, approved):
                # Create a circle patch
                our_ind = np.where(approved == point_ind)
                cur_color = colors[our_ind]
            
                # Set alpha to 0.4
                cur_color[0][3] = 0.4
            
                # Plot the circle with a facecolor appropriate to the colormap
                circle = plt.Circle((x_values[point_ind], y_values[point_ind]), heatmap_radius, edgecolor="none", facecolor=cur_color)

                # Add the circle patch to the plot
                self.result_area.add_artist(circle)

        # Hide axes
        self.result_area.set_xticks([])
        self.result_area.set_yticks([])
        self.result_area.set_xticklabels([])
        self.result_area.set_yticklabels([])

        # Set the axis limits to crop the image
        self.result_area.set_xlim(extent[0], extent[1])
        self.result_area.set_ylim(extent[3], extent[2])

        # Set the aspect ratio to 'equal' to preserve the square shape
        self.result_area.set_aspect('equal', adjustable='box')
        self.figure.tight_layout()

class ScatterPlot(ResultObject):
    def __init__(self):
        self.title = "SCATTERPLOT"
        super().__init__()

    def update_data(self, metric_1, metric_2, metric_name_1, metric_name_2, dark=False):
        """
        metric_1, metric_2: flattened array of data that will be included in the scatterplot
        metric_name_1, metric_name_2: string name of the metric being passed in (ex: SNR, Center, Sigma, etc)
        dark: boolean flag of whether the boxplot should be light mode or dark mode defaults to False
        """
        textcolor = "black"

        # Dark mode handling
        if dark:
            self.figure.set_facecolor("#2B2B2B")
            self.result_area.set_facecolor("#363636")
            self.result_area.set_title(self.title, color="white")
            self.result_area.tick_params(axis='x', colors='white')
            self.result_area.tick_params(axis='y', colors='white')

            textcolor = "white"

        # Plotting
        self.result_area.clear()

        self.result_area.scatter(metric_1, metric_2, color=textcolor)
        self.title = f"{metric_name_1.upper()} VS {metric_name_2.upper()}"
        self.result_area.set_title(self.title, color=textcolor)
        self.result_area.set_xlabel(metric_name_1, color=textcolor)
        self.result_area.set_ylabel(metric_name_2, color=textcolor)
        self.result_area.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.result_area.yaxis.set_major_locator(MaxNLocator(integer=True))
        self.result_area.set_aspect('equal', adjustable='box')

class SpatialPlot(ResultObject):
    def __init__(self):
        self.title = "HEATMAP ACCURATE LOCATIONS"
        super().__init__()

    def update_data(self, image_path, loc_array, scan_name, dark=False):
        """
        Updates the spatially accurate image plot.

        image_path: directory to the appropriate image in the form of a string
        loc_array: array of arrays, first array in the outer array is x coordinates and second is y coordinates
        scan_name: name of the scan (ex: sol_207-detail_1)
        dark: boolean flag of whether the boxplot should be light mode or dark mode defaults to False
        """
        textcolor = "black"

        # Dark mode handling
        if dark:
            self.figure.set_facecolor("#2B2B2B")
            self.result_area.set_facecolor("#363636")
            self.result_area.set_title(self.title, color="white")
            self.result_area.tick_params(axis='x', colors='white')
            self.result_area.tick_params(axis='y', colors='white')

            textcolor = "white"

        # Plotting
        self.result_area.clear()

        # Unpack locations
        x_values = loc_array[0]
        y_values = loc_array[1]

        # Plot the image
        image = plt.imread(image_path)
        self.result_area.imshow(image, aspect='auto', cmap='gray')
        self.title = f"{scan_name.upper()} ACCURATE LOCATIONS"
        self.result_area.set_title(self.title, color=textcolor)

        # Radius of each circle, adjusted such that they will fill take up the most visual space
        heatmap_radius = (np.max(x_values) - np.min(x_values)) / 18

        # Size of padding around the points
        padding = heatmap_radius + 10

        # Calculate the extent for cropping
        extent = [np.min(x_values) - padding, np.max(x_values) + padding,
                    np.min(y_values) - padding, np.max(y_values) + padding]

        # Plot the circles
        for point_ind, x in enumerate(x_values):
            # Always plot a point on the right image
            circle = plt.Circle((x_values[point_ind], y_values[point_ind]), 5, edgecolor='black', facecolor='none')
        
            # Add the circle patch to the plot
            self.result_area.add_artist(circle)

        # Hide axes
        self.result_area.set_xticks([])
        self.result_area.set_yticks([])
        self.result_area.set_xticklabels([])
        self.result_area.set_yticklabels([])

        # Set the axis limits to crop the image
        self.result_area.set_xlim(extent[0], extent[1])
        self.result_area.set_ylim(extent[3], extent[2])

        # Set the aspect ratio to 'equal' to preserve the square shape
        self.result_area.set_aspect('equal', adjustable='box')
        self.figure.tight_layout()