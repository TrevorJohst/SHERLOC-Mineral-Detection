<h2 align="center">SHERLOC Mineral Detector</h3>

  <p align="center">
    A tool to assist in the detection of minerals in SHERLOC Raman spectroscopy data. 
    <br />
    <br />
    Feel free to contact me at <a href="mailto:trejohst@mit.edu">trejohst@mit.edu</a> to report a bug, request a feature, or if you are having issues.
  </p>
  <br />


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#setup">Setup</a></li>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#settings">Settings</a></li>
      </ul>
    <li><a href="#usage">Usage</a></li>
      <ul>
        <li><a href="#loupe">Loupe</a></li>
        <li><a href="#processing">Processing</a></li>
        <li><a href="#visualizations">Visualizations</a></li>
      </ul>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- SETUP -->
## Setup

It is highly recommended to use Windows if possible, as the GUI has yet to be optimized for Mac. The application will still function, but navigation
may be difficult or confusing. 

### Installation

1. Open terminal and navigate to your desired directory
2. Clone the repository
   
   ```
   git clone https://github.com/TrevorJohst/SHERLOC-Mineral-Detection.git

   ```
3. Navigate into the repository and launch the primary python file
   
   ```
   python3 SHERLOC_Mineral_Detection.py

   ```

If you are using Windows and do not plan to modify any of the code, you can delete everything except the "SHERLOC Mineral Detection Executable" folder, and use
the .exe file to launch the application. 

### Settings

In the `User` directory you will find a file titled `Settings.csv`. From here you can modify all of the parameters for the app. Below is an image of what you will see when
you open the file.

