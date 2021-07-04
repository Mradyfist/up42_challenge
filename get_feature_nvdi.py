import requests
import json
import os


# Get the described feature as the default, or whatever is passed as an arg
def get_geo_feature():
    geojson_feature = requests.get('https://gist.githubusercontent.com/rodrigoalmeida94/369280ddccf97763da54371199a9acea/raw/d18cd1e266023d08464e13bf0e239ee29175e592/doberitzer_heide.geojson')
    file = open('geojson_tmp/workingfeature.json', "w")
    file.write(geojson_feature.text)
    file.close()

    return geojson_feature.json()

#def query_element84():


#print(geojson_feature.json())
if __name__ == "__main__":
    geo_feature = get_geo_feature()