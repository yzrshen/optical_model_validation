import cv2
import math
import numpy as np
import tkinter as tk
from pathlib import Path
# filedialog creates file-selection window
# simpledialog creates small input windows that ask the user for values
from tkinter import filedialog, simpledialog


# ---------------------------------------------------------
# Open a file-selection window
# ---------------------------------------------------------

# Create a Tkinter window
root = tk.Tk()
# Hide window
root.withdraw()

# Let the user select one or more checkerboard photographs
# "image_paths" is a tuple that stores image file paths in order
image_paths = filedialog.askopenfilenames(
    title="Select checkerboard photographs, hold ctrl to select multiple",
    filetypes=[
        ("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
        ("All files", "*.*")
    ]
)

# Stop if no photographs were selected.
# "not" returns True when a value is empty, zero, False, or Non
if not image_paths:
    print("No images were selected.")
    # Close root window
    root.destroy()
    # Stop program
    raise SystemExit


# ---------------------------------------------------------
# Ask the user for the measurement information
# ---------------------------------------------------------

# Enter the number of inner corners
corner_rows = 9

corner_columns = 9

square_size_mm = simpledialog.askfloat(
    "Checkerboard information",
    "Checker-square size (mm):"
)

pixel_pitch_um = simpledialog.askfloat(
    "Camera information",
    "Sensor pixel pitch (µm):"
)

object_distance_mm = simpledialog.askfloat(
    "Camera information",
    "Distance from checkerboard to lens principal plane (mm):"
)

# Stop if the user cancelled any input window
if None in (
    corner_rows,
    corner_columns,
    square_size_mm,
    pixel_pitch_um,
    object_distance_mm
):
    print("Input was cancelled.")
    root.destroy()
    raise SystemExit

# Check that all entered values are usable
if (
    square_size_mm <= 0
    or pixel_pitch_um <= 0
    or object_distance_mm <= 0
):
    print("All measurements must be positive, and corner counts must be at least 2.")
    root.destroy()
    raise SystemExit

# OpenCV expects the checkerboard pattern as (columns, rows)
pattern_size = (corner_columns, corner_rows)

# Convert the pixel pitch from micrometres to millimetres
pixel_pitch_mm = pixel_pitch_um / 1000


# ---------------------------------------------------------
# Calculate the known checkerboard dimensions
# ---------------------------------------------------------

# Calculate the distance from the first detected inner corner
# to the last detected inner corner
# Nine inner corners contain eight corner-to-corner intervals
checkerboard_width_mm = (
    corner_columns - 1
) * square_size_mm

checkerboard_height_mm = (
    corner_rows - 1
) * square_size_mm


# ---------------------------------------------------------
# List results
# ---------------------------------------------------------

# Each successful image will add one value to each list.
file_names = []

horizontal_coverages_mm = []
vertical_coverages_mm = []

horizontal_fovs_deg = []
vertical_fovs_deg = []
diagonal_fovs_deg = []

horizontal_efls_mm = []
vertical_efls_mm = []
mean_efls_mm = []


# ---------------------------------------------------------
# Open and analyze each checkerboard photograph
# ---------------------------------------------------------

# Runs once for each image in image paths
# 1st loop: image_path = image_paths[0] = image1.jpg
# 2nd loop: image_path = image2.jpg etc..
for image_path in image_paths:

    # Open the photograph
    image = cv2.imread(image_path)

    if image is None:
        print(f"Could not open: {image_path}")  # f tells python to evaluate value inside quotations
        continue    # Stop current loop and return to top (next image)

    # Find the full image width and height in pixels.
        # [:2] -> Only take first 2 values, height and width
    image_height_px, image_width_px = image.shape[:2]

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


    # -----------------------------------------------------
    # Detect the checkerboard inner corners
    # -----------------------------------------------------

    # findChessboardCornersSB returns:
    # found   = true/false
    # corners = detected inner-corner coordinates
        # 3D NumPy array (total_corners, 1, 2)
    found, corners = cv2.findChessboardCornersSB(
        gray_image,
        pattern_size,
        flags=(
            cv2.CALIB_CB_NORMALIZE_IMAGE
            | cv2.CALIB_CB_EXHAUSTIVE
        )
    )

    if not found:
        print(
            f"Checkerboard was not detected in: "   
            f"{Path(image_path).name}" 
        )
        continue

    # Organize the detected corners by checkerboard row and column
    # Each corner stores its (x, y) pixel coordinates
    # corners[2, 4, 0] -> x coordinate
    # corners[2, 4, 1] -> y coordinate
    corners = corners.reshape(
        corner_rows,
        corner_columns,
        2
    )


    # -----------------------------------------------------
    # Measure the checkerboard in image pixels
    # -----------------------------------------------------

    # For every checkerboard row, create a vector from its
    # first inner corner to its last inner corner
    horizontal_vectors = (
        corners[:, -1, :]       # All rows, last column, both coordinates
        - corners[:, 0, :]      # All rows, first column, both coordinates
    )

    # Calculate each vector's length, then take the mean
    checkerboard_width_px = np.mean(
        np.linalg.norm(
            horizontal_vectors,
            # axis = 1 sqrt(x^2 + y^2) uses values down each row
            # axis = 1 -> uses values down each column
            # no axis -> every number in array, returns 1 number
            axis=1
        )
    )

    # For every checkerboard column, create a vector from its
    # first inner corner to its last inner corner
    vertical_vectors = (
        corners[-1, :, :]
        - corners[0, :, :]
    )

    # Calculate each vector's length, then take the mean
    checkerboard_height_px = np.mean(
        np.linalg.norm(
            vertical_vectors,
            axis=1
        )
    )


    # -----------------------------------------------------
    # Calculate magnification and object-plane coverage
    # -----------------------------------------------------

    # Checkerboard's image -> millimetres on the sensor.
    checkerboard_image_width_mm = (
        checkerboard_width_px
        * pixel_pitch_mm
    )

    checkerboard_image_height_mm = (
        checkerboard_height_px
        * pixel_pitch_mm
    )

    # Magnification = image size / object size
    horizontal_magnification = (
        checkerboard_image_width_mm
        / checkerboard_width_mm
    )

    vertical_magnification = (
        checkerboard_image_height_mm
        / checkerboard_height_mm
    )

    # Scale the known checkerboard dimensions to the full image.
    horizontal_coverage_mm = (
        checkerboard_width_mm
        * image_width_px
        / checkerboard_width_px
    )

    vertical_coverage_mm = (
        checkerboard_height_mm
        * image_height_px
        / checkerboard_height_px
    )

    diagonal_coverage_mm = math.hypot(
        horizontal_coverage_mm,
        vertical_coverage_mm
    )


    # -----------------------------------------------------
    # Calculate field of view
    # -----------------------------------------------------

    # Full FOV = 2 * arctan(half coverage / object distance)
    horizontal_fov_deg = math.degrees(      # Converts radians into degrees
        2 * math.atan(
            horizontal_coverage_mm
            / (2 * object_distance_mm)
        )
    )

    vertical_fov_deg = math.degrees(
        2 * math.atan(
            vertical_coverage_mm
            / (2 * object_distance_mm)
        )
    )

    diagonal_fov_deg = math.degrees(
        2 * math.atan(
            diagonal_coverage_mm
            / (2 * object_distance_mm)
        )
    )

    # Zemax normally uses half-field angles
    horizontal_half_field_deg = horizontal_fov_deg / 2
    vertical_half_field_deg = vertical_fov_deg / 2


    # -----------------------------------------------------
    # Calculate effective focal length
    # -----------------------------------------------------

    # Thin-lens finite-distance equation:
    #
    # EFL = magnification * object distance
    #       --------------------------------
    #              1 + magnification
    horizontal_efl_mm = (
        horizontal_magnification
        * object_distance_mm
        / (1 + horizontal_magnification)
    )

    vertical_efl_mm = (
        vertical_magnification
        * object_distance_mm
        / (1 + vertical_magnification)
    )

    mean_efl_mm = (
        horizontal_efl_mm
        + vertical_efl_mm
    ) / 2


    # -----------------------------------------------------
    # Store and print this image's results
    # -----------------------------------------------------

    file_names.append(Path(image_path).name)

    # Adds value to previously made arrays
    horizontal_coverages_mm.append(horizontal_coverage_mm)
    vertical_coverages_mm.append(vertical_coverage_mm)

    horizontal_fovs_deg.append(horizontal_fov_deg)
    vertical_fovs_deg.append(vertical_fov_deg)
    diagonal_fovs_deg.append(diagonal_fov_deg)

    horizontal_efls_mm.append(horizontal_efl_mm)
    vertical_efls_mm.append(vertical_efl_mm)
    mean_efls_mm.append(mean_efl_mm)

    print("\n----------------------------------------")
    print("Image:", Path(image_path).name)
    print("----------------------------------------")

    print(
        f"Horizontal object coverage: "
        f"{horizontal_coverage_mm:.3f} mm"
    )

    print(
        f"Vertical object coverage:   "
        f"{vertical_coverage_mm:.3f} mm"
    )

    print(
        f"Horizontal full FOV:        "
        f"{horizontal_fov_deg:.3f} degrees"
    )

    print(
        f"Vertical full FOV:          "
        f"{vertical_fov_deg:.3f} degrees"
    )

    print(
        f"Diagonal full FOV:          "
        f"{diagonal_fov_deg:.3f} degrees"
    )

    print(
        f"Zemax horizontal half-field: "
        f"{horizontal_half_field_deg:.3f} degrees"
    )

    print(
        f"Zemax vertical half-field:   "
        f"{vertical_half_field_deg:.3f} degrees"
    )

    print(
        f"Horizontal EFL:             "
        f"{horizontal_efl_mm:.3f} mm"
    )

    print(
        f"Vertical EFL:               "
        f"{vertical_efl_mm:.3f} mm"
    )

    print(
        f"Mean EFL:                   "
        f"{mean_efl_mm:.3f} mm"
    )


# ---------------------------------------------------------
# Calculate statistics for multiple images
# ---------------------------------------------------------

number_of_results = len(file_names)

if number_of_results == 0:
    print("\nNo images were successfully analyzed.")

elif number_of_results > 1:
    print("\n========================================")
    print("MULTIPLE-IMAGE SUMMARY")
    print("========================================")

    print(
        f"Horizontal FOV: "
        f"{np.mean(horizontal_fovs_deg):.3f} degrees mean, "
        # Standard deviation formula
        f"{np.std(horizontal_fovs_deg, ddof=1):.3f} degrees SD"
    )

    print(
        f"Vertical FOV:   "
        f"{np.mean(vertical_fovs_deg):.3f} degrees mean, "
        f"{np.std(vertical_fovs_deg, ddof=1):.3f} degrees SD"
    )

    print(
        f"Diagonal FOV:   "
        f"{np.mean(diagonal_fovs_deg):.3f} degrees mean, "
        f"{np.std(diagonal_fovs_deg, ddof=1):.3f} degrees SD"
    )

    print(
        f"Horizontal EFL: "
        f"{np.mean(horizontal_efls_mm):.3f} mm mean, "
        f"{np.std(horizontal_efls_mm, ddof=1):.3f} mm SD"
    )

    print(
        f"Vertical EFL:   "
        f"{np.mean(vertical_efls_mm):.3f} mm mean, "
        f"{np.std(vertical_efls_mm, ddof=1):.3f} mm SD"
    )

    print(
        f"Combined EFL:   "
        f"{np.mean(mean_efls_mm):.3f} mm mean, "
        f"{np.std(mean_efls_mm, ddof=1):.3f} mm SD"
    )


# ---------------------------------------------------------
# Close Tkinter
# ---------------------------------------------------------

root.destroy()