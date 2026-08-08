import cv2
import matplotlib.pyplot as plt
import numpy as np

import tkinter as tk
from tkinter import filedialog, simpledialog

# ---------------------------------------------------------
# Open a file-selection window
# ---------------------------------------------------------

# Create a Tkinter window
root = tk.Tk()
# Hide window
root.withdraw()

image_path = filedialog.askopenfilename(
    title="Select slanted edges photograph",
    filetypes=[
        ("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
        ("All files", "*.*")
    ]
)

# Stop if no photographs were selected.
if not image_path:
    print("No images were selected.")
    root.destroy()
    raise SystemExit

image = cv2.imread(image_path)
# Convert image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# Destroy root window
root.destroy()


# ---------------------------------------------------------
# Isolate crop from green margin
# ---------------------------------------------------------

# Convert to HSV
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define green (hue, saturation, value)
lower_green = np.array([35, 50, 40])
upper_green = np.array([90, 255, 255])

# Create black-and-white image "green_mask"
# Accepted pixels = white
# Pixels not in range = black
green_mask = cv2.inRange(
    hsv_image,
    np.array([35, 50, 40]),
    np.array([90, 255, 255])
)

# Contours = list of detected boundaries. 
# Each contours[i] is an array of (x, y) points tracing the outline of one white region
    # Contours[0] = Outer boundary
    # Contours[1] = Inner boundary
# Hierarchy[0][i] = [next, previous, first_child, parent] for contours[i]
contours, hierarchy = cv2.findContours( 
    green_mask, 
    cv2.RETR_TREE, # Find every contour and construct the complete parent–child hierarchy
    cv2.CHAIN_APPROX_SIMPLE # Compresses each contour by removing unnecessary points along straight lines
)

# Check if any contour relationships were found
if hierarchy is None:
    raise SystemExit("No green frame detected")

# Gets rid of unnecessary outer dimension
hierarchy = hierarchy[0]


inside_contours = []
# enumerate returns both index and contour information
# i recieves index and loops for every index in contours[]
# contour recieves contour[i] information
for i, contour in enumerate(contours):
    # Checks parent of contour. If parent is not -1, must be an inside contour
    if hierarchy[i][3] != -1:
        inside_contours.append(contour)

if not inside_contours:
    raise SystemExit("Green frame is not closed")

# Find inside contour with largest area
inside_contour = max(
    inside_contours,
    key=cv2.contourArea   # Compare enclosed area instead of coordinate array
)

# x = left edge of rectangle
# y = top edge of rectangle
x, y, width, height = cv2.boundingRect(inside_contour)

# Remove 6 pixel margin from each edge
margin = 3
x += margin
y += margin
width -= 2*margin
height -= 2*margin

crop = gray_image[
    y : y+height,
    x : x+width
]


# ---------------------------------------------------------
# Find field position of slanted edge
# ---------------------------------------------------------

# Find center of original image in coordinates
original_height, original_width = image.shape[:2]
center_x = original_width / 2
center_y = original_height / 2

# Find center of crop in coordinates
crop_height, crop_width = crop.shape[:2]

crop_center_x = x + crop_width / 2
crop_center_y = y + crop_height / 2

# Calculate distance between image centers
distance_x = crop_center_x - center_x
distance_y = center_y - crop_center_y

# Convert distances into normalized field positions
field_x = distance_x / (original_width / 2)
field_y = distance_y / (original_height / 2)

print(f"Field position: ({field_x:.3f}, {field_y:.3f})")


# ---------------------------------------------------------
# Find the edge position in every row
# ---------------------------------------------------------

# Calculate horizontal brightness change.
# axis=1 means calculate the change from left to right.
row_gradients = np.gradient(crop, axis=1)

edge_positions = []

# Run code once for every row in the crop
# range(2, 6) = 2, 3, 4, 5
for row_number in range(crop.shape[0]):

    # Finds all absolute values for change in brightness for current row
    gradient_strength = np.abs(row_gradients[row_number])

    # Find the pixel with the strongest brightness change
    # argmax returns index with largest value
    peak_column = np.argmax(gradient_strength)

    # Examine 5 columns around the peak for a more accurate position
    start = max(0, peak_column - 2)
    #crop.shape[1] = number of columns (0-199)
    end = min(crop.shape[1], peak_column + 3)

    # Creates array of numbers beginning at start and stopping before end
    columns = np.arange(start, end)
    # Finds gradient values of these 5 columns
    weights = gradient_strength[start:end]

    # Check that we are not dividing by 0
    if np.sum(weights) > 0:
        # Weighted-average position gives a subpixel edge location
        subpixel_position = np.sum(columns * weights) / np.sum(weights)
    # If we are dividing by 0, use position of peak column
    else:
        subpixel_position = float(peak_column)

    # Store subpixel result 
    edge_positions.append(subpixel_position)
#Convert list into NumPy array 
edge_positions = np.array(edge_positions)


# ---------------------------------------------------------
# Fit a straight line through the edge positions
# ---------------------------------------------------------

# Creates a vertical coordinate for every row
row_coordinates = np.arange(crop.shape[0])

# np.polyfit(x_data, y_data, degree)
# outputs slope, intercept
slope, intercept = np.polyfit(
    row_coordinates,
    edge_positions,
    1
)

# Converts noise from points into fitted coordinates
fitted_edge_positions = slope * row_coordinates + intercept


# ---------------------------------------------------------
# Calculate every pixel's perpendicular distance
#    from the fitted edge
# ---------------------------------------------------------

# Creates 2 arrays each with the crop shape
# y_coordinates contain each pixel's row number
# x_coordinates contain each pixel's column number
y_coordinates, x_coordinates = np.indices(crop.shape)

# Formula calculates signed perpendicular (shortest) distance
# from each pixel to that line
# distance_from_edge is a 2D array with crop shape
distance_from_edge = (
    x_coordinates
    - slope * y_coordinates
    - intercept
) / np.sqrt(1 + slope**2)

# Flatten the 2D arrays into matching 1D arrays
distances = distance_from_edge.ravel()
intensities = crop.ravel()


# ---------------------------------------------------------
# Bin pixels by perpendicular distance
# ---------------------------------------------------------

oversampling = 4

# With 4x oversampling, each ESF bin is 0.25 pixel wide
bin_width = 1.0 / oversampling

minimum_distance = distances.min()
maximum_distance = distances.max()

# Creates 1D array using np.arange(start, stop, step)
bin_edges = np.arange(
    minimum_distance,
    # arange usually excludes stopping value, hence maximum_distance + bin_width
    maximum_distance + bin_width,
    bin_width
)

# bin_numbers = 1D array with info on which bin each pixel belongs to
# x = np.array([0.2, 0.8, 1.4, 2.7])
# bin_edges = np.array([0, 1, 2, 3])
# np.digitze(x, bin_edges) = [1, 1, 2, 3]
bin_numbers = np.digitize(distances, bin_edges) - 1

number_of_bins = len(bin_edges) - 1
# Create array with shape number_of_bins filled with empty values
esf = np.full(number_of_bins, np.nan)

# Loop for every bin number
for bin_number in range(number_of_bins):

    # 1D array that takes all the intensities of every bin
    pixels_in_bin = intensities[bin_numbers == bin_number]

    # Averages each bin's intensities and stores it in esf[] with index bin_number
    if len(pixels_in_bin) > 0:
        esf[bin_number] = np.mean(pixels_in_bin)


# The center distance of each bin from the fitted edge line
esf_distance = (
    # [:-1] = every index but the last
    # [1:]  = index 1 onwards
    bin_edges[:-1] + bin_edges[1:]
) / 2


# ---------------------------------------------------------
# Fill empty bins by interpolation *** MOSTLY UNNECESSARY
# ---------------------------------------------------------

# np.isnan outputs boolean array, valid_bins[i] == true if esf[i] == NaN
# ~ reverses values, valid_bins[i] == true if esf[i] != NaN
valid_bins = ~np.isnan(esf)

# New esf array including interpolations for empty bin edges
# np.interp(x, xp, fp)
# x:  The positions where you want values.
# xp: The positions where you already know the values.
# fp: The known values corresponding to xp.
esf = np.interp(
    esf_distance,
    esf_distance[valid_bins],
    esf[valid_bins]
)


# ---------------------------------------------------------
# Make sure the ESF rises from dark to bright
# ---------------------------------------------------------

# If last esf value is darker than first esf value
if esf[-1] < esf[0]:
    # Reverse intensity array
    esf = esf[::-1]
    # Reverse distance array to match intensities, while preserving increasing distance
    esf_distance = -esf_distance[::-1]


# Normalize brightness from 0 to 1
esf = (esf - np.min(esf)) / (np.max(esf) - np.min(esf))


# ---------------------------------------------------------
# Calculate the LSF
# ---------------------------------------------------------

# Differentiate the ESF with respect to distance
lsf = np.gradient(esf, bin_width)


# ---------------------------------------------------------
# Apply a window before the Fourier transform
# ---------------------------------------------------------

# Apply Hamming filter
window = np.hamming(len(lsf))
windowed_lsf = lsf * window


# ---------------------------------------------------------
# Calculate the MTF
# ---------------------------------------------------------

mtf = np.abs(np.fft.rfft(windowed_lsf))

# Normalize so MTF begins at 1, or 100%
mtf = mtf / mtf[0]

# Because the ESF spacing is bin_width pixels,
# the frequency unit is cycles per pixel
# cpp = cycles per pixel
frequencies_cpp = np.fft.rfftfreq(
    len(windowed_lsf),
    d=bin_width
)


# ---------------------------------------------------------
# Plot the detected edge
# ---------------------------------------------------------

# Create new empty plot window
plt.figure()

# Show greyscaled cropped image 
plt.imshow(crop, cmap="gray")

# plt.plot(x_values, y_values, style, label=...)
plt.plot(
    edge_positions,
    row_coordinates,
    # Show as dot instead of line
    ".",
    label="Detected edge positions"
)

plt.plot(
    fitted_edge_positions,
    row_coordinates,
    label="Fitted edge"
)

plt.xlabel("Column, pixels")
plt.ylabel("Row, pixels")
plt.title("Slanted-edge detection")
plt.legend()
plt.show()


# ---------------------------------------------------------
# Plot the oversampled ESF
# ---------------------------------------------------------

plt.figure()
plt.plot(esf_distance, esf)
plt.xlabel("Perpendicular distance from edge, pixels")
plt.ylabel("Normalized brightness")
plt.title("Oversampled Edge Spread Function")
plt.grid()
plt.show()


# ---------------------------------------------------------
# Plot the LSF
# ---------------------------------------------------------

plt.figure()
plt.plot(esf_distance, lsf)
plt.xlabel("Perpendicular distance from edge, pixels")
plt.ylabel("Brightness change")
plt.title("Line Spread Function")
plt.grid()
plt.show()


# ---------------------------------------------------------
# Plot the MTF
# ---------------------------------------------------------

# Allows text entry field inside graph
from matplotlib.widgets import TextBox

plt.figure()
plt.subplots_adjust(bottom=0.2)

plt.plot(frequencies_cpp, mtf * 100)

# 0.5 cpp is Nyquist frequency
plt.xlim(0, 0.5)
plt.ylim(0, 105)

plt.xlabel("Spatial frequency, cycles/pixel")
plt.ylabel("Contrast transfer, %")
plt.title("Modulation Transfer Function")
plt.grid()


def calculate_mtf(text):
    frequency = float(text)

    # np.interp(requested_x, known_x_values, known_y_values)
    mtf_value = np.interp(
        frequency,
        frequencies_cpp,
        mtf * 100
    )
    print(f"MTF at {frequency} cycles/pixel: {mtf_value:.1f}%")

# Create area for input box [left position, bottom position, width, height]
    # Decimals values represent percent of the figure
box_area = plt.axes([0.35, 0.05, 0.25, 0.06])
frequency_box = TextBox(box_area, "Frequency: ")

# Run calculate_mtf when user presses enter
frequency_box.on_submit(calculate_mtf)

plt.show()