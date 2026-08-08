import numpy as np
import cv2
import math

def array_to_image(array, image_name):

    # Save array as image file
    saved = cv2.imwrite(f"targets/{image_name}.png", array)
    if not saved:
        raise SystemExit("Image could not be saved")
    
    # Show image
    cv2.imshow("image", array)

    # Show indefinitely until key is pressed (0 = no time limit)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

image_width = 2500
image_height = 2500
slant_angle = math.radians(5)
margin = 80

x_center = (image_width - 1) / 2
y_center = (image_height - 1) / 2

# Blank image of given dimensions
image = np.zeros((image_height, image_width))

# Create slanted edge
for row in range(image_height):
    x_edge = round(x_center + (row - y_center) * math.tan(slant_angle))
    image[row, :x_edge] = 255

# Store each pixel in 8-bit format, as expected by cv2
image = image.astype(np.uint8)

# Convert to BGR 
image = cv2.cvtColor(
    image,
    cv2.COLOR_GRAY2BGR
)

# Add green border
image = cv2.copyMakeBorder(
    image,
    margin, margin, margin, margin,
    cv2.BORDER_CONSTANT,
    value=(0, 255, 0)
)

# Save and display image
array_to_image(image, "slanted_edge")
