import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import math
import os
import threading

import Plots
import Auto
import Helper

class MainApp:
    def __init__(self, root):
        """
        Initializes the application window.

        root: a tkinter tk object
        """
        # Unpack user settings
        settings_path = os.path.join(os.getcwd(), "Settings.csv")
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

        # Hard coded noise dataframe locations
        folder_path = os.path.join("Noise", settings_df["NOISE_SAMPLE"][0] + ".csv")
        folder_path = os.path.join(os.getcwd(), folder_path)
        self.noise_df = pd.read_csv(folder_path)

        # Result dataframes setup
        result_dict = {
            "Point" : [],
            "Height" : [],
            "Mean" : [],
            "Sigma" : [],
            "FWHM" : [],
            "R^2" : [],
            "SNR" : []
        }

        self.approved_result_df = pd.DataFrame(result_dict)
        self.denied_result_df = pd.DataFrame(result_dict)

        # Instance variables and root setup
        self.folder_pressed = False
        self.file_selected = None
        self.center = settings_df["CENTER"][0]
        self.ind1 = self.center - 150
        self.ind2 = self.center + 150
        self.root = root
        self.root.title("SHERLOC Mineral Detection")
        self.root.state('zoomed')  # Maximize the window

        # Threading button interrupt setup
        self.button_event = threading.Event()

        # Set dark theme background color for the root window
        self.root.config(bg="#2B2B2B")

        # Create a main frame to hold the buttons and plots
        self.main_frame = tk.Frame(self.root, bg="#2B2B2B")
        self.main_frame.grid(row=0, column=0, sticky='news')

        # Center the main frame within the window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Show the buttons initially
        self.show_buttons()

    def request_input(self, output_string, valid_func):
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

    def toggle_buttons(self, state):
        """
        Helper function that will change the state of the selection buttons.

        state: a tk state you wish to set the buttons to, tk.NORMAL or tk.DISABLED
        """
        self.baseline_button.config(state=state)
        self.cosmic_button.config(state=state)
        self.peakfit_button.config(state=state)
        self.approve_button.config(state=state)
        self.deny_button.config(state=state)

    def update_data(self):
        """
        Helper function that updates the data label with current information.
        """
        self.data_label.config(text=f"CURRENT DATA\n\nHeight: {round(self.peak_params[0], 1)}\n\nMean: {round(self.peak_params[1], 1)}\n\nSigma: {round(self.peak_params[2], 1)}\n\nFWHM: {round(self.FWHM, 1)}\n\nR^2: {round(self.r_squared, 4)}\n\nSNR: {round(self.SNR, 2)}\n\nSampling: {self.sampling}\n\nSmoothing: {self.smoothing}\n\n")


    def append_df(self, point_index):
        """
        Helper function to add current point settings to a desired dataframe.

        point_index: index of the current point being looked at
        """
        # Create the new row to be entered        
        new_row = {
            "Point" : point_index,
            "Height" : self.peak_params[0],
            "Mean" : self.peak_params[1],
            "Sigma" : self.peak_params[2],
            "FWHM" : self.FWHM,
            "R^2" : self.r_squared,
            "SNR" : self.SNR
        }
        new_row = pd.DataFrame.from_dict(new_row, orient='index').T

        # Add it to the appropriate dataframe
        if self.approved:
            self.approved_result_df = pd.concat([self.approved_result_df, new_row], ignore_index=True)
        else:
            self.denied_result_df = pd.concat([self.denied_result_df, new_row], ignore_index=True)


    def show_buttons(self):
        """
        Displays the selection screen to the user. Allows them to load a sample file and select a scan type.
        """
        # Remove the plots from the main frame
        for widget in self.main_frame.winfo_children():
            widget.grid_forget()

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

        # Make changes if the folder select button was never pressed
        if self.file_selected is None:
            button0_color = "#B00020"
            
            # Disable the other buttons until you select a file
            button1.config(state=tk.DISABLED)
            button2.config(state=tk.DISABLED)
            button3.config(state=tk.DISABLED)

            # If the button was pressed but a file is not loaded
            if self.folder_pressed is True:
                # Display an error message
                text_label = tk.Label(self.main_frame, text="ERROR LOADING FILE\nFull Map_spectra_ZNZ_R1.csv\nDID NOT EXIST IN THAT FOLDER", bg="#2B2B2B", fg="white", font=("Arial", 10))
                text_label.grid(row=4, column=0, pady=0)

        else:
            button0_color = "#424242"

            # Display what file we loaded
            text_label = tk.Label(self.main_frame, text="CURRENT FILE LOADED:\n" + self.file_selected.replace('/', '\\'), bg="#2B2B2B", fg="white", font=("Arial", 10))
            text_label.grid(row=4, column=0, pady=0)

        # Display the folder select button
        button0 = tk.Button(self.main_frame, text="Select a Full Map Folder", command=self.select_folder, bg=button0_color, fg="white", font=("Arial", 20), width=30)
        button0.grid(row=3, column=0, pady=0)

    def select_folder(self):
        """
        Prompts user to select a full map folder and checks if it exists.
        """
        # Update the button flag
        self.folder_pressed = True

        # Prompt user to select our folder
        full_map_path = tk.filedialog.askdirectory(title='Select the Full Map folder', parent=root)
        
        # Build file path and convert into dataframe
        csv_name = 'Full Map_spectra_ZNZ_R1.csv'
        file_selected = os.path.join(full_map_path, csv_name)

        # Store the file path if it exists
        if os.path.exists(file_selected):
            self.file_selected = file_selected
        else:
            self.file_selected = None

        # Update the buttons
        self.show_buttons()

    def show_plots(self, button_num):
        """
        Initializes plot screen, handles the scan type selection, and begins the point scan.

        button_num: either 1 (auto), 2 (semi-auto), or 3 (manual) from button selection
        """
        # Remove the buttons from the main frame
        for widget in self.main_frame.winfo_children():
            widget.grid_forget()

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
        self.data_label = tk.Label(selection_frame, text="CURRENT DATA\n\nHeight:\n\nMean:\n\nSigma:\n\nFWHM:\n\nR^2\n\nSNR:\n\nSampling:\n\nSmoothing:\n\n", bg="#2B2B2B", fg="white", font=("Arial", 10), width=15, justify='left', anchor='w', wraplength=100)
        self.data_label.pack(side=tk.TOP)

        # Selection button handling
        self.baseline_button = tk.Button(selection_frame, text="Baseline", command=self.baseline_click, bg="#424242", fg="white", font=("Arial", 10), width=10)
        self.baseline_button.pack(side=tk.TOP, anchor='w')
        self.cosmic_button = tk.Button(selection_frame, text="Cosmic Rays", command=self.cosmic_click, bg="#424242", fg="white", font=("Arial", 10), width=10)
        self.cosmic_button.pack(side=tk.TOP, anchor='w')
        self.peakfit_button = tk.Button(selection_frame, text="Peakfit", command=self.peakfit_click, bg="#424242", fg="white", font=("Arial", 10), width=10)
        self.peakfit_button.pack(side=tk.TOP, anchor='w')
        self.approve_button = tk.Button(selection_frame, text="Approve", command=self.approve_click, bg="#424242", fg="white", font=("Arial", 10), width=10)
        self.approve_button.pack(side=tk.TOP, anchor='w')
        self.deny_button = tk.Button(selection_frame, text="Deny", command=self.deny_click, bg="#424242", fg="white", font=("Arial", 10), width=10)
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
        self.baseline_unzoomed = Plots.BaselinePlot(self.main_frame)
        self.baseline_zoomed = Plots.ZoomedBaselinePlot(self.main_frame)
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
        # Unpack the sample dataframe
        self.ramanshift, self.spectrums = Helper.process_ZNZ_dataframe(self.file_selected)
        
        # Store a median noise sample for subtraction
        self.noise_sample = np.array(self.noise_df.median(axis=1))

        # Disable the buttons until needed
        self.toggle_buttons(tk.DISABLED)

        for i, spectrum_raw in enumerate(self.spectrums):
            # Initialize the cosmic plot initial settings
            self.cosmic_display_lower = self.ind1
            self.cosmic_display_upper = self.ind2
            self.cosmic_lower_index = 0
            self.cosmic_upper_index = 0

            # Set the value of our current mhw and shw
            self.sampling = self.MHW
            self.smoothing = self.SHW
        
            # Remove stowed arm noise median
            self.spectrum_stowed_arm_removed = Auto.stowed_arm_subtraction(spectrum_raw, self.noise_sample)
        
            # Calculate and remove a baseline
            self.baseline, self.spectrum = Auto.baselining(self.spectrum_stowed_arm_removed, self.sampling, self.smoothing)
        
            # Fit a gaussian curve to the data at our desired location
            self.peak_params, self.FWHM, self.r_squared = Auto.perform_peakfit(self.ramanshift, self.spectrum, self.ind1, self.ind2, self.center)
        
            # Calculate SNR of the fit
            self.SNR = Auto.calculate_SNR_stowed_arm(self.ramanshift, self.noise_sample, self.peak_params[0], self.ind1, self.ind2)
        
            # Determine if the point should be approved
            self.approved = (self.SNR > self.SNR_THRESHOLD and self.r_squared > self.R_SQUARED_THRESHOLD 
                            and self.FWHM > self.FWHM_MIN and self.FWHM < self.FWHM_MAX
                            and self.peak_params[1] > self.center - self.CENTER_RANGE
                            and self.peak_params[1] < self.center + self.CENTER_RANGE)

            if self.display_func(self.SNR, self.r_squared, self.FWHM):
                # Enable update buttons
                self.toggle_buttons(tk.NORMAL)

                # Update the plots
                self.baseline_unzoomed.update_data(self.ramanshift, self.spectrum, self.baseline)
                self.baseline_zoomed.update_data(self.ramanshift, self.spectrum, self.baseline, self.ind1, self.ind2)
                self.cosmic.update_data(self.ramanshift, self.spectrum_stowed_arm_removed, self.cosmic_display_lower, self.cosmic_display_upper, self.cosmic_lower_index, self.cosmic_upper_index)
                self.peakfit.update_data(self.ramanshift, self.spectrum, self.peak_params, self.ind1, self.ind2)

                # Update data
                self.update_data()

                # Wait for a button event to indicate a change occured 
                self.button_event.wait()
                self.button_event.clear()

            # Update the dataframes
            self.append_df(i)

            # Update the progress bar value and label text
            self.progress_bar["value"] = i + 1
            self.progress_label.config(text=f"  Point {i}/99")

        # Export dataframes
        self.export_dfs()

        # Recenter the main frame
        self.main_frame.grid(row=0, column=0, sticky='news')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Return to the main page
        self.show_buttons()

    def baseline_click(self):
        # Disable buttons while updating
        self.toggle_buttons(tk.DISABLED)

        # Prompt for sampling and smoothing
        self.sampling = int(self.request_input("Sampling:", lambda x: x.isdigit()))
        self.update_data()
        self.smoothing = int(self.request_input("Smoothing:", lambda x: x.isdigit()))
        self.update_data()
        
        # Calculate and remove a baseline
        self.baseline, self.spectrum = Auto.baselining(self.spectrum_stowed_arm_removed, self.sampling, self.smoothing)
        
        # Fit a gaussian curve to the data at our desired location
        self.peak_params, self.FWHM, self.r_squared = Auto.perform_peakfit(self.ramanshift, self.spectrum, self.ind1, self.ind2, self.center)
        
        # Calculate SNR of the fit
        self.SNR = Auto.calculate_SNR_stowed_arm(self.ramanshift, self.noise_sample, self.peak_params[0], self.ind1, self.ind2)

        # Update the plots
        self.baseline_unzoomed.update_data(self.ramanshift, self.spectrum, self.baseline)
        self.baseline_zoomed.update_data(self.ramanshift, self.spectrum, self.baseline, self.ind1, self.ind2)
        self.peakfit.update_data(self.ramanshift, self.spectrum, self.peak_params, self.ind1, self.ind2)

        # Update data
        self.update_data()

        # Prompt for approval
        approved = self.request_input("Approve(Y/N):", lambda x: x.upper() in ["Y", "N"]).upper()
            
        # Reset if approved otherwise loop
        if approved == "Y":
            # Re-enable the buttons and clear entry label
            self.entry_label.config(text="\n")
            self.toggle_buttons(tk.NORMAL)

        else:
            self.baseline_click()

    def cosmic_click(self):
        # Numpy helper function to find an actual data point when user selects one
        def find_nearest_index(array, value):
            idx = np.searchsorted(array, value, side="left")
            if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
                return idx - 1
            else:
                return idx
            
        # Disable buttons while updating
        self.toggle_buttons(tk.DISABLED)

        # Collect a selection and handle it
        selection = self.request_input("(A)pprove\n(R)ange\n(M)odify\n(E)xit:", lambda x: x.upper() in ["A", "R", "M", "E"]).upper()

        loop = True
        if selection == "A":
            # Calculate linear replacement for peak (change in y/change in x)
            replacement_slope = (self.spectrum_stowed_arm_removed[self.cosmic_lower_index] - self.spectrum_stowed_arm_removed[self.cosmic_upper_index]) / (self.cosmic_lower_index - self.cosmic_upper_index)
    
            for i in range(self.cosmic_lower_index + 1, self.cosmic_upper_index):
                self.spectrum_stowed_arm_removed[i] = self.spectrum_stowed_arm_removed[i - 1] + replacement_slope
        
            # Calculate and remove a baseline
            self.baseline, self.spectrum = Auto.baselining(self.spectrum_stowed_arm_removed, self.sampling, self.smoothing)
        
            # Fit a gaussian curve to the data at our desired location
            self.peak_params, self.FWHM, self.r_squared = Auto.perform_peakfit(self.ramanshift, self.spectrum, self.ind1, self.ind2, self.center)
        
            # Calculate SNR of the fit
            self.SNR = Auto.calculate_SNR_stowed_arm(self.ramanshift, self.noise_sample, self.peak_params[0], self.ind1, self.ind2)
            
            # Update plots
            self.baseline_unzoomed.update_data(self.ramanshift, self.spectrum, self.baseline)
            self.baseline_zoomed.update_data(self.ramanshift, self.spectrum, self.baseline, self.ind1, self.ind2)
            self.peakfit.update_data(self.ramanshift, self.spectrum, self.peak_params, self.ind1, self.ind2)

            # Update data
            self.update_data()

            loop = False

        elif selection == "R":
            # Get new ranges
            self.cosmic_display_lower = float(self.request_input("Lower Range:", lambda x: x.replace('.', '', 1).isdigit()))
            self.cosmic_display_upper = float(self.request_input("Upper Range:", lambda x: x.replace('.', '', 1).isdigit()))

        elif selection == "M":
            # Get new cosmic ray range
            cosmic_lower = float(self.request_input("Cosmic Lower:", lambda x: x.replace('.', '', 1).isdigit()))
            cosmic_upper = float(self.request_input("Cosmic Upper:", lambda x: x.replace('.', '', 1).isdigit()))

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
            self.toggle_buttons(tk.NORMAL)

    def peakfit_click(self, original_settings=None):
        # Local constants
        WIDTH_APPROXIMATION = 2.35
        R_SQUARED_CALC_RANGE = 2

        # Sstore original settings as needed
        if original_settings is None:
            stored = self.peak_params.copy()
        else:
            stored = original_settings

        # Disable buttons while updating
        self.toggle_buttons(tk.DISABLED)

        # Collect a selection and handle it
        selection = self.request_input("(A)pprove\n(M)odify\n(E)xit:", lambda x: x.upper() in ["A", "M", "E"]).upper()

        loop = True
        if selection == "A":
            loop = False
        
        elif selection == "M":
            # Collect a modification selection and value
            modify = self.request_input("(H)eight\n(M)ean\n(S)igma:", lambda x: x.upper() in ["H", "M", "S"]).upper()
            value = float(self.request_input("Value:", lambda x: x.replace('.', '', 1).isdigit()))

            if modify == "H":
                self.peak_params[0] = value
            elif modify == "M":
                self.peak_params[1] = value
            else:
                self.peak_params[2] = value

        else:
            # Reset peak parameters back to original
            self.peak_params[0] = stored[0]
            self.peak_params[1] = stored[1]
            self.peak_params[2] = stored[2]

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
        self.SNR = Auto.calculate_SNR_stowed_arm(self.ramanshift, self.noise_sample, self.peak_params[0], self.ind1, self.ind2)

        # Update the graph
        self.peakfit.update_data(self.ramanshift, self.spectrum, self.peak_params, self.ind1, self.ind2)

        # Update data
        self.update_data()

        if loop:
            self.peakfit_click(stored)

        else:
            # Re-enable the buttons and clear entry tag
            self.entry_label.config(text="\n")
            self.toggle_buttons(tk.NORMAL)

    def approve_click(self):
        # Approve the point and unlock the loop after disabling buttons again
        self.approved = True
        self.toggle_buttons(tk.DISABLED)
        self.button_event.set()

    def deny_click(self):
        # Deny the point and unlock the loop after disabling buttons again
        self.approved = False
        self.toggle_buttons(tk.DISABLED)
        self.button_event.set()

    def export_dfs(self):
        # Split our known working directory to access naming information
        split_path = self.file_selected.split('/')

        # Store the scan name and scan type
        scan_name = split_path[-5]
        scan_type = split_path[-4]

        # Build a file name
        file_name = scan_name + '-' + scan_type

        # Initialize folder count, will be incremented until no longer matches existing folders in user's files
        folder_count = 1

        # Create a result directory if needed
        result_directory = os.path.join(os.getcwd(), "Results")
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

        
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
