from geopy import geocoders
import json
places = []
from login_credentials import BING_KEY
bing_key = ''

def encode_bing(origin_address,key):
	b = geocoders.Bing(key)
	try: 
		place, (lat, lng) = b.geocode(origin_address)
		if place.find(', PA ') != -1:
			places.append([place,lat,lng])
	except ValueError:
		for place, (lat, lng) in b.geocode(origin_address, exactly_one=False):
			if place.find(', PA ') != -1:
				places.append([place,lat,lng])
	except:
		return 'No results found using Bing.'
	return places

print encode_bing('	101 Main St. Hartford, CT',bing_key)

# def encode_google(origin_address):
# 	g = geocoders.Google()
# 	try: 
# 		place, (lat, lng) = g.geocode(origin_address)
# 		places.append([place,lat,lng])
# 	except ValueError:
# 		for place, (lat, lng) in g.geocode(origin_address, exactly_one=False):
# 			places.append([place,lat,lng])
# 	except:
# 		print 'No results found using Google.'
# 		return encode_geocoder_us(origin_address)
# 	return places
# 
# # def encode_yahoo(origin_address):
# # 	y = geocoders.Yahoo('WE NEED AN APP ID TO USE YAHOO')
# # 	try: 
# # 		place, (lat, lng) = y.geocode(origin_address)
# # 		places.append([place,lat,lng])
# # 	except ValueError:
# # 		for place, (lat, lng) in y.geocode(origin_address, exactly_one=False):
# # 			places.append([place,lat,lng])
# # 	except:
# # 		print 'No results found using Yahoo.'
# # 		return 0;
# # 	return places
# 
# def encode_geocoder_us(origin_address):
# 	us = geocoders.GeocoderDotUS()
# 	try: 
# 		place, (lat, lng) = us.geocode(origin_address)
# 		places.append([place,lat,lng])
# 	except TypeError:
# 		return 'No results found using geocoder.us'
# 		# When we get a Yahoo! Application ID
# 		# print 'No results found using geocoder.us'
# 		# 		return encode_yahoo(origin_address)
# 	# except HTTPError:
# 	# 	return 'service unavailable'
# 	except ValueError:
# 		for place, (lat, lng) in us.geocode(origin_address, exactly_one=False):
# 			places.append([place,lat,lng])
# 	return places
# 	
# print encode_geocoder_us('109 S. 13th St. Philly PA')
# print encode_google('109 S. 13th St. Philly PA')