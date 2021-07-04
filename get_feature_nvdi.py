import requests
import json
import os
from satsearch import Search
import numpy as np
import cv2
from osgeo import gdal
import rasterio


# Get the described feature as the default, or whatever is passed as an arg
def get_geo_feature():

    geojson_feature = requests.get('https://gist.githubusercontent.com/rodrigoalmeida94/369280ddccf97763da54371199a9acea/raw/d18cd1e266023d08464e13bf0e239ee29175e592/doberitzer_heide.geojson')

    # Write the working json to a file, in case we want to reference it later
    file = open('geojson_tmp/workingfeature.json', "w")
    file.write(geojson_feature.text)
    file.close()

    return geojson_feature.json()


# Query STAC with our geofeature coords
def query_element84(api_endpoint, geofeature):
    search = Search(api_endpoint, intersects=geofeature, datetime='2021-06-01/2021-06-30', collections=['sentinel-s2-l2a-cogs'])
    return search

def calc_ndvi(nir, red, offset):
    return (nir - red) / (nir + red + offset)

#print(geojson_feature.json())
if __name__ == "__main__":

    stac_api_endpoint = "https://earth-search.aws.element84.com/v0"
    images_red = []
    images_nir = []


    geo_feature_coords = get_geo_feature()['features'][0]['geometry']

    #print(geo_feature['features'][0]['geometry'])

    results = query_element84(stac_api_endpoint, geo_feature_coords)

    for item in results.items():
        images_red.append(item.asset('red')['href'])
        images_nir.append(item.asset('nir')['href'])

    print(images_red)
    print(images_nir)

    for index, image in enumerate(images_red):
        with rasterio.open(image) as im_red:
            with rasterio.open(images_nir[index]) as im_nir:


                im_red_chunk = im_red.read()
                im_nir_chunk = im_nir.read()

                ndvi = calc_ndvi(im_nir_chunk, im_red_chunk, 0.001)
                #print(ndvi)
                mean_ndvi = ndvi.mean()
                print(mean_ndvi)
