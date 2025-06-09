#!/bin/env python
#
# Identify most massive subhalo in a HBT output
#

import os
import sys
import argparse
import numpy as np
import h5py
import yaml


def identify_massive(hbtdir, snap_nr, output_filename, nmax):
    """
    Find the most massive subhalos
    """

    # Read the halo catalogue
    print("Reading halos")
    subhalos = []
    filenames = "{hbtdir}/{snap_nr:03d}/SubSnap_{snap_nr:03d}.{file_nr}.hdf5"
    file_nr = 0
    nr_files = 1
    while file_nr < nr_files:
        filename = filenames.format(snap_nr=snap_nr, file_nr=file_nr, hbtdir=hbtdir)
        with h5py.File(filename, "r") as hbt:
            subhalos.append(hbt["Subhalos"][...])
            nr_files = int(hbt["NumberOfFiles"][0])
        print(f"File {file_nr} of {nr_files}")
        file_nr += 1
    subhalos = np.concatenate(subhalos)

    # Find order by mass
    print("Sorting halos")
    order = np.argsort(-subhalos["Mbound"])

    # Store location of the most massive objects
    massive_pos = np.ndarray((nmax,3), dtype=float)
    n = 0
    for i in order:
        if subhalos[i]["Rank"] == 0:
            massive_pos[n,:] = subhalos["ComovingMostBoundPosition"][i,:]
            n += 1
        if n >= nmax:
            break

    # Write out results
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "w") as outfile:
        for i in range(nmax):
            print(f"{massive_pos[i,0]:.4f}, {massive_pos[i,1]:.4f}, {massive_pos[i,2]:.4f}", file=outfile)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Find massive HBT-HERONS halos in a COLIBRE simulation")
    parser.add_argument("config_file", type=str, help="Location of the yaml config file")
    args = parser.parse_args()

    # Read the config
    with open(args.config_file, "r") as f:
        config = yaml.safe_load(f)

    # Use the first HBT branch to locate the halos
    first_branch = list(config["branches"].keys())[0]
    hbt_dir = config["branches"][first_branch]["hbt_dir"]

    # Snapshot number we're using
    snap_nr = int(config["snap_nr"])
    print(f"Reading halo positions for snapshot {snap_nr} from {hbt_dir}")

    # Number of halos to plot
    nmax = int(config["nr_halos"])
    print(f"Will locate {nmax} most massive halos")

    # Where to write the output catalogue
    out_dir = config["out_dir"]
    filename = f"{out_dir}/massive_halos_{snap_nr:03d}.txt"

    identify_massive(hbt_dir, snap_nr, filename, nmax)
    print(f"Wrote file: {filename}")
