#!/bin/env python

import unyt
import swiftsimio as sw
import numpy as np
import matplotlib.pyplot as plt


def smooth_particles(pos, mass, boxsize, resolution, x_axis=0, y_axis=1,
                     region=None, display=True, periodic_wrap=True, **kwargs):
    """
    Make a smoothed plot of the supplied particles projected along the
    specified axis.

    pos[N,3] : positions of the particles
    mass[n]  : masses of the particles
    resolution : horizontal resolution of the image to make
    x_axis : axis to use as x direction
    y_axis : axis to use as y direction
    region[6]: (xmin, xmax, ymin, ymax, zmin, zmax) volume to plot
    display: whether we should actually imshow() the image
    periodic_wrap: wrap coordinates to periodic copy closest to region

    Returns:

    displayed_region: (xmin, xmax, ymin, ymax) extent of the image
    image: 2D float array with the image data
    aximg: matplotlib AxesImage object, or None if display=False

    Any extra named args are passed to the imshow call.
    """

    from swiftsimio.visualisation.smoothing_length import generate_smoothing_lengths
    from swiftsimio.visualisation.projection_backends.fast import scatter

    # Compute smoothing lengths for the particles
    pos = pos % boxsize # Wrap all particles into the box
    smoothing_length = generate_smoothing_lengths(pos, boxsize=boxsize,
                                                  kernel_gamma=1.8,
                                                  neighbours=57, speedup_fac=2,
                                                  dimension=3)
    # Ensure region is a cosmo_array (and not a list)
    if region is not None:
        region_ca = np.empty_like(pos, shape=(6,))
        for i in range(6):
            region_ca[i] = region[i]
        region = region_ca

    # Do periodic wrap if necessary
    if periodic_wrap and (region is not None):
        centre = 0.5*(region[0::2]+region[1::2])
        offset = centre - 0.5*boxsize
        pos = ((pos - offset[None,:]) % boxsize) + offset

    # Determine range of coordinates to plot if not specified
    if region is None:
        x_min = pos[:,x_axis].min()
        x_max = pos[:,x_axis].max()
        y_min = pos[:,y_axis].min()
        y_max = pos[:,y_axis].max()
    else:
        x_min, x_max = region[2*x_axis+0], region[2*x_axis+1]
        y_min, y_max = region[2*y_axis+0], region[2*y_axis+1]

    # Determine size of square region that covers the requested area
    dx = x_max - x_min
    dy = y_max - y_min
    size = max(dx,dy)
    square_region = [x_min, x_min+size, y_min, y_min+size]

    # Get scaled coordinates and smoothing lengths
    x = (pos[:,x_axis] - x_min) / size
    y = (pos[:,y_axis] - y_min) / size
    smoothing_length /= size

    # Make the image
    image = scatter(x=x, y=y, h=smoothing_length, m=mass, res=resolution)

    # Determine number of pixels to keep and trim the image
    pixels_x = int(min(resolution, np.ceil(resolution * float(dx/size))))
    pixels_y = int(min(resolution, np.ceil(resolution * float(dy/size))))
    image = image[:pixels_x,:pixels_y]

    # Compute the corresponding region
    displayed_region = [x_min, x_min + (size/resolution)*pixels_x,
                        y_min, y_min + (size/resolution)*pixels_y]

    # Construct args for imshow
    args = {}
    for name in kwargs:
        args[name] = kwargs[name]
    if "norm" not in args:
        from matplotlib.colors import LogNorm
        args["norm"] = LogNorm()
    if "origin" not in args:
        args["origin"] = "lower"

    # Display the image at the required coordinates
    if display:
        aximg = plt.imshow(image.T, extent=np.asarray(displayed_region), **args)
    else:
        aximg = None

    return displayed_region, image, aximg
