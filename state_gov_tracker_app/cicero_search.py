## Functions to login to cicero
## Identify state representatives by address using cicero

from login_credentials import *
import urllib,httplib2, mimetypes,os,sys,re,random,string

####SETTINGS####
http = httplib2.Http()
url_base = 'http://cicero.azavea.com/v3.1'

import json


def search(request, upper_or_lower):
    if 'q' in request.GET:
        loc = request.GET['q'].replace(' ', '+')
    else:
        loc = '1+Penn+Square+Philadelphia+PA+19107'
    json_response = login(cicero_user, cicero_password)
    token = json_response['token']
    uid = str(json_response['user'])
    official_response = get_officials(loc, uid, token, upper_or_lower)
    official_dict = json.loads(official_response)
    for x in range(1):
        return official_info(official_dict, x)


def get_officials(loc, uid, token, upper_or_lower):
    url = '/official?user=' + uid + '&token=' + token + '&search_loc=' + loc + '&search_country=US&valid_on_or_before=2012-11-01&district_type=STATE_' + upper_or_lower
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    response, content = http.request(url_base + url, 'GET', headers=headers)
    return content


def login(username, password):
    url = '/token/new.json'
    body = {'username': username, 'password': password}
    print url_base + url + '\n'
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    response, content = http.request(url_base + url, 'POST', headers=headers, body=urllib.urlencode(body))
    #print str(response) + '\n'
    content_dict = json.loads(content)
    return content_dict


def official_info(official_dict, x):
    results = {}
    results['district_id'] = official_dict['response']['results']['candidates'][0]['officials'][x]['office']['district']['district_id']
    results['chamber'] = official_dict['response']['results']['candidates'][0]['officials'][x]['office']['chamber']['name']
    results['first_name'] = official_dict['response']['results']['candidates'][0]['officials'][x]['first_name']
    results['last_name'] = official_dict['response']['results']['candidates'][0]['officials'][x]['last_name']
    results['address'] = str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['address_1']) + ' ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['address_2']) + ' ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['city']) + ', ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['state']) + ' ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['postal_code'])
    results['phone'] = str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['phone_1'])
    return results
