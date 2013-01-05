from geopy import geocoders
import json
places = []
from login_credentials import BING_KEY
bing_key = BING_KEY


def encode_bing(origin_address, key):
    b = geocoders.Bing(key)
    try:
        place, (lat, lng) = b.geocode(origin_address)
        if place.find(', PA ') != -1:
            places.append([place, lat, lng])
    except ValueError:
        for place, (lat, lng) in b.geocode(origin_address, exactly_one=False):
            if place.find(', PA ') != -1:
                places.append([place, lat, lng])
    except:
        return 'No results found using Bing.'
    return places

print encode_bing('101 Main St. Hartford, CT', bing_key)
