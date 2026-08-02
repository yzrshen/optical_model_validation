import numpy as np
import cv2

square_count = 10
square_size_px = 50

small_checker = np.indices(
# Makes 2 arrays of row indices and column indices
# with shape (2, square_count, square_count)
(square_count, square_count)
# Adds 2 coordinate arrays together position by position
# and take remainders after division by 2
# Multiply by 255
# Creates array with alternating 0s and 255s
).sum(axis=0) % 2 * 255

# Stretch out array to pixels per square
checker_block_vert = np.repeat(small_checker, square_size_px, axis=0)
checker_block = np.repeat(checker_block_vert, square_size_px, axis=1)

# Add white margin to be processed by findChessboardCornersSB
checker_block = np.pad(
    checker_block,
    pad_width = 100,
    mode="constant",
    constant_values=255
)

# Store each pixel in 8-bit format, as expected by cv2
checker_block = checker_block.astype(np.uint8)
# Save array as image file
cv2.imwrite("targets/checkerboard.png", checker_block)
# Show image
cv2.imshow("Checkerboard", checker_block)
# Show indefinitely until key is pressed (0 = no time limit)
cv2.waitKey(0)
cv2.destroyAllWindows()