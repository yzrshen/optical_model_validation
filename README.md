# Optical Model Validation

## Overview
This repository contains python tools to experimentally validate the accuracy of a digital optical model (ex. Ansys Zemax OpticStudio) with respect to its corresponding physical system. 
The objective is to establish sufficient agreement between simulated and experimental performance, thereby increasing confidence in the model’s use for subsequent optical analysis. Features include: 

### Experimental Measurements
- Optimal thread position for best focus using Laplacian Variance
- System's field-of-view and effective-focal-length
- Modulation Transfer Functions across different field positions

### Imaging Targets
- 10 x 10 checkerboard pattern
- 2500 x 2500 px slanted edge target with 5&deg; edge angle 
- 2500 x 2500 px Siemen's star target

Scripts for generating each target are included. Target dimensions and other image parameters can be easily modified.

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
    │   ├── best_focus.py
    │   ├── siemens.py
    │   └── slanted_edge.
    ├── requirements.txt       # Required Python packages
    └── README.md              # Project documentation
```

## Procedure

### Installation and Setup

1. Clone the repository and enter the project folder:

   ```bash
   git clone <repository-url>
   cd optical_model_validation
   ```
2. 
