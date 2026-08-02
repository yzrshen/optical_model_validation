import cv2
import numpy as np
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import filedialog, simpledialog
from pathlib import Path


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

    # Greyscale image 
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Ask for thread offset
    thread_offset_mm = simpledialog.askfloat(
        "User input",
        "Thread offset (mm)"
    )
    if thread_offset_mm is None:
        print("No user input, next image")
        continue
    offsets.append(thread_offset_mm)

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




