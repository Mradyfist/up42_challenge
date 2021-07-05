# NDVI Geofeature Lookup

This script will accept a URL to a geojson file, and using that file as a shape it will search the Element84 STAC catalog for Sentinel 2 scenes that intersect. It then filters the list of intersecting scenes to find only ones that have 0% cloud cover (as reported in metadata), and picks the latest of each by date.

Scenes are then compared to find the mean NDVI as calculated by comparing NIR and red channels, but without downloading the images themselves; instead, they're left on the AWS Open Data Registry and per-pixel comparisons are done by pulling a pixel at a time via the cloud-optimized GeoTIFF format.

# Installation

NDVI Geofeature lookup requires the following dependencies:
requests
sat-search
numpy
cv2
gdal
rasterio

All of these can be installed via pip with the exception of gdal and rasterio (on Windows), where you'll need to pull wheel binaries that are already compiled.
