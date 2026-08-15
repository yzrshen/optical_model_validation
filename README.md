# Optical Model Validation

## Overview
This repository contains the tools and instructions needed to experimentally validate the accuracy of a digital optical model (e.g., Ansys Zemax OpticStudio) against its corresponding physical counterpart. 
The objective is to create a repeatable procedure for conducting a preliminary comparison of an optical system's simulated and experimental performance. The results can then be used to assess the simulation’s credibility for subsequent optical analysis. 


### Supported Experimental Measurements
- Finding the optimal thread position for best focus
- Calculating the system's field of view and effective focal length
- Modulation Transfer Functions across different field positions

### Imaging Targets
- 2500 x 2500 px Siemens star target
- 10 x 10 checkerboard pattern
- 2500 x 2500 px slanted edge target with 5&deg; edge angle 

Respective scripts for generating each target are included. Target dimensions and other image parameters can be easily modified.

### Data Entry
- Google Sheets template for recording experimental results

## Repository Structure

```text
optical_model_validation/
    ├── target_scripts/        # Printable target-generating scripts
    │   ├── siemens.py
    │   ├── checkerboard.py
    │   └── slanted_edge.py
    ├── targets/               # Image folder of targets
    │   ├── siemens.png
    │   ├── checkerboard.png
    │   └── slanted_edge.png
    ├── test_images/           # Empty test image storage folder
    ├── analysis_scripts/      # Image analysis scripts
    │   ├── best_focus.py
    │   ├── fov_efl.py
    │   └── mtf_fp.py
    ├── requirements.txt       # Required Python packages
    └── README.md              # Project documentation
```

## Procedure

### Required Equipment
- Optical system for test
- Stable, movable test bench
- Printed imaging targets
- Digital calipers with at least a 0.01 mm resolution
- Measuring tape

### Physical Setup 

1. Print targets on matte-white paper/cardstock with the highest print quality setting available. Disable any options such as "fit to page" that changes the target dimensions 

2. Secure camera to test bench

3. Align targets onto a vertical surface, perpendicular and centered to the camera's optical axis

4. Position camera so that targets appear as large as possible while ensuring the margins fit comfortably within the image

5. Ensure the targets are flat and evenly illuminated. Try to eliminate glare, shadows, and reflections 

6. Disable automatic image adjustments where possible

7. Record results in [this spreadsheet template](https://docs.google.com/spreadsheets/d/19bQ3YoSR_WSW7G-d8i1SoJNDLfoneezhGHcqGAoD-7E/edit?usp=sharing)

### Software Setup

**Prerequisites:** Install [Python](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads) before continuing.

Open a terminal and run the following commands:

1. Clone the repository and enter the project folder

   ```bash
   git clone <https://github.com/yzrshen/optical_model_validation.git>
   cd optical_model_validation
   ```
2. Install required packages

    ```bash
    pip install -r requirements.txt
    ```

### Best Focus Test

1. Prepare Siemens star target
2. Establish a rough expected best-focus position. Offset the thread by 0.80mm from the expected best-focus position
3. Capture an image of the target. Save the image file in test_images/ and rename the image with thread position information
4. Adjust the thread by an increment of 0.10mm towards the direction of the expected best-focus position
5. Perform a "coarse sweep". Repeat steps 3-4 until 15 images are captured. Ensure each increment is constant for this step
6. Run the best-focus analysis program using the images taken in the last sweep
7. Determine a new expected best focus position near the peak of the "Image sharpness vs. thread position" graph
8. Offset the thread by 0.25mm from the new expected best-focus position.
9. Perform a "fine sweep". Repeat steps 5 and 6 with a new increment of 0.03mm. 
10. Determine the best focus position from the peak of the graph
11. Record thread position and corresponding laplacian value outputs from the terminal into the data entry template

### Field of View and Effective Focal Length

1. Prepare checkerboard target

### Modulation Transfer Function (MTF)


