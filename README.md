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


### Processing

### Visualizations


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
