import requests
import json
import os
import sys
from satsearch import Search
import numpy as np
import cv2
from osgeo import gdal
import rasterio, rasterio.mask


# Get the described feature as the default, or whatever is passed as an arg
def get_geo_feature(feature_url):

    if type(feature_url) not in [str]:
        raise TypeError('The feature URL passed as a command-line arg must be a string')

    try:
        geojson_feature = requests.get(feature_url)
    except:
        print("Invalid geofeature URL")
        sys.exit(1)

    # Write the working json to a file, in case we want to reference it later
    file = open('geojson_tmp/workingfeature.json', "w")
    file.write(geojson_feature.text)
    file.close()

    if type(geojson_feature) not in [dict]:
        raise TypeError('Did not get a proper response for feature URL')

    return geojson_feature.json()


# Query STAC with our geofeature coords
def query_element84(api_endpoint, geofeature, max_cloud_cover):
    search = Search(api_endpoint, intersects=geofeature, datetime='2021-01-01/2021-06-30', collections=['sentinel-s2-l2a-cogs'], query={'eo:cloud_cover': {'lte': max_cloud_cover}})
    
    # quick debug code to see cloud cover from images
    items = search.items()
    print(items.summary(['date', 'id', 'eo:cloud_cover']))


    return search

# Function to calculate NDVI - possible that it needs tweaks to accommodate the data?
def calc_ndvi(nir, red, offset):

    return (nir - red) / (nir + red + offset)

#####################################################################################

if __name__ == "__main__":

    stac_api_endpoint = "https://earth-search.aws.element84.com/v0"
    images_red = []
    images_nir = []

    # List where we can keep ndvi means as we calculate them per chunk
    per_chunk_ndvi_means = []

    # feature_url defaults to our Github Gist path, if no argument is given
    feature_url = sys.argv[1] if len(sys.argv) > 1 else 'https://gist.githubusercontent.com/rodrigoalmeida94/369280ddccf97763da54371199a9acea/raw/d18cd1e266023d08464e13bf0e239ee29175e592/doberitzer_heide.geojson'
    geo_feature_coords = get_geo_feature(feature_url)['features'][0]['geometry']


    results = query_element84(stac_api_endpoint, geo_feature_coords, 0)
    
    image_gridsquares = set()
    latest_images = []


    # iterate through all our images and only include the latest of each id
    for item in results.items():
        # Make a string that represents this image's unique location so we can hash it into our set
        gridsquare = str(item.properties['sentinel:utm_zone']) + str(item.properties['sentinel:latitude_band']) + str(item.properties['sentinel:grid_square'])

        # Check the set and add to latest_images if not already in the set, and since results are returned in descending order from latest we'll have the latest of each
        if gridsquare not in image_gridsquares:
            image_gridsquares.add(gridsquare)
            latest_images.append(item)
            print(image_gridsquares)

    # Make lists of image refs for both red and NIR image sets, matched by index
    for item in latest_images:
        images_red.append(item.asset('red')['href'])
        images_nir.append(item.asset('nir')['href'])

    # iterate over one set, opening the matching image in sync
    for index, image in enumerate(images_red):
        with rasterio.open(image) as im_red:
            with rasterio.open(images_nir[index]) as im_nir:


                # select the second-largest resolution, this could be changed via an argument but performance seems good where it's at
                overviews = im_red.overviews(1)
                overview_selected = overviews[1]

                print(geo_feature_coords)


                im_red_chunk = im_red.read(out_shape=(1, int(im_red.height // overview_selected), int(im_red.width // overview_selected))).clip(0)
                im_nir_chunk = im_nir.read(out_shape=(1, int(im_nir.height // overview_selected), int(im_nir.width // overview_selected))).clip(0)

                # Mask chunks based on original geofeature coords

                #im_red_masked = rasterio.mask.mask(im_red_chunk, [geo_feature_coords], nodata=0)

                ndvi = calc_ndvi(im_nir_chunk, im_red_chunk, 0.000001)
                mean_ndvi = ndvi.mean()
                print(f"Image set {index} - mean NDVI: {mean_ndvi}")
                per_chunk_ndvi_means.append(mean_ndvi)

    area_ndvi_mean = sum(per_chunk_ndvi_means) / len(per_chunk_ndvi_means)

    print(f"The mean NDVI for the given area is {area_ndvi_mean}")
