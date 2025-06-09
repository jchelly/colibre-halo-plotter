#!/bin/env python
#
# Identify most massive subhalo in a HBT output
#

import os
import sys
import argparse
import numpy as np
import h5py


def identify_massive(hbtdir, snap_nr, output_dir):
    """
    Find the most massive subhalos
    """

    nmax = 120

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
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/massive_halos_{snap_nr:04d}.txt", "w") as outfile:
        for i in range(nmax):
            print(f"{massive_pos[i,0]:.4f}, {massive_pos[i,1]:.4f}, {massive_pos[i,2]:.4f}", file=outfile)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Find massive HBT-HERONS halos in a COLIBRE simulation")
    parser.add_argument("hbtdir", type=str, help="Location of the HBT output")
    parser.add_argument("snap_nr", type=int, help="Which snapshot to do")
    parser.add_argument("output_dir", type=str, help="Where to write the output")
    args = parser.parse_args()

    identify_massive(**vars(args))