![Screenshot 2024-03-12 194658](https://github.com/TrevorJohst/SHERLOC-Mineral-Detection/assets/122303295/960bce3c-cca7-42cc-abd1-2f690935472a)

If you plan to use manual mode, or are not certain what to set for the thresholds, you only need to modify CENTER and MINERAL_NAME.

#### SNR_THRESHOLD and R_SQUARED_THRESHOLD:
These metrics set the cutoffs for the signal to noise ratio and coefficient of determination respectively. In automatic mode these will be taken as hard cutoffs for deciding
if a mineral is "good enough." In semi-automatic mode the thresholds will be more relaxed and still present you with promising fits even if they do not meet both thresholds.

#### FWHM_MIN and FWHM_MAX:
These set the bounds on the full width half max of the peak, measured in cm<sup>-1</sup>. It is not recommended to go below 20 cm<sup>-1</sup> as this will allow fits to
only a couple of points. The maximum simply serves to remove any attempts to fit to the overall baseline of the data. 

#### CENTER, MINERAL_NAME, and CENTER_RANGE:
These settings are properties of the mineral you are searching for. The center location should be set at the Raman shift peak ( in cm<sup>-1</sup> ) for your desired
mineral, and the center range should reflect the maximum possible deviation from that position. Mineral name is only used to organize your results into folders.

#### SAMPLING and SMOOTHING:
These settings impact the automatic baseline removal. Changing these can have a drastic effect on results, so it is recommended to pick values that will work for most 
samples. In semi-automatic and manual mode, the baseline can be further adjusted if needed.

#### NOISE_SAMPLE:
This field determines which stowed arm scan ( located in `User > Noise` ) should be used to calculate the stowed SNR. It is best to use the sample closest to the date of the scan you are analyzing to account for changes in SHERLOC over time. I have provided the stowed arm scans from sols 413 and 678 with all major cosmic rays removed. If you wish to use one not provided, you could either try to use Loupe to generate it or email it to me and I will try to update the github.


<!-- USAGE -->
## Usage

Below I will walk through the general workflow for using the application.

### Loupe
This app is intended to be used in conjunction with <a href="https://github.com/nasa/Loupe">Loupe</a> by Kyle Uckert. After downloading and running his application from GitHub, you must start by opening a loupe file for your desired scan.

![open_loupe](https://github.com/TrevorJohst/SHERLOC-Mineral-Detection/assets/122303295/7a238d86-be6b-4c5e-a5d4-32831b5a78e8)

Next you need to select the scan of interest, normalize the laser scan, and export it as a Full Map file. If you want to try using Uckert's automatic ray removal there is a tab dedicated to it, but we have found it safer to remove them manually in the program when needed.

![export_loupe](https://github.com/TrevorJohst/SHERLOC-Mineral-Detection/assets/122303295/7856db1d-eecd-417c-a01b-4a6c639859f2)

After doing this, the full sample folder should be put in the Data folder. Ensure your directory looks similar to the one below so the program can navigate correctly. Each sol should be in the Data folder, and each scan within a sol should be within that sol's folder. 

```
User
├── Data
│   ├── sol_0489
│   │   ├── detail_1
│   │   │   ├── SrlcSpecSpec...
│   │   │   │   ├── ROI
│   │   │   │   │   ├── Full Map
│   │   │   │   │   │   ├── Full Map_spectra_ZNZ_R1.csv
│   │   │   │   │   │   └── ...
│   │   │   │   │   └── ...
│   │   │   │   └── ...
│   │   │   └── ...
│   │   ├── detail_2
│   │   └── ...
│   └── ...
├── Noise
├── Results
├── Visuals
└── Settings.csv
```

### Processing
Upon opening the application, you should select the full map button and navigate to the full map folder for your desired scan. 

![smd_select](https://github.com/TrevorJohst/SHERLOC-Mineral-Detection/assets/122303295/bb8623e2-6a1a-4130-b817-11dd41c31492)

After this, you must select either automatic, semi-automatic, or manual. There is a tradeoff between accuracy and time with the more manual options, the latter two options will present either some or all data points for manual ajustment and approval. Below is an image of what you will see if you select a manual option. Statistics are in the upper right and buttons to adjust the baseline, remove cosmic rays, adjust the peakfit, change to a double peakfit, and approve or deny the point. 

![Screenshot 2024-03-12 225506](https://github.com/TrevorJohst/SHERLOC-Mineral-Detection/assets/122303295/d8184b15-3b86-4804-a52a-a0ea949287a2)

For baseline adjustment you will be prompted for new sampling and smoothing values and the data will update live after both are provided. You can then approve or continue to update these values until you are happy with the baseline. 

For cosmic ray removal, you begin by providing an estimate for the range of the cosmic ray. This will update the upper right window to the range provided. Then you can modify the location of the cosmic ray until you are satisfied with the selection. If you then approve it, the ray will be removed from the sample. Doing this can help improve baselines, or make identifying minerals easier.

![Screenshot 2024-03-12 230857](https://github.com/TrevorJohst/SHERLOC-Mineral-Detection/assets/122303295/acbe0c20-b09e-41db-8bd5-87c94e9fa8b9)

If there is another mineral within the vicinity of the one you are looking for, the single gaussian curve may fit poorly to the data. You can then attempt to fit a double gaussian curve if you provide an estimate for the center of the other peak. This double curve can be adjusted manually just like the single curve fit if desired. 

![image](https://github.com/TrevorJohst/SHERLOC-Mineral-Detection/assets/122303295/0a0f65a9-b2df-4f2b-b023-18d0b65090e3)

When you finish a scan, either automatically or manually, a folder will be added to the results folder. This folder contains a .csv file storing all of the metrics for each approved and denied point. You can either analyze this data manually, or use the visualization to produce a set of graphs and visuals for your results.

### Visualizations
The app can produce some graphs and heatmaps for results if you wish to analyze them quickly. To start with, on the main menu select visualize results. From the next window you can select add group to add a cluster of results. You can use this for whatever you like, but you may use it to group samples based on the rock they came from. Next if you select the blue + sign, you can add individual accepted files ( ex: `User > Results > Carbonate > sol_0489-detail_1_1 > sol_0489-detail_1_Approved.csv` )

![image](https://github.com/TrevorJohst/SHERLOC-Mineral-Detection/assets/122303295/75da5ff9-8a54-4d75-b3d5-efd10ff87018)

When you are done adding groups and samples you can click the export button. After a moment you will be taken back to the main menu and a new folder will be created with your results. Below is an example of some results that can automatically produced. 

![smd_results](https://github.com/TrevorJohst/SHERLOC-Mineral-Detection/assets/122303295/55cf07e3-f855-4750-a834-a94b1ea5ef89)

The program will take the first alphabetical file in the img folder ( located at `User > Data > sol_0489 > detail_1 > SrlcSpecSpec... > img` ), so if you have a colorized version of the image you can place it there and it will be used instead. If this is done, make sure the colorized version is aligned with the original grayscale version so plotted points remain accurate. 

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
