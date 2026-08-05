import cv2
import math
import numpy as np

def image_sharpness(gray_image):
    """
    Purpose: Find sharpness value of given image using Laplacian Variance
    Parameter(s): grayscaled image array
    Return(s): Sharpness value
    
    """
    smoothed_image = cv2.GaussianBlur(gray_image, (3, 3), 0)

    laplacian_image = cv2.Laplacian(
    smoothed_image,
    cv2.CV_64F,
    ksize = 1
    )

    sharpness = laplacian_image.var()

    return sharpness

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

def find_fov(coverage, object_distance):

    fov_deg = math.degrees(
            2 * math.atan(
                coverage
                / (2 * object_distance)
            )
        )
    return fov_deg

def find_efl(magnification, object_distance):

    efl = (
            magnification
            * object_distance
            / (1 + magnification)
        )
    return efl

def bin_esf(distances, intensities, oversampling=4):
    """
    Group pixels by their perpendicular distance from an edge and
    calculate the average intensity in each group.

    Parameters
    ----------
    distances : numpy.ndarray
        Flattened perpendicular distance of every pixel from the edge.

    intensities : numpy.ndarray
        Flattened intensity of every pixel.

    oversampling : int
        Number of ESF samples per pixel. For example, 4 produces
        bins that are 0.25 pixels wide.

    Returns
    -------
    esf_distance : numpy.ndarray
        Distance of each ESF sample from the fitted edge.

    esf : numpy.ndarray
        Average pixel intensity at each distance.
    """

    # Each bin's width in pixels
    bin_width = 1.0 / oversampling

    minimum_distance = distances.min()
    maximum_distance = distances.max()

    # Create the boundaries of the distance bins
    bin_edges = np.arange(
        minimum_distance,
        maximum_distance + bin_width,
        bin_width
    )

    # Determine which bin contains each pixel
    bin_numbers = np.digitize(distances, bin_edges) - 1

    number_of_bins = len(bin_edges) - 1

    # Initially mark every ESF bin as empty
    esf = np.full(number_of_bins, np.nan)

    # Calculate the average intensity inside each bin
    for bin_number in range(number_of_bins):
        pixels_in_bin = intensities[
            bin_numbers == bin_number
        ]

        if len(pixels_in_bin) > 0:
            esf[bin_number] = np.mean(pixels_in_bin)

    # Calculate the centre distance of every bin
    esf_distance = (
        bin_edges[:-1] + bin_edges[1:]
    ) / 2

    # Interpolate any empty bins
    valid_bins = ~np.isnan(esf)

    esf = np.interp(
        esf_distance,
        esf_distance[valid_bins],
        esf[valid_bins]
    )

    return esf_distance, esf

def find_mtf(lsf, bin_width):

    # Apply Hamming window
    window = np.hamming(len(lsf))
    windowed_lsf = lsf * window

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

    return mtf, frequencies_cpp