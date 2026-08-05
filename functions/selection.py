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

    root = tk.Tk()
    root.withdraw()

    image_paths = filedialog.askopenfilenames(
        title="Select checkerboard photographs, hold ctrl to select multiple",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
            ("All files", "*.*")
        ]
    )

    if not image_paths:
        print("No images were selected.")
        root.destroy()
        raise SystemExit

    return image_paths

def ask_user_input(prompt, title="User input"):
    """
    Purpose: Request user input with text box
    Parameter(s): prompt, tit;e
    Return(s): user_input
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
