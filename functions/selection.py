import cv2
import numpy as np


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

def field_position(image, crop, x, y):

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

    return field_x, field_y

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

