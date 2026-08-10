# Optical Model Validation

## Overview
This repository contains the tools and instructions needed to experimentally validate the accuracy of a digital optical model (e.g., Ansys Zemax OpticStudio) against its corresponding physical counterpart. 
The objective is to create a repeatable procedure for conducting a preliminary comparison of an optical system's simulated and experimental performance. The results can then be used to assess the simulation’s credibility for subsequent optical analysis. 


### Supported Experimental Measurements
- Calculating the system's field of view and effective focal length
- Finding the optimal thread position for best focus
- Modulation Transfer Functions across different field positions

### Imaging Targets
- 10 x 10 checkerboard pattern
- 2500 x 2500 px slanted edge target with 5&deg; edge angle 
- 2500 x 2500 px Siemen's star target

Respective scripts for generating each target are included. Target dimensions and other image parameters can be easily modified.

### Data Entry
- Google Sheets template for recording experimental results

## Repository Structure

```text
optical_model_validation/
    ├── target_scripts/        # Printable target-generating scripts
    │   ├── checkerboard.py
    │   ├── siemens.py
    │   └── slanted_edge.py
    ├── targets/               # Image folder of targets
    │   ├── checkerboard.png
    │   ├── siemens.png
    │   └── slanted_edge.png
    ├── test_images/           # Empty test image storage folder
    ├── analysis_scripts/      # Image analysis scripts
    │   ├── fov_efl.py
    │   ├── best_focus.py
    │   └── mtf_fp.py
    ├── requirements.txt       # Required Python packages
    └── README.md              # Project documentation
```

## Procedure

### General Test Setup

1. Print targets on matte-white paper/cardstock with the highest print quality setting available. Disable any options such as "fit to page" that changes the target dimensions 

2. Mount the camera securely onto a table or stand

3. Position printed targets perpendicular and centered to the camera's optical axis

4. Ensure the target is flat and evenly illuminated. Avoid glare, shadows, and reflections

5. **Optional:** Record results in [this spreadsheet template](https://docs.google.com/spreadsheets/d/19bQ3YoSR_WSW7G-d8i1SoJNDLfoneezhGHcqGAoD-7E/edit?usp=sharing)

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

### Field of View and Effective Focal Length