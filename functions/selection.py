from logging import root

import cv2
import numpy as np
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, simpledialog


def select_crop(image, max_width, max_height):

    original_height, original_width = image.shape

    # Finds smallest scaling factor to ensure both dimensions fit in window
    scale = min(
        max_width / original_width,
        max_height / original_height,
        1.0
    )

    display_image = cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale
    )

    x, y, width, height = cv2.selectROI(
        "Select crop",
        display_image
    )

    cv2.destroyAllWindows()

    # Convert selection coordinates to original-image coordinates
    # round() rounds to nearest integer
    x = round(x / scale)
    y = round(y / scale)
    width = round(width / scale)
    height = round(height / scale)

    crop = image[
        y:y + height,
        x:x + width
    ]

def select_images():

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

def ask_user_input(prompt, title="User input"):
    """
    Display a text-entry window and return the entered text.

    Returns None if the user presses Cancel or closes the window.
    """

    root = tk.Tk()
    root.withdraw()

    user_input = simpledialog.askstring(
        title=title,
        prompt=prompt,
        parent=root
    )

    root.destroy()

    return user_input

def find_user_input(text, known_x_values, known_y_values):
    """
    Purpose: Output interpolated y-value with user-given x-value
    Parameter(s):   
        text: User input
        known_x_values
        known_y_values
    Return(s): requested_y
    """
    requested_x = float(text)

    requested_y = np.interp(
        requested_x,
        known_x_values,
        known_y_values
    )
    return requested_y

ask_user_input("this is it", "hi")