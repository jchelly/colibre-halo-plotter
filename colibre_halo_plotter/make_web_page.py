#!/bin/env python

import os
import yaml
import argparse
import importlib.resources
import shutil
import json

def make_web_page(config):

    # Determine output directory
    dest_dir = config["out_dir"]

    # Copy html and javascript source
    for filename in ("index.html", "main.js"):
        infile = importlib.resources.files("colibre_halo_plotter.data").joinpath(filename)
        shutil.copyfile(infile, dest_dir+"/"+filename)

    # Make a json file with parameters needed to display the images
    with open(dest_dir+"/params.json","w") as param_file:
        json.dump(config, param_file, indent=4)


if __name__ == "__main__":

    # Get command line params
    parser = argparse.ArgumentParser(description="Make web page with COLIBRE halo plots")
    parser.add_argument("config_file", type=str, help="Location of the yaml config file")
    args = parser.parse_args()

    # Read the config
    with open(args.config_file, "r") as f:
        config = yaml.safe_load(f)

    make_web_page(config)
