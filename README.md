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

To plot the first halo from the list of most massive halos:
```
python3 -m colibre_halo_plotter.plot_halo ./config.yml 0 0
```
This writes image files to the directory specified in the config file. The
two integer parameters are the indexes of the first and last halos to plot.
To do the first ten halos:
```
python3 -m colibre_halo_plotter.plot_halo ./config.yml 0 9
```

## Making a web page

Once all of the halos has been plotted, the module can make a directory of
images with html and javascript to display them:
```
python3 -m colibre_halo_plotter.make_web_page ./config.yml
```
