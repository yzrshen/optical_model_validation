import cv2
import numpy as np
from pathlib import Path
from functions.image_tools import array_to_image


# Image settings
image_size_px = 1500
spoke_count = 72
margin_px = 100
supersampling = 4

# Create the image at a higher resolution
large_size = image_size_px * supersampling
large_margin = margin_px * supersampling

y, x = np.indices((large_size, large_size))

center = (large_size - 1) / 2

# Coordinates measured from the image centre
x_relative = x - center
y_relative = y - center

# Angle of every pixel, from -pi to pi radians
angles = np.arctan2(y_relative, x_relative)

# Create alternating angular sections
star = (
    np.floor(
        (angles + np.pi) / (2 * np.pi) * spoke_count
    ) % 2
) * 255

# Limit the star to a circle
radius = np.sqrt(x_relative**2 + y_relative**2)
star_radius = large_size / 2 - large_margin

outside_circle = radius > star_radius
star[outside_circle] = 255

# Convert to an 8-bit image
star = star.astype(np.uint8)

# Downsample to the requested size for smoother edges
star = cv2.resize(
    star,
    (image_size_px, image_size_px),
    interpolation=cv2.INTER_AREA
)

# Save and display image
array_to_image(star, "siemens_star")