import cv2
import numpy as np
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import filedialog, simpledialog
from pathlib import Path

def detect_green_roi(image, margin):

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
    x += margin
    y += margin
    width -= 2*margin
    height -= 2*margin

    return x, y, width, height

# Open and hide root window
root = tk.Tk()
root.withdraw()

# Ask for amount of images
image_count = simpledialog.askinteger(
    "User Input",
    "Number of images:"
)
# End program if user cancels
if image_count is None:
    root.destroy()
    raise SystemExit("User cancelled, program terminated")

file_names = []
offsets = []
sharpnesses = []

# Loop for each image
for i in range(image_count):
    
    # Create file selection screen
    image_path = filedialog.askopenfilename(
    title = "Select test image",
    filetypes = [
        ("image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
        ("all files", "*.*")
    ]
    )
    # Check if image was selected
    if not image_path:
        print(f"No image selected for image {i + 1}")
        continue

    # Open image
    image = cv2.imread(image_path)
    # Check to see image opens
    if image is None:
       print(f"{Path(image_path).name} could not be opened")
       continue
    print(f"File opened: {Path(image_path).name}")

    # Ask for thread offset
    thread_offset_mm = simpledialog.askfloat(
        "User input",
        "Thread offset (mm)"
    )
    if thread_offset_mm is None:
        print("No user input, next image")
        continue
    offsets.append(thread_offset_mm)

    # Find green frame and crop image to inside of frame
    x, y, width, height = detect_green_roi(image, 5)
    crop = image[
    y : y+height,
    x : x+width
    ]

    gray_image = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # Gaussian blur to reduce noise                # Kernel dimensions
    smoothed_image = cv2.GaussianBlur(gray_image, (3, 3), 0)

    # Apply laplacian to find edges
    laplacian_image = cv2.Laplacian(
    smoothed_image,
    cv2.CV_64F,
    ksize = 1
    )

    # Calculate sharpness
    sharpness = laplacian_image.var()
    sharpnesses.append(sharpness)

    # Show laplacian image
    plt.figure()
    plt.imshow(np.abs(laplacian_image), cmap="gray")
    plt.show()

print(offsets)
for sharpness in sharpnesses:
    print(f"{sharpness:.2f}")

plt.figure()
plt.scatter(offsets, sharpnesses)
plt.xlabel("Thread offset (mm)")
plt.ylabel("Laplacian variance")
plt.title("Image sharpness vs. focus position")
plt.show()


root.destroy()




