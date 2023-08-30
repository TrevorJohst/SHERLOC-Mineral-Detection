import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import math
import os
import threading
from collections import defaultdict

import Plots
import Auto
import Helper
import Results

class MainApp:
    def __init__(self, root):
        """
        Initializes the application window.

        root: a tkinter tk object
        """
        # Unpack user settings
        user_path = os.path.join(os.getcwd(), "User")
        settings_path = os.path.join(user_path, "Settings.csv")
        settings_df = pd.read_csv(settings_path)

        # Parameter constants
        self.SNR_THRESHOLD = settings_df["SNR_THRESHOLD"][0]
        self.R_SQUARED_THRESHOLD = settings_df["R_SQUARED_THRESHOLD"][0]
        self.FWHM_MIN = settings_df["FWHM_MIN"][0]
        self.FWHM_MAX = settings_df["FWHM_MAX"][0]
        self.CENTER_RANGE = settings_df["CENTER_RANGE"][0]
        self.MHW = settings_df["SAMPLING"][0]
        self.SHW = settings_df["SMOOTHING"][0]
        self.MINERAL_NAME = settings_df["MINERAL_NAME"][0]
        self.CENTER = settings_df["CENTER"][0]

        # Load in the user selected noise dataframe
        folder_path = os.path.join(user_path, "Noise")
        folder_path = os.path.join(folder_path, settings_df["NOISE_SAMPLE"][0] + ".csv")
        self.noise_df = pd.read_csv(folder_path)

        # Result dataframes setup
        result_dict = {
            "Point" : [],
            "Height" : [],
            "Height STD" : [],
            "Mean" : [],
            "Mean STD" : [],
            "Sigma" : [],
            "Sigma STD": [],
            "FWHM" : [],
            "R^2" : [],
            "Stowed SNR" : [],
            "Silent SNR" : []
        }

        self.fresh_df = pd.DataFrame(result_dict)
        self.approved_result_df = pd.DataFrame(result_dict)
        self.denied_result_df = pd.DataFrame(result_dict)

        # Instance variables and root setup
        self.file_pressed = False
        self.file_selected = None
        self.ind1 = self.CENTER - 150
        self.ind2 = self.CENTER + 150
        self.root = root
        self.root.title("SHERLOC Mineral Detection")
        self.root.state('zoomed')
        self.root.config(bg="#2B2B2B")
        self.groups = {}

        # Threading button interrupt setup
        self.button_event = threading.Event()

        # Create a main frame to hold the buttons and plots
        self.main_frame = tk.Frame(self.root, bg="#2B2B2B")
        self.main_frame.grid(row=0, column=0, sticky='news')

        # Center the main frame within the window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Start the program by showing the selection screen
        self.show_buttons()

    def _toggle_buttons(self, state):
        """
        Helper function that will change the state of the selection buttons.

        state: a tk state you wish to set the buttons to, tk.NORMAL or tk.DISABLED
        """
        self.baseline_button.config(state=state)
        self.cosmic_button.config(state=state)
        self.peakfit_button.config(state=state)
        self.double_peakfit_button.config(state=state)
        self.approve_button.config(state=state)
        self.deny_button.config(state=state)

    def _update_data(self):
        """
        Helper function that updates the data label with current information.
        """
        std = np.sqrt(np.diag(self.cov))
        std = [x if x <= 10000 else np.nan for x in std]
        self.data_label.config(text=f"CURRENT DATA\n\nHeight: {round(self.peak_params[0], 1)} \u00B1\n{round(std[0], 1)}\n\nMean: {round(self.peak_params[1], 1)} \u00B1\n{round(std[1], 1)}\n\nSigma: {round(self.peak_params[2], 1)} \u00B1\n{round(std[2], 1)}\n\nFWHM: {round(self.FWHM, 1)}\n\nR\u00B2 : {round(self.r_squared, 4)}\n\nStow SNR: {round(self.SNR_stowed, 2)}\n\nSilent SNR: {round(self.SNR_silent, 2)}\n\nSampling: {self.sampling}\n\nSmoothing: {self.smoothing}\n\n")

    def show_buttons(self):
        """
        Displays the selection screen to the user. Allows them to load a sample file and select a scan type.
        """
        def select_file():
            """
            Function called when the file button is pressed 
            """
            # Prompt user for a full map file
            file_selected = tk.filedialog.askopenfilename(title='Select the Full Map File', parent=root)

            # Only update stored file if user selected a file
            if file_selected != "":
                # Update the button flag
                self.file_pressed = True

                # Store the file path if it is a valid full map csv file
                if "Full Map_spectra" in file_selected and file_selected.lower().endswith(".csv"):
                    self.file_selected = file_selected
                else:
                    self.file_selected = None

            # Update the buttons
            self.show_buttons()

        # Clear anything in the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Set button grids
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid_rowconfigure(5, weight=1)
        self.main_frame.grid_rowconfigure(6, weight=1)
        self.main_frame.grid_rowconfigure(7, weight=1)
        self.main_frame.grid_rowconfigure(8, weight=1)
        self.main_frame.grid_rowconfigure(9, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Scan type button handling
        button1 = tk.Button(self.main_frame, text="Automatic Check", command=lambda: self.show_plots(1), bg="#424242", fg="white", font=("Arial", 20), width=30)
        button1.grid(row=6, column=0, pady=0)
        button2 = tk.Button(self.main_frame, text="Semi-Automatic Check", command=lambda: self.show_plots(2), bg="#424242", fg="white", font=("Arial", 20), width=30)
        button2.grid(row=7, column=0, pady=0)
        button3 = tk.Button(self.main_frame, text="Manual Check", command=lambda: self.show_plots(3), bg="#424242", fg="white", font=("Arial", 20), width=30)
        button3.grid(row=8, column=0, pady=0)            
        
        # File selection label
        text_label = tk.Label(self.main_frame, text="\n", bg="#2B2B2B", fg="white", font=("Arial", 10))
        text_label.grid(row=5, column=0, pady=0)

        # Make changes if the folder select button was never pressed
        if self.file_selected is None:
            button0_color = "#B00020"
            
            # Disable the other buttons until you select a file
            button1.config(state=tk.DISABLED)
            button2.config(state=tk.DISABLED)
            button3.config(state=tk.DISABLED)

            # If the button was pressed but a file is not loaded
            if self.file_pressed is True:
                # Display an error message
                text_label.config(text="ERROR LOADING FILE\nPLEASE SELECT A FULL MAP CSV")

        else:
            button0_color = "#424242"

            # Display what file we loaded
            text_label.config(text="CURRENT FILE LOADED:\n" + self.file_selected)

        # Display the folder select button
        button4 = tk.Button(self.main_frame, text="Visualize Results", command=self.select_results, bg="#424242", fg="white", font=("Arial", 20), width=30)
        button4.grid(row=2, column=0, pady=0)
        button0 = tk.Button(self.main_frame, text="Select a Full Map File", command=select_file, bg=button0_color, fg="white", font=("Arial", 20), width=30)
        button0.grid(row=4, column=0, pady=0)

    def show_plots(self, button_num):
        """
        Initializes plot screen, handles the scan type selection, and begins the point scan.

        button_num: either 1 (auto), 2 (semi-auto), or 3 (manual) from button selection
        """
        def request_input(output_string, valid_func):
            """
            Helper function that will request input from the user until a valid input is given.

            output_string: text to display above the entry box
            valid_func: a function that determines if the input is valid or not
            """
            # Clear the box
            self.entry_box.delete(0, tk.END)
        
            # Loop until a valid input is given
            user_input = None
            while user_input is None:        
                self.entry_label.config(text="\n" + output_string)
                self.root.wait_variable(self.entry_input_ready)
                user_input = self.entry_box.get()
                self.entry_box.delete(0, tk.END)
    
                if valid_func(user_input):
                    self.invalid_label.config(text="")
                    return user_input
                else:
                    user_input = None
                    self.invalid_label.config(text="INVALID")

        def baseline_click():
            """
            Function called when the baseline button is pressed. Updates sampling and smoothing then loops or exits.
            """
            # Disable buttons while updating
            self._toggle_buttons(tk.DISABLED)

            # Prompt for sampling and smoothing
            self.sampling = int(request_input("Sampling:", lambda x: x.isdigit()))
            self._update_data()
            self.smoothing = int(request_input("Smoothing:", lambda x: x.isdigit()))
            self._update_data()
        
            # Calculate and remove a baseline
            self.baseline, self.spectrum = Auto.baselining(self.spectrum_stowed_arm_removed, self.sampling, self.smoothing)
        
            # Fit a gaussian curve to the data at our desired location
            self.peak_params, self.FWHM, self.r_squared, self.cov = Auto.perform_peakfit(self.ramanshift, self.spectrum, self.ind1, self.ind2, self.CENTER)
        
            # Calculate SNR of the fit
            self.SNR_stowed = Auto.calculate_SNR_stowed_arm(self.ramanshift, self.cur_noise, self.peak_params[0], self.CENTER)
            self.SNR_silent = Auto.calculate_SNR_silent_region(self.ramanshift, self.spectrum, self.peak_params[0])

            # Update the plots
            self.baseline_display.update_data(self.ramanshift, self.spectrum, self.baseline, self.ind1, self.ind2)
            self.noise_display.update_data(self.ramanshift, self.spectrum, self.cur_noise, self.CENTER)
            self.peakfit.update_data(self.ramanshift, self.spectrum, self.peak_params, self.ind1, self.ind2)

            # Update data
            self._update_data()

            # Prompt for approval
            approved = request_input("Approve(Y/N):", lambda x: x.upper() in ["Y", "N"]).upper()
            
            # Reset if approved otherwise loop
            if approved == "Y":
                # Re-enable the buttons and clear entry label
                self.entry_label.config(text="\n")
                self._toggle_buttons(tk.NORMAL)

            else:
                self.baseline_click()

        def cosmic_click():
            """
            Function called when cosmic ray button is pressed. Replaces current selected region, changes range of
            viewframe, or modifies selected region.
            """
            # Numpy helper function to find an actual data point when user selects one
            def find_nearest_index(array, value):
                idx = np.searchsorted(array, value, side="left")
                if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
                    return idx - 1
                else:
                    return idx
            
            # Disable buttons while updating
            self._toggle_buttons(tk.DISABLED)

            # Collect a selection and handle it
            selection = request_input("(A)pprove\n(R)ange\n(M)odify\n(E)xit:", lambda x: x.upper() in ["A", "R", "M", "E"]).upper()

            loop = True
            if selection == "A":
                # Calculate linear replacement for peak (change in y/change in x)
                replacement_slope = (self.spectrum_stowed_arm_removed[self.cosmic_lower_index] - self.spectrum_stowed_arm_removed[self.cosmic_upper_index]) / (self.cosmic_lower_index - self.cosmic_upper_index)
    
                for i in range(self.cosmic_lower_index + 1, self.cosmic_upper_index):
                    self.spectrum_stowed_arm_removed[i] = self.spectrum_stowed_arm_removed[i - 1] + replacement_slope
        
                # Calculate and remove a baseline
                self.baseline, self.spectrum = Auto.baselining(self.spectrum_stowed_arm_removed, self.sampling, self.smoothing)
        
                # Fit a gaussian curve to the data at our desired location
                self.peak_params, self.FWHM, self.r_squared, self.cov = Auto.perform_peakfit(self.ramanshift, self.spectrum, self.ind1, self.ind2, self.CENTER)
        
                # Calculate SNR of the fit
                self.SNR_stowed = Auto.calculate_SNR_stowed_arm(self.ramanshift, self.cur_noise, self.peak_params[0], self.CENTER)
                self.SNR_silent = Auto.calculate_SNR_silent_region(self.ramanshift, self.spectrum, self.peak_params[0])
            
                # Update plots
                self.baseline_display.update_data(self.ramanshift, self.spectrum, self.baseline, self.ind1, self.ind2)
                self.noise_display.update_data(self.ramanshift, self.spectrum, self.cur_noise, self.CENTER)
                self.peakfit.update_data(self.ramanshift, self.spectrum, self.peak_params, self.ind1, self.ind2)

                # Update data
                self._update_data()

                loop = False

            elif selection == "R":
                # Get new ranges
                self.cosmic_display_lower = float(request_input("Lower Range:", lambda x: x.replace('.', '', 1).isdigit()))
                self.cosmic_display_upper = float(request_input("Upper Range:", lambda x: x.replace('.', '', 1).isdigit()))

            elif selection == "M":
                # Get new cosmic ray range
                cosmic_lower = float(request_input("Cosmic Lower:", lambda x: x.replace('.', '', 1).isdigit()))
                cosmic_upper = float(request_input("Cosmic Upper:", lambda x: x.replace('.', '', 1).isdigit()))

                # Convert to an array index
                self.cosmic_lower_index = find_nearest_index(self.ramanshift, cosmic_lower)
                self.cosmic_upper_index = find_nearest_index(self.ramanshift, cosmic_upper)

            else:
                loop = False

            # Update the cosmic ray plot
            self.cosmic.update_data(self.ramanshift, self.spectrum_stowed_arm_removed, self.cosmic_display_lower, self.cosmic_display_upper, self.cosmic_lower_index, self.cosmic_upper_index)

            if loop:
                self.cosmic_click()

            else:
                # Re-enable the buttons and clear entry tag
                self.entry_label.config(text="\n")
                self._toggle_buttons(tk.NORMAL)

        def peakfit_click(original_settings=None):
            """
            Function called when the peakfit button is pressed. Approves current peakfit, modifies one parameter,
            or exits without saving changes.
            """
            # Local constants
            WIDTH_APPROXIMATION = 2.35
            R_SQUARED_CALC_RANGE = 2

            # Store original settings as needed
            if original_settings is None:
                stored = [self.peak_params.copy()]
                stored.append(self.cov.copy())
                self.cov = np.zeros((3, 3))
            else:
                stored = original_settings

            # Disable buttons while updating
            self._toggle_buttons(tk.DISABLED)

            # Collect a selection and handle it
            selection = request_input("(A)pprove\n(M)odify\n(E)xit:", lambda x: x.upper() in ["A", "M", "E"]).upper()

            loop = True
            if selection == "A":
                loop = False
        
            elif selection == "M":
                # Collect a modification selection and value
                modify = request_input("(H)eight\n(M)ean\n(S)igma:", lambda x: x.upper() in ["H", "M", "S"]).upper()
                value = float(request_input("Value:", lambda x: x.replace('.', '', 1).isdigit()))

                if modify == "H":
                    self.peak_params[0] = value
                elif modify == "M":
                    self.peak_params[1] = value
                else:
                    self.peak_params[2] = value

            else:
                # Reset peak parameters back to original
                self.peak_params[0] = stored[0][0]
                self.peak_params[1] = stored[0][1]
                self.peak_params[2] = stored[0][2]
                self.cov = stored[1]

                loop = False

            # Narrow down x and y values to ones surrounding the peak
            ind_fit = (self.ramanshift > self.peak_params[1] - self.peak_params[2]*R_SQUARED_CALC_RANGE) & (self.ramanshift < self.peak_params[1] + self.peak_params[2]*R_SQUARED_CALC_RANGE)
            peak_ramanshift = self.ramanshift[ind_fit]
            peak_spectrum = self.spectrum[ind_fit]

            # Calculate R-Squared
            residuals = peak_spectrum - Helper.gauss(peak_ramanshift, self.peak_params[0], self.peak_params[1], self.peak_params[2])
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((peak_spectrum - np.mean(peak_spectrum))**2)
            self.r_squared = 1 - (ss_res / ss_tot) if (ss_res / ss_tot) != 0 else 0
            
            # Calculate FWHM
            self.FWHM = WIDTH_APPROXIMATION * self.peak_params[2]

            # Calculate SNR of the fit
            self.SNR_stowed = Auto.calculate_SNR_stowed_arm(self.ramanshift, self.cur_noise, self.peak_params[0], self.CENTER)
            self.SNR_silent = Auto.calculate_SNR_silent_region(self.ramanshift, self.spectrum, self.peak_params[0])

            # Update the graph
            self.peakfit.update_data(self.ramanshift, self.spectrum, self.peak_params, self.ind1, self.ind2)

            # Update data
            self._update_data()

            if loop:
                self.peakfit_click(stored)

            else:
                # Re-enable the buttons and clear entry tag
                self.entry_label.config(text="\n")
                self._toggle_buttons(tk.NORMAL)

        def double_peakfit_click(original_settings=None, other_peak_params=None):
            """
            Function called when double peakfit button is pressed. Performs preliminary double peakfit, approves
            the double peakfit, modifies one parameter of either peak, or exits without approving.
            """
            # Local constants
            WIDTH_APPROXIMATION = 2.35
            R_SQUARED_CALC_RANGE = 2

            # Store original settings as needed
            if original_settings is None:
                stored = [self.peak_params.copy()]
                stored.append(self.cov.copy())
                self.cov = np.zeros((3, 3))
            else:
                stored = original_settings
            
            # Disable buttons while updating
            self._toggle_buttons(tk.DISABLED)

            # Collect a second center as needed and perform preliminary fit
            other_params = [0, 0, 0]
            if other_peak_params is None:
                other_center = float(request_input("Other Peak:", lambda x: x.replace('.', '', 1).isdigit()))

                # Perform a double peak fit, update the graphs and data
                self.peak_params, other_params, self.FWHM, self.r_squared = Auto.perform_double_peakfit(self.ramanshift, self.spectrum, self.ind1, self.ind2, self.CENTER, other_center)
                self.SNR_stowed = Auto.calculate_SNR_stowed_arm(self.ramanshift, self.cur_noise, self.peak_params[0], self.CENTER)
                self.SNR_silent = Auto.calculate_SNR_silent_region(self.ramanshift, self.spectrum, self.peak_params[0])
                self.peakfit.update_data(self.ramanshift, self.spectrum, self.peak_params, self.ind1, self.ind2, other_params)
                self._update_data()

            else:
                other_params = other_peak_params

            focus_left = self.peak_params[1] < other_params[1]
            if focus_left:
                left_params = self.peak_params
                right_params = other_params
            else:
                left_params = other_params
                right_params = self.peak_params

            # Collect a selection and handle it
            selection = request_input("(A)pprove\n(M)odify\n(E)xit:", lambda x: x.upper() in ["A", "M", "E"]).upper()
        
            loop = True
            if selection == "A":
                loop = False

            elif selection == "M":
                # Determine which peak to modify
                peak_selection = request_input("(L)eft\n(R)ight:", lambda x: x.upper() in ["L", "R"]).upper()

                # Collect a modification selection and value
                modify = request_input("(H)eight\n(M)ean\n(S)igma:", lambda x: x.upper() in ["H", "M", "S"]).upper()
                value = float(request_input("Value:", lambda x: x.replace('.', '', 1).isdigit()))

                # Update the appropriate parameters
                if (peak_selection == "L" and focus_left) or (peak_selection == "R" and not focus_left):
                    if modify == "H":
                        self.peak_params[0] = value
                    elif modify == "M":
                        self.peak_params[1] = value
                    else:
                        self.peak_params[2] = value
                else:
                    if modify == "H":
                        other_params[0] = value
                    elif modify == "M":
                        other_params[1] = value
                    else:
                        other_params[2] = value

            else:
                # Reset peak parameters back to original
                self.peak_params[0] = stored[0][0]
                self.peak_params[1] = stored[0][1]
                self.peak_params[2] = stored[0][2]
                self.cov = stored[1]
            
                # Narrow down x and y values to ones surrounding the peak
                ind_fit = (self.ramanshift > self.peak_params[1] - self.peak_params[2]*R_SQUARED_CALC_RANGE) & (self.ramanshift < self.peak_params[1] + self.peak_params[2]*R_SQUARED_CALC_RANGE)
                peak_ramanshift = self.ramanshift[ind_fit]
                peak_spectrum = self.spectrum[ind_fit]

                # Calculate R-Squared
                residuals = peak_spectrum - Helper.gauss(peak_ramanshift, self.peak_params[0], self.peak_params[1], self.peak_params[2])
                ss_res = np.sum(residuals**2)
                ss_tot = np.sum((peak_spectrum - np.mean(peak_spectrum))**2)
                self.r_squared = 1 - (ss_res / ss_tot) if (ss_res / ss_tot) != 0 else 0
            
                # Calculate FWHM
                self.FWHM = WIDTH_APPROXIMATION * self.peak_params[2]

                # Calculate SNR of the fit
                self.SNR_stowed = Auto.calculate_SNR_stowed_arm(self.ramanshift, self.cur_noise, self.peak_params[0], self.CENTER)
                self.SNR_silent = Auto.calculate_SNR_silent_region(self.ramanshift, self.spectrum, self.peak_params[0])

                # Update the graph
                self.peakfit.update_data(self.ramanshift, self.spectrum, self.peak_params, self.ind1, self.ind2)

                # Update data
                self._update_data()

                # Re-enable the buttons and clear entry tag
                self.entry_label.config(text="\n")
                self._toggle_buttons(tk.NORMAL)

                return

            # Narrow down x and y values to ones surrounding the peak
            ind_fit = (self.ramanshift > left_params[1] - left_params[2]*R_SQUARED_CALC_RANGE) & (self.ramanshift < right_params[1] + right_params[2]*R_SQUARED_CALC_RANGE)
            peak_ramanshift = self.ramanshift[ind_fit]
            peak_spectrum = self.spectrum[ind_fit]

            # Calculate R-Squared
            residuals = peak_spectrum - Helper.double_gauss(peak_ramanshift, self.peak_params[0], self.peak_params[1], self.peak_params[2], other_params[0], other_params[1], other_params[2])
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((peak_spectrum - np.mean(peak_spectrum))**2)
            self.r_squared = 1 - (ss_res / ss_tot) if (ss_res / ss_tot) != 0 else 0
            
            # Calculate FWHM
            self.FWHM = WIDTH_APPROXIMATION * self.peak_params[2]

            # Calculate SNR of the fit
            self.SNR_stowed = Auto.calculate_SNR_stowed_arm(self.ramanshift, self.cur_noise, self.peak_params[0], self.CENTER)
            self.SNR_silent = Auto.calculate_SNR_silent_region(self.ramanshift, self.spectrum, self.peak_params[0])

            # Update the graph
            self.peakfit.update_data(self.ramanshift, self.spectrum, self.peak_params, self.ind1, self.ind2, other_params)

            # Update data
            self._update_data()
        
            if loop:
                self.double_peakfit_click(stored, other_params)
            else:
                self.entry_label.config(text="\n")
                self._toggle_buttons(tk.NORMAL)

        def approve_click():
            """
            Function called when approve button is pressed. Marks the point for approval and ends modify loop.
            """
            # Approve the point and unlock the loop after disabling buttons again
            self.approved = True
            self._toggle_buttons(tk.DISABLED)
            self.button_event.set()

        def deny_click():
            """
            Function called when deny button is pressed. Marks the point for denial and ends modify loop.
            """
            # Deny the point and unlock the loop after disabling buttons again
            self.approved = False
            self._toggle_buttons(tk.DISABLED)
            self.button_event.set()

        # Clear anything in the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create a frame to hold the progress bar and label
        progress_frame = tk.Frame(self.main_frame, bg="#2B2B2B")
        progress_frame.grid(row=0, column=0, columnspan=3, pady=0, sticky="n")

        # Create a ttk.Progressbar widget and apply custom style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("bar.Horizontal.TProgressbar", troughcolor="#363636", 
                        bordercolor="#2B2B2B", background="#B00020", lightcolor="#B00020", 
                        darkcolor="#B00020")
        self.progress_bar = ttk.Progressbar(progress_frame, style="bar.Horizontal.TProgressbar", orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT)

        # Create a label to display progress percentage
        self.progress_label = tk.Label(progress_frame, text="  Point 0/99", font=("Arial", 12), bg="#2B2B2B", fg="white")
        self.progress_label.pack(side=tk.LEFT)
        
        # Create a frame to hold the selection buttons
        selection_frame = tk.Frame(self.main_frame, bg="#2B2B2B")
        selection_frame.grid(row=0, column=2, rowspan=2, padx=0, pady=10, sticky="e")

        # Info display above the selection buttons
        self.data_label = tk.Label(selection_frame, text="CURRENT DATA\n\nHeight:\n\nMean:\n\nSigma:\n\nFWHM:\n\nR\u00B2 \n\nStow SNR:\n\nSilent SNR:\n\nSampling:\n\nSmoothing:\n\n", bg="#2B2B2B", fg="white", font=("Arial", 9), width=20, justify='left', anchor='w', wraplength=100)
        self.data_label.pack(side=tk.TOP)

        # Selection button handling
        self.baseline_button = tk.Button(selection_frame, text="Baseline", command=baseline_click, bg="#424242", fg="white", font=("Arial", 10), width=10)
        self.baseline_button.pack(side=tk.TOP, anchor='w')
        self.cosmic_button = tk.Button(selection_frame, text="Cosmic Rays", command=cosmic_click, bg="#424242", fg="white", font=("Arial", 10), width=10)
        self.cosmic_button.pack(side=tk.TOP, anchor='w')
        self.peakfit_button = tk.Button(selection_frame, text="Peakfit", command=peakfit_click, bg="#424242", fg="white", font=("Arial", 10), width=10)
        self.peakfit_button.pack(side=tk.TOP, anchor='w')
        self.double_peakfit_button = tk.Button(selection_frame, text="Double Peakfit", command=double_peakfit_click, bg="#424242", fg="white", font=("Arial", 10), width=10)
        self.double_peakfit_button.pack(side=tk.TOP, anchor='w')
        self.approve_button = tk.Button(selection_frame, text="Approve", command=approve_click, bg="#424242", fg="white", font=("Arial", 10), width=10)
        self.approve_button.pack(side=tk.TOP, anchor='w')
        self.deny_button = tk.Button(selection_frame, text="Deny", command=deny_click, bg="#424242", fg="white", font=("Arial", 10), width=10)
        self.deny_button.pack(side=tk.TOP, anchor='w')

        # Create labels and entry box below the selection buttons
        self.entry_label = tk.Label(selection_frame, text="\n", bg="#2B2B2B", fg="white", font=("Arial", 10), width=10, justify='left', anchor='w', wraplength=100)
        self.entry_label.pack(side=tk.TOP, anchor='w')
        self.entry_box = tk.Entry(selection_frame, bg="#424242", fg="white", font=("Arial", 10), width=12)
        self.entry_box.pack(side=tk.TOP, anchor='w')
        self.invalid_label = tk.Label(selection_frame, text="", bg="#2B2B2B", fg="white", font=("Arial", 10), width=10)
        self.invalid_label.pack(side=tk.TOP, anchor='w')

        # Create a tkinter variable to signal the entry input is ready
        self.entry_input_ready = tk.BooleanVar()
        self.entry_box.bind('<Return>', lambda event: self.entry_input_ready.set(True))

        # Create the PlotObjects inside the main frame
        self.baseline_display = Plots.BaselinePlot(self.main_frame)
        self.noise_display = Plots.NoisePlot(self.main_frame)
        self.cosmic = Plots.CosmicRayPlot(self.main_frame)
        self.peakfit = Plots.PeakfitPlot(self.main_frame)

        if button_num == 1:
            # When auto button was selected, dont display any future plots for approval
            self.display_func = lambda SNR, r_squared, FWHM: False

        elif button_num == 2:
            # When semi-auto button was selected, display plots for approval if specific parameters are met
            self.display_func = lambda SNR, r_squared, FWHM: ((SNR > self.SNR_THRESHOLD 
                                                               and r_squared > self.R_SQUARED_THRESHOLD / 2.0 
                                                               and FWHM > self.FWHM_MIN and FWHM < self.FWHM_MAX) 
                                                              or (SNR > self.SNR_THRESHOLD * 1.5 
                                                                  and FWHM > self.FWHM_MIN and FWHM < self.FWHM_MAX))

        else:
            # When manual button was selected, always display future plots for approval
            self.display_func = lambda SNR, r_squared, FWHM: True

        # Start the point scan on a different thread so it can be interrupted by button presses
        self.loop_thread = threading.Thread(target=self.scan_points)
        self.loop_thread.start()

    def scan_points(self):    
        """
        Scans through each point in the user selected dataframe and handles adjustments as necessary.
        """
        def append_df(point_index):
            """
            Helper function to add current point settings to a desired dataframe.

            point_index: index of the current point being looked at
            """
            # Find standard deviation of the covariance
            std = np.sqrt(np.diag(self.cov))

            # Create the new row to be entered        
            new_row = {
                "Point" : point_index,
                "Height" : self.peak_params[0],
                "Height STD" : std[0],
                "Mean" : self.peak_params[1],
                "Mean STD" : std[1],
                "Sigma" : self.peak_params[2],
                "Sigma STD" : std[2],
                "FWHM" : self.FWHM,
                "R^2" : self.r_squared,
                "Stowed SNR" : self.SNR_stowed,
                "Silent SNR" : self.SNR_silent
            }
            new_row = pd.DataFrame.from_dict(new_row, orient='index').T

            # Add it to the appropriate dataframe
            if self.approved:
                self.approved_result_df = pd.concat([self.approved_result_df, new_row], ignore_index=True)
            else:
                self.denied_result_df = pd.concat([self.denied_result_df, new_row], ignore_index=True)

        def export_dfs():
            """
            Exports both dataframes in their current state to the results folder and resets them to empty.
            """

            # Split our known working directory to access naming information
            split_path = self.file_selected.split('/')

            # Store the scan name and scan type
            scan_name = split_path[-6]
            scan_type = split_path[-5]

            # Build a file name
            file_name = scan_name + '-' + scan_type

            # Initialize folder count, will be incremented until no longer matches existing folders in user's files
            folder_count = 1

            # Create a result directory if needed
            result_directory = os.path.join(os.getcwd(), "User")
            result_directory = os.path.join(result_directory, "Results")
            result_directory = os.path.join(result_directory, self.MINERAL_NAME)
            if not os.path.exists(result_directory):
                os.makedirs(result_directory)

            # Increment the folder counter until we create a unique folder name
            folder_path = os.path.join(result_directory, file_name + '_' + str(folder_count))
            while os.path.exists(folder_path):
                folder_count += 1
                folder_path = os.path.join(result_directory, file_name + '_' + str(folder_count))

            # Create the folder path
            os.makedirs(folder_path)

            # Initialize our file paths and store results
            approved_file = os.path.join(folder_path, file_name + '_Approved.csv')
            denied_file = os.path.join(folder_path, file_name + '_Denied.csv')
            self.approved_result_df.to_csv(approved_file, index=False)
            self.denied_result_df.to_csv(denied_file, index=False)

            self.approved_result_df = self.fresh_df
            self.denied_result_df = self.fresh_df

        # Unpack the sample dataframe
        self.ramanshift, self.spectrums = Helper.process_ZNZ_dataframe(self.file_selected)
        
        # Store a median noise sample for subtraction
        self.noise_sample = np.array(self.noise_df.median(axis=1))

        # Disable the buttons until needed
        self._toggle_buttons(tk.DISABLED)

        for i, spectrum_raw in enumerate(self.spectrums):
            spectrum_raw = pd.to_numeric(spectrum_raw)
            # Initialize the cosmic plot initial settings
            self.cosmic_display_lower = self.ind1
            self.cosmic_display_upper = self.ind2
            self.cosmic_lower_index = 0
            self.cosmic_upper_index = 0

            # Set the value of our current mhw and shw
            self.sampling = self.MHW
            self.smoothing = self.SHW

            # Store current noise
            self.cur_noise = self.noise_df[f"Point {i}"]
        
            # Remove stowed arm noise median
            self.spectrum_stowed_arm_removed = Auto.stowed_arm_subtraction(spectrum_raw, self.noise_sample)
        
            # Calculate and remove a baseline
            self.baseline, self.spectrum = Auto.baselining(self.spectrum_stowed_arm_removed, self.sampling, self.smoothing)
        
            # Fit a gaussian curve to the data at our desired location
            self.peak_params, self.FWHM, self.r_squared, self.cov = Auto.perform_peakfit(self.ramanshift, self.spectrum, self.ind1, self.ind2, self.CENTER)
        
            # Calculate SNR of the fit
            self.SNR_stowed = Auto.calculate_SNR_stowed_arm(self.ramanshift, self.cur_noise, self.peak_params[0], self.CENTER)
            self.SNR_silent = Auto.calculate_SNR_silent_region(self.ramanshift, self.spectrum, self.peak_params[0])
        
            # Determine if the point should be approved
            self.approved = (min(self.SNR_stowed, self.SNR_silent) > self.SNR_THRESHOLD
                            and self.r_squared > self.R_SQUARED_THRESHOLD 
                            and self.FWHM > self.FWHM_MIN and self.FWHM < self.FWHM_MAX
                            and self.peak_params[1] > self.CENTER - self.CENTER_RANGE
                            and self.peak_params[1] < self.CENTER + self.CENTER_RANGE)

            if self.display_func(max(self.SNR_stowed, self.SNR_silent), self.r_squared, self.FWHM):
                # Enable update buttons
                self._toggle_buttons(tk.NORMAL)

                # Update the plots
                self.baseline_display.update_data(self.ramanshift, self.spectrum, self.baseline, self.ind1, self.ind2)
                self.noise_display.update_data(self.ramanshift, self.spectrum, self.cur_noise, self.CENTER)
                self.cosmic.update_data(self.ramanshift, self.spectrum_stowed_arm_removed, self.cosmic_display_lower, self.cosmic_display_upper, self.cosmic_lower_index, self.cosmic_upper_index)
                self.peakfit.update_data(self.ramanshift, self.spectrum, self.peak_params, self.ind1, self.ind2)

                # Update data
                self._update_data()

                # Wait for a button event to indicate a change occured 
                self.button_event.wait()
                self.button_event.clear()

            # Update the dataframes
            append_df(i)

            # Update the progress bar value and label text
            self.progress_bar["value"] = i + 1
            self.progress_label.config(text=f"  Point {i + 1}/99")

        # Export dataframes
        export_dfs()

        # Recenter the main frame
        self.main_frame.grid(row=0, column=0, sticky='news')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Return to the main page
        self.show_buttons()

    def select_results(self):
        """
        Function called when visualization is selected from the main screen.
        """
        def canvasConfig(event):
            """
            Configures our canvas to be scrollable
            """
            canvas.configure(scrollregion=canvas.bbox("all"))

        def group_popup():
            """
            Called when a new group is to be added
            """
            group_name = tk.simpledialog.askstring("Group Name", "Enter group name:")
            self.groups[group_name] = []

            # Update the display
            self.select_results()

        def sample_popup(group_name):
            """
            Called when a new sample is to be added
            """
            # Prompt user for a full map file
            file_selected = tk.filedialog.askopenfilename(title='Select the result file', parent=root)

            # Only update stored file if user selected a valid file
            if file_selected != "" and file_selected.lower().endswith(".csv"):
                # Add the file to our list
                self.groups[group_name].append(file_selected)

            # Update the display
            self.select_results()
             
        def remove_group(group_name):
            """
            Called when a group is to be removed
            """
            self.groups.pop(group_name)

            # Update the display
            self.select_results()

        def remove_sample(group_name, index):
            """
            Called when a sample is to be removed
            """
            self.groups[group_name].pop(index)

            # Update the display
            self.select_results()

        # Clear anything in the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.main_frame, bg="#2B2B2B", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        inner_frame = tk.Frame(canvas, bg="#2B2B2B")
        scrollbar = tk.Scrollbar(inner_frame, orient="vertical", command=canvas.yview, troughcolor="blue", bg="red")
        canvas.configure(yscrollcommand=scrollbar.set)
        inner_frame.update()
        canvas.create_window((canvas.winfo_width()/2, 0), window=inner_frame, anchor='center')
        scrollbar.pack(side="right", fill="y")
        inner_frame.bind("<Configure>", canvasConfig)

        first = True

        for group_name, group in self.groups.items():
            top_pad = (40,0) if first else (5,0)
            first = False

            # Group name and removal button
            label_frame = tk.Frame(inner_frame, bg="#2B2B2B", width=300)
            label_frame.pack(side="top", pady=top_pad)
            group_label = tk.Label(label_frame, text=group_name, bg="#2B2B2B", fg="white", font=("Arial", 10))
            group_label.pack(side="left")
            label_frame.update()
            remove_group_button = tk.Button(label_frame, text="-", command=lambda name=group_name: remove_group(name), bg="#B00020", fg="white", font=("Arial", 10), width=3)
            group_label.pack(side="left", padx=228-group_label.winfo_width()/2)
            remove_group_button.pack(side="left", padx=228-group_label.winfo_width()/2)

            for i, filename in enumerate(group):
                identifier = filename.rsplit('/', 1)[1]

                # Identifier name and removal button
                identifier_frame = tk.Frame(inner_frame, bg="#2B2B2B", width=300)
                identifier_frame.pack(side="top", pady=(5,0))
                identifier_label = tk.Label(identifier_frame, text=identifier, bg="#2B2B2B", fg="white", font=("Arial", 10))
                identifier_label.pack(side="left")
                identifier_frame.update()
                remove_identifier_button = tk.Button(identifier_frame, text="-", command=lambda name=group_name, index=i: remove_sample(name, index), bg="#B00020", fg="white", font=("Arial", 10), width=3)
                identifier_label.pack(side="left", padx=228-identifier_label.winfo_width()/2)
                remove_identifier_button.pack(side="left", padx=208-identifier_label.winfo_width()/2)

            # Individual sample add button
            sample_frame = tk.Frame(inner_frame, bg="#2B2B2B", width=300)
            sample_frame.pack(side="top", pady=5)
            add_sample_button = tk.Button(sample_frame, text="+", command=lambda name=group_name: sample_popup(name), bg="#2F4562", fg="white", font=("Arial", 10), width=3)
            add_sample_button.pack(side="left", padx=225)
            blank_label = tk.Label(sample_frame, text="", bg="#2B2B2B", fg="white", font=("Arial", 10))
            blank_label.pack(side="left", padx=205)

        # Add additional padding if first run through
        top_pad = (40,0) if first else (0,0)
        
        # Place the add group button
        group_button = tk.Button(inner_frame, text="Add Group", command=group_popup, bg="#424242", fg="white", font=("Arial", 20), width=30)
        group_button.pack(side="top", pady=top_pad, padx=228)

        # Place the export button
        export_button = tk.Button(inner_frame, text="Export", command=self.export_visuals, bg="#424242", fg="white", font=("Arial", 20), width=30)
        export_button.pack(side="top", pady=(5,0), padx=228)

    def export_visuals(self):
        """
        Creates a new folder and exports all visuals to it
        """
        def calculate_positions(x_values, y_values):
            # Laser center value
            center = (809, 664)
    
            # Pixel scale in microns
            pix_um = 10.1
    
            pix_x = []
            pix_y = []
    
            # Conversion from x/y to image pixel values
            for x, y in zip(x_values, y_values):
                pix_x.append(int(np.round(center[0] - (x * 1000.0 / pix_um))))
                pix_y.append(int(np.round(center[1] - (y * 1000.0 / pix_um))))
        
            return pix_x, pix_y

        # Path to the visual folder
        visual_path = os.path.join(os.getcwd(), "User")
        visual_path = os.path.join(visual_path, "Visuals")

        # Create a unique folder for the visuals
        folder_count = 1
        folder_path = os.path.join(visual_path, "Visuals" + '_' + str(folder_count))
        while os.path.exists(folder_path):
            folder_count += 1
            folder_path = os.path.join(visual_path, "Visuals" + '_' + str(folder_count))    
        os.makedirs(folder_path)
        
        metric_list = []

        for group_name, group in self.groups.items():

            metric_dict = defaultdict(list)

            for scan_path in group:
                
                # Get the identifier (ex: sol_207)
                file_name = scan_path.rsplit('/', 1)[1].rsplit('_', 1)[0]           
                
                # Store scan name
                file_split = file_name.rsplit('-', 1)
                scan_name = file_split[0]
                scan_type = file_split[1]

                # Build a path into the desired scan
                loupe_data_path = os.path.join(os.getcwd(), "User")
                loupe_data_path = os.path.join(loupe_data_path, "Data")
                loupe_data_path = os.path.join(loupe_data_path, scan_name)
                loupe_data_path = os.path.join(loupe_data_path, scan_type)
                contents = os.listdir(loupe_data_path)
                directories = [item for item in contents if os.path.isdir(os.path.join(loupe_data_path, item))]
                loupe_data_path = os.path.join(loupe_data_path, directories[0])
                   
                # Unpack spatial data frame
                spatial_df = pd.read_csv(os.path.join(loupe_data_path, 'spatial.csv'))

                # Extract the image directory
                loupe_data_path = os.path.join(loupe_data_path, 'img')
                files = os.listdir(loupe_data_path)
                files = [f for f in files if not f.startswith('.')]
                png_files = [file for file in files if file.lower().endswith('.png')]
                sorted_png_files = sorted(png_files)
                image_file = sorted_png_files[0][:6] + '~' + sorted_png_files[0][-5:] # Why do I have to do this?
                image_dir = os.path.join(loupe_data_path, image_file) # Take the first image alphabetically (this will be colored if available)

                # Limit the spatial dataframe to just the x and y values and convert them to floats
                spatial_df = spatial_df.iloc[101:201]
                spatial_df = spatial_df.astype(float)

                # Store an array of x and y values for each point
                x_values = np.array(spatial_df["az"])
                y_values = np.array(spatial_df["el"])
                x, y = calculate_positions(x_values, y_values)
                loc_array = [x, y]

                approved = []
                scan_df = pd.read_csv(scan_path)         

                for i, metric_name in enumerate(scan_df.columns):

                    if i == 0:
                        approved = scan_df[metric_name].values

                        # Make and save a spatial map
                        spatial = Results.SpatialPlot()
                        spatial.update_data(image_dir, loc_array, file_name)
                        spatial.export(folder_path)

                    else:
                        # Append the metric values to our metric dictionary at the metric name key
                        metric_dict[metric_name].extend(scan_df[metric_name].values.tolist())

                        # Make heatmap diverging if it is a center map
                        linear = metric_name != "Mean"

                        # Make and save a heatmap
                        heatmap = Results.MetricHeatmap(1)
                        heatmap.update_data(file_name + ' ' + metric_name, metric_name, scan_df[metric_name].values, approved, image_dir, loc_array, linear)
                        heatmap.export(folder_path)

            # Add our metric dictionary to the list
            metric_list.append(metric_dict)

        if len(metric_list) > 0:
            for metric_name, unused in metric_list[0].items():
                values_list = []
            
                for all_metrics in metric_list:
                    # Build up our nested list (ex: All SNRs for Dourbes, All SNRs for Garde, etc.)
                    values_list.append(all_metrics[metric_name])

                # Make and save a boxplot
                boxplot = Results.MetricPlot(1)
                boxplot.update_boxplot(metric_name, values_list, list(self.groups.keys()))
                boxplot.export(folder_path)

                # Make and save a histogram
                histogram = Results.MetricPlot(1)
                histogram.update_histogram(metric_name, np.ravel(values_list), 5)
                histogram.export(folder_path)

        # Go back to the main menu and reset groups
        self.groups = {}
        self.show_buttons()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
