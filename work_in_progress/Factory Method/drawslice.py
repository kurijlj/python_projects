import math
import numpy as np
import matplotlib.pyplot as plt
from skimage.draw import disk, ellipse

# matplotlib.use('qtagg')

def draw_slice(pixel_spacing_r, pixel_spacing_c):
    # Calculate the slice extents (in pixels) to hold the phantom image. The
    # phantom dimsnions are 200 mm x 160 mm (AP-PA, LL). So we need to calculate
    # the optimal extents of the image given in pixels.
    phantom_width  = int(160.0 / pixel_spacing_r)
    phantom_height = int(200.0 / pixel_spacing_c)
    slice_width    = int(200.0 / pixel_spacing_r)
    slice_height   = int(160.0 / pixel_spacing_c)
    slice_extent   = max(slice_width, slice_height)
    if 256 < slice_extent:
        slice_extent = 512
    elif 128 < slice_extent:
        slice_extent = 256
    else:
        slice_extent = 128

    pixel_data = np.zeros((slice_extent, slice_extent), dtype=np.uint16)

    # Draw the outer phantom contour
    rr, cc = ellipse(
                     slice_extent / 2,
                     slice_extent / 2,
                     phantom_height / 2,
                     phantom_width / 2,
                     shape=pixel_data.shape
                    )
    pixel_data[rr, cc] = 30000

    plt.imshow(pixel_data, cmap=plt.cm.gray)
    plt.show()

if __name__ == '__main__':
    draw_slice(0.5, 0.5)