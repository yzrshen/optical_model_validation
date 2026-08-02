import numpy as np
import cv2

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