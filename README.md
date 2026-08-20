# Optical Model Validation

## TODO:
- Finish "Zemax Setup" set up
- Add Zemax comparison instructions to prcedures
- "What can we conclude" in overview
- Fix FOV/EFL table
- MTF procedure
- Add images
    - "ensure graph looks like this"
    - combo image of targets
    - experiment setup
    - 

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
    ├── figures/               # Figures displayed in the README
    ├── requirements.txt       # Required Python packages
    └── README.md              # Project documentation

```

## Preparation

### Required Equipment
- Optical system for test
- Stable, movable test bench
- Printed imaging targets
- Digital calipers with at least a 0.01 mm resolution
- Measuring tape

### Software Setup

Install [Python](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads) before continuing.

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

3. Create an empty folder named `test_images` inside the project:

   ```bash
   mkdir test_images

### Zemax Setup

Install [Ansys Zemax OpticStudio](https://ansys.synopsys.com/en-gb//academic/students/ansys-student)

### General Setup 

1. Print targets on matte-white paper/cardstock with the highest print quality setting available. Disable any options such as "fit to page" that changes the target dimensions 

2. Secure camera to test bench

3. Align targets onto a vertical surface, perpendicular to the camera's optical axis

4. Position camera so that targets appear as large as possible while ensuring the margins fit comfortably within the image

5. Ensure the targets are flat and evenly illuminated. Try to eliminate glare, shadows, and reflections 

6. Disable automatic image adjustments where possible

8. Record results in [this spreadsheet template](https://docs.google.com/spreadsheets/d/19bQ3YoSR_WSW7G-d8i1SoJNDLfoneezhGHcqGAoD-7E/edit?usp=sharing)

## Test Procedures

### Best Focus

1. Prepare Siemens star target and general setup
2. Align the center of the target with the camera's optical axis
3. Measure and record parallel to the optical axis the distance between target plane and front face of the lens housing
4. Establish a rough expected best-focus position. Offset the thread by 0.80mm from the expected best-focus position
5. Capture an image of the target. Save the image file in test_images/ and rename the image with thread position information
6. Adjust the thread by an increment of 0.10mm towards the direction of the expected best-focus position
7. Perform a "coarse sweep". Repeat steps 5 and 6 until 15 images are captured. Ensure each increment is constant for this step
8. Run the "best_focus.py" analysis script using the images taken in the last sweep
9. Determine a new expected best focus position near the peak of the "Image sharpness vs. thread position" graph
10. Offset the thread by 0.25mm from the new expected best-focus position.
11. Perform a "fine sweep". Take 15 more images with a thread position increment of 0.03mm. 
12. Determine the best focus position from the peak of the graph
13. Compare 
14. Record thread position and corresponding laplacian value outputs from the terminal into the data entry template

### Field of View and Effective Focal Length

1. Prepare checkerboard target and general setup
2. Measure the size of each square in milimeters
3. Position camera so that target takes up roughly 50% - 80% of the frame
3. Align the center of the target with the camera's optical axis
4. Measure and record parallel to the optical axis the distance between target plane and front face of the lens housing
5. Capture at least 3 images without adjusting the setup
6. Run "fov_efl.py" analysis script with only images taken from the same object distance
7. Perform steps 3-7 for 2 other distances
8. Record mean EFL, horizontal half-field, and vertical half-field for all 3 trials 

### Modulation Transfer Function (MTF)

1. Use the thread position determined in "Best Focus " for the latter procedures