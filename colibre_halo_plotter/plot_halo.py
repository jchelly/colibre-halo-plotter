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
import yaml
import swiftsimio as sw

from colibre_halo_plotter.load_region import load_region
from colibre_halo_plotter.smooth_particles import smooth_particles


def plot_halo(snap_nr, read_radius, halo_file, snap_file, ptype, index, image_dir, branch, scaling):
    """
    Plot a halo from a HBT run
    """

    # Read coordinates of halos of interest
    massive_positions = np.loadtxt(halo_file, dtype=float, delimiter=",")

    plt.rc('xtick', labelsize=6)
    plt.rc('ytick', labelsize=6)

    j = index

    # Read particles near this halo
    snap = load_region(snap_file, massive_positions[j,:], read_radius)
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
    plot_radius = read_radius
    region = [centre[0]-plot_radius, centre[0]+plot_radius,
              centre[1]-plot_radius, centre[1]+plot_radius,
              centre[2]-plot_radius, centre[2]+plot_radius]
    region = [sw.cosmo_array(r, units=part_pos.units, cosmo_factor=part_pos.cosmo_factor, comoving=True) for r in region]

    # vmin and vmax values for imshow log normalisation
    vmin = scaling[ptype]["vmin"]
    vmax = scaling[ptype]["vmax"]

    # Centre for periodic wrap
    periodic_centre = massive_positions[j,:]*snap.metadata.boxsize.units

    for plot_name, to_plot in (("central",    in_halo),
                               ("satellites", in_subhalo),
                               ("fof",        in_fof)):

        plt.figure(figsize=(8,8))

        # Make a plot of the particles in this halo
        _, img, aximg = smooth_particles(part_pos[to_plot,:], part_mass[to_plot], snap.metadata.boxsize, 512,
                                         region=region, cmap="plasma", norm=LogNorm(vmin=vmin, vmax=vmax, clip=True))
        plt.gca().set_aspect("equal")

        plt.suptitle(f"Halo {index}, snap {snap_nr}, {branch} : {ptype}, {plot_name}")
        image_filename = f"{image_dir}/{plot_name}_{ptype}_{snap_nr:04d}_halo_{index}.png"
        os.makedirs(os.path.dirname(image_filename), exist_ok=True)
        plt.savefig(image_filename)
        plt.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Plot HBT-HERONS halos in a COLIBRE simulation")
    parser.add_argument("config_file", type=str, help="Location of the yaml config file")
    parser.add_argument("first_index", type=int, help="Index of first halo to plot")
    parser.add_argument("last_index", type=int, help="Index of last halo to plot")
    args = parser.parse_args()

    # Read the config
    with open(args.config_file, "r") as f:
        config = yaml.safe_load(f)

    snap_nr = int(config["snap_nr"])
    halo_file = f"{config['out_dir']}/massive_halos_{snap_nr:03d}.txt"
    read_radius = float(config["read_radius"])
    scaling = config["scaling"]

    # Loop over branches to plot
    for branch in config["branches"]:

        # Virtual snapshot location for this HBT branch
        snap_file = config["branches"][branch]["virtual_snaps"].format(snap_nr=snap_nr)

        # Output image directory for this branch
        image_dir = f"{config['out_dir']}/{branch}"

        # Make the images
        for index in range(args.first_index, args.last_index+1):
            for ptype in config["ptypes"]:
                print(f"Image for branch {branch}, {ptype}, halo index {index}")
                plot_halo(snap_nr, read_radius, halo_file, snap_file, ptype, index, image_dir, branch, scaling)

    print("Done.")
