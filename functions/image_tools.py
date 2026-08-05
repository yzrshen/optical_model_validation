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

def detect_checker_board(gray_image, image_path, corner_columns, corner_rows):

    pattern_size = (corner_columns, corner_rows)

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
            f"Checkerboard was not detected"
        )
        raise SystemExit

    # Organize the detected corners by checkerboard row and column
    # Each corner stores its (x, y) pixel coordinates
    # corners[2, 4, 0] -> x coordinate
    # corners[2, 4, 1] -> y coordinate
    corners = corners.reshape(
        corner_rows,
        corner_columns,
        2
    )

    return corners

def find_edge_positions(image):
    """
        Purpose: Find positions of pixels along edge
        Parameter(s): Image array with defined edge
        Return(s): edge_positions
        
    """

    # Calculate horizontal brightness change.
    # axis=1 means calculate the change from left to right.
    row_gradients = np.gradient(image, axis=1)

    edge_positions = []

    # Run code once for every row in the crop
    # range(2, 6) = 2, 3, 4, 5
    for row_number in range(image.shape[0]):

        # Finds all absolute values for change in brightness for current row
        gradient_strength = np.abs(row_gradients[row_number])

        # Find the pixel with the strongest brightness change
        # argmax returns index with largest value
        peak_column = np.argmax(gradient_strength)

        # Examine 5 columns around the peak for a more accurate position
        start = max(0, peak_column - 2)
        #crop.shape[1] = number of columns (0-199)
        end = min(image.shape[1], peak_column + 3)

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

    return edge_positions

def fitted_edge_positions(image, edge_positions):
    # Creates a vertical coordinate for every row
    row_coordinates = np.arange(image.shape[0])

    # np.polyfit(x_data, y_data, degree)
    # outputs slope, intercept
    slope, intercept = np.polyfit(
        row_coordinates,
        edge_positions,
        1
    )

    # Converts noise from points into fitted coordinates
    fitted_edge_positions = slope * row_coordinates + intercept

    return fitted_edge_positions

