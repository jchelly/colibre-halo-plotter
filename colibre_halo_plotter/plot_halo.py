#!/bin/env python
#
# Identify most massive subhalo in a HBT output
#
import matplotlib
matplotlib.use("Agg")

import sys
import os.path
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import h5py
import unyt


def plot_massive(snap_nr, output_dir, ptype, index):
    """
    Plot most massive main halos in several HBT runs on the same snapshot
    """

    read_radius = 6.0

    # Read coordinates of halos of interest
    massive_positions = np.loadtxt(f"{output_dir}/../massive_halos_{snap_nr:04d}.txt", dtype=float, delimiter=",")

    plt.rc('xtick', labelsize=6)
    plt.rc('ytick', labelsize=6)

    j = index

    # Read particles near this halo
    filename = f"{output_dir}/virtual_snapshots/colibre_{snap_nr:04d}.hdf5"
    snap = ssio.load_region(filename, massive_positions[j,:], read_radius)
    data = getattr(snap, ptype)
    part_groupnr = data.group_nr_bound.value
    part_pos = data.coordinates % snap.metadata.boxsize[0]
    part_mass = data.masses
    part_fof = data.fofgroup_ids.value

    # Find GroupNr_bound of particles near the centre
    centre = massive_positions[j,:]
    radius = np.linalg.norm(part_pos.value - centre[None,:], axis=1)
    centre_groupnr = part_groupnr[radius<0.1]

    # Find the most common GroupNr_bound near the centre
    unique_groupnr, unique_count = np.unique(centre_groupnr, return_counts=True)
    imax = np.argmax(unique_count)
    central_groupnr = unique_groupnr[imax]
    in_halo = part_groupnr == central_groupnr
    print("Particles in central = ", sum(in_halo))

    # Find FoF index of the same particles
    fof_id = np.amin(part_fof[in_halo])
    print("FOFGroupID = ", fof_id)

    # Identify bound non-central subhalos in the FoF group
    in_subhalo = (part_fof==fof_id) & (part_groupnr != central_groupnr) & (part_groupnr >= 0)
    print("Particles in satellites = ", sum(in_subhalo))

    # Identify all particles in the FoF
    in_fof = (part_fof==fof_id)
    print("Particles in FoF = ", sum(in_fof))

    # Decide region to plot
    plot_radius = 1.0
    region = [centre[0]-plot_radius, centre[0]+plot_radius,
              centre[1]-plot_radius, centre[1]+plot_radius,
              centre[2]-plot_radius, centre[2]+plot_radius]
    region = [r*part_pos.units for r in region]

    # vmin and vmax values for imshow log normalisation
    scaling = {
        "dark_matter" : (1e2, 1e7),
        "stars"       : (1e-2, 1e5),
        "gas"         : (1e1, 1e7),
    }
    vmin, vmax = scaling[ptype]

    # Centre for periodic wrap
    periodic_centre = massive_positions[j,:]*snap.metadata.boxsize.units

    for plot_name, to_plot in (("central",    in_halo),
                               ("satellites", in_subhalo),
                               ("fof",        in_fof)):

        plt.figure(figsize=(8,8))

        # Make a plot of the particles in this halo
        print(region)
        _, img, aximg = ssio.smooth_particles(part_pos[to_plot,:], part_mass[to_plot], snap.metadata.boxsize, 512,
                                              region=region, cmap="plasma", norm=LogNorm(vmin=vmin, vmax=vmax, clip=True))
        #print("vmin = ", np.amin(img[img>0]))
        #print("vmax = ", np.amax(img[img>0]))

        plt.gca().set_aspect("equal")

        branch = os.path.basename(output_dir)
        plt.suptitle(f"Halo {index}, snap {snap_nr}, {branch} : {ptype}, {plot_name}")
        image_filename = f"{output_dir}/images/{plot_name}_{ptype}_{snap_nr:04d}_halo_{index}.png"
        os.makedirs(os.path.dirname(image_filename), exist_ok=True)
        plt.savefig(image_filename)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Plot HBT-HERONS halos in a COLIBRE simulation")
    parser.add_argument("snap_nr", type=int, help="Which snapshot to do")
    parser.add_argument("output_dir", type=str, help="Where to write the output")
    parser.add_argument("index", type=int, help="Index of halo to plot")
    parser.add_argument("ptype", type=str, help="Particle type to show")
    args = parser.parse_args()

    plot_massive(args.snap_nr, args.output_dir, args.ptype, args.index)
