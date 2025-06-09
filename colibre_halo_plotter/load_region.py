#!/bin/env python

import numpy as np
import swiftsimio as sw
import swiftsimio.objects


def load_region(filename, centre, radius):
    """
    Open a region in a snapshot using swiftsimio

    filename: name of the snapshot to read
    centre: coordinates of the centre of the region
    radius: radius to read in about the centre

    Inputs are assumed to be comoving simulation units if not specified.
    """

    # Create the mask
    mask = sw.mask(filename)

    # Determine length units
    length_unit = mask.metadata.boxsize.units

    # Get centre and radius with units, assuming sim units if not unyt arrays
    centre = np.asanyarray(centre)
    if not hasattr(centre, "units"):
        centre *= length_unit
    radius = np.asanyarray(radius)
    if not hasattr(radius, "units"):
        radius *= length_unit

    # Ensure centre and radius are cosmo arrays
    cf = mask.metadata.boxsize.cosmo_factor
    if not isinstance(centre, sw.cosmo_array):
        centre = sw.cosmo_array(centre, units=centre.units, cosmo_factor=cf, comoving=True)
    if not isinstance(radius, sw.cosmo_array):
        radius = sw.cosmo_array(radius, units=radius.units, cosmo_factor=cf, comoving=True)

    # Compute bounding box
    bbox = [[c-radius, c+radius] for c in centre]
    mask.constrain_spatial(bbox)

    # Return the swiftsimio snapshot object
    return sw.load(filename, mask)
