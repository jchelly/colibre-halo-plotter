# Scripts for plotting HBT-HERONS halos in COLIBRE

This module selects the most massive N HBT halos in a COLIBRE snapshot and
makes images of them. As input it requires one or more HBT outputs and
corresponding SWIFT virtual snapshots with halo membership information.

The output is a large collection of image files and a html page to view them.

## Configuration

The runs to plot are defined in a yaml config file. See
`examples/L012_m6/config.yml` for an example.

## Extracting positions of the halos to plot

We use the HBT catalogue from one run to identify a sample of halos to plot:
```
python3 -m colibre_halo_plotter.identify_massive ./config.yml
```
This writes a text file with the halo coordinates

## Plotting a halo

