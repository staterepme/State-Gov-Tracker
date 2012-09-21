from django.http import HttpResponse
import datetime
import urllib,httplib2, mimetypes,os,sys,re,random,string
from django.shortcuts import render_to_response
from subprocess import call
try:
	import json
except ImportError:
	import simplejson as json

def MyRep(request):
	rep_result = search(request)
	return HttpResponse(rep_result)

def main2():
	z = '755+N.+26th+St.+Philadelphia+PA'
	request = search(z)

def search(request):
	if 'q' in request.GET:
		loc = request.GET['q'].replace(' ','+')
	else:
		loc = '755+N.+26th+St.+Philadelphia+PA'
	json_response = login('christophernies@gmail.com', 'Congress1!')
	token = json_response['token']
	uid = str(json_response['user'])
	official_response = get_official(loc, uid, token)
	official_dict = json.loads(official_response)
	for x in range(1):
		return official_info(official_dict, x)


def search_form(request):
    return render_to_response('search_form.html')

def link(text, url):
	return '<a href=\"' + url + '\">' + text + '</a>'

####SETTINGS####
http = httplib2.Http()
url_base = 'http://cicero.azavea.com/v3.1'
users = {'christophernies@gmail.com':'Congress1!'}
fb_app_id = '503590929669292'
fb_app_secret = '9b3287b8287efbd4b18150173a9188d4'


def encode_multipart (file_path, fields):
        BOUNDARY = '----------boundary------'
        CRLF = '\r\n'
        body = []
        # Add the metadata about the upload first
        for key in fields:
            body.extend(
              ['--' + BOUNDARY,
               'Content-Disposition: form-data; name="%s"' % key,
               '',
               fields[key],
               ])
        # Now add the file itself
        file_name = os.path.basename(file_path)
        f = open(file_path, 'rb')
        file_content = f.read()
        f.close()
        body.extend(
          ['--' + BOUNDARY,
           'Content-Disposition: form-data; name="file"; filename="%s"'
           % file_name,
           # The upload server determines the mime-type, no need to set it.
           'Content-Type: application/octet-stream',
           '',
           file_content,
           ])
        # Finalize the form body
        body.extend(['--' + BOUNDARY + '--', ''])
        return 'multipart/form-data; boundary=%s' % BOUNDARY, CRLF.join(body)


def login(username, password):
	url = '/token/new.json'
	body = {'username': username, 'password': password}
	print url_base+url + '\n'
	headers = {'Content-type': 'application/x-www-form-urlencoded'}
	response, content = http.request(url_base+url, 'POST', headers=headers, body=urllib.urlencode(body))
	#print str(response) + '\n'
	content_dict = json.loads(content)
	return content_dict

def get_official(loc, uid, token):
	content = {}
#	url = '/official?user=' + uid + '&token=' + token + '&search_loc=' + loc + '&search_country=US&state=PA&district_type=STATE_UPPER'
	url = '/official?user=' + uid + '&token=' + token + '&search_loc=' + loc + '&search_country=US&district_type=STATE_UPPER'
#	print url_base+url
	headers = {'Content-type': 'application/x-www-form-urlencoded'}
	response, content = http.request(url_base+url, 'GET', headers=headers)
#	print response
#	print str(content) + '\n'
	return content

def official_info(official_dict, x):
#	return 'Your representative is: ' + str(official_dict['response'])
	return 'Your representative is: ' + official_dict['response']['results']['candidates'][0]['officials'][x]['first_name'] + ' ' + official_dict['response']['results']['candidates'][0]['officials'][x]['last_name'] + '\n'
#	print 'Your representative\'s address is: \n' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['address_1']) + '\n'+ str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['address_2']) + '\n'+ str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['city']) + ', ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['state']) + ' ' +str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['postal_code'])
#	print 'Your representative\'s phone number is: ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['phone_1'])
#	print 'Your representative\'s URL is: ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['urls'][0])
#	print 'Your representative began on: ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['current_term_start_date']) +  '\nYour representative\'s term ends on: ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['term_end_date'])

def main():
	for account in users.keys():
		json_response = login(account, users[account])
		token = json_response['token']
		uid = str(json_response['user'])
#		print lat_long(lat, lon, uid, token)
		address = raw_input('What is your address?').replace(' ','+')
		official_response = get_official(address, uid, token)
		official_dict = json.loads(official_response)
#		print official_dict
		for x in range(1):
			official_info(official_dict, x)

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

def home(request):
	return HttpResponse('Welcome to StateGovTracker!')