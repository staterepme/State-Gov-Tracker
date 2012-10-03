# Create your views here.
from state_gov_tracker_app.models import *
import urllib,httplib2, mimetypes,os,sys,re,random,string
from state_gov_tracker_app.login_credentials import *
from django.shortcuts import render_to_response
from django.template import Context, loader
from state_gov_tracker_app.models import *
from django.http import HttpResponse
from subprocess import call

import datetime
try:
	import json
except ImportError:
	import simplejson as json
	
####SETTINGS####
http = httplib2.Http()
url_base = 'http://cicero.azavea.com/v3.1'

def WhichRep(request):
	upper = search(request, 'UPPER')
	lower = search(request, 'LOWER')
	upper['legid'] = Officials.objects.filter(district=upper['district_id']).filter(chamber="upper")[0].legid
	lower['legid'] = Officials.objects.filter(district=lower['district_id']).filter(chamber="lower")[0].legid

	upper_posts = []
	lower_posts = []
	
	for x in range(5):
		if len(FbData.objects.all().order_by('timestamp').filter(legid=upper['legid'])) > 0:
			upper_posts.append(FbData.objects.all().filter(legid=upper['legid'])[x].post)
		else:
			upper_posts = 'No Facebook posts have been collected for this representative'
	upper['fbdata'] = upper_posts

	for x in range(5):
		if len(FbData.objects.all().order_by('timestamp').filter(legid=lower['legid'])) > 0:
			lower_posts.append(FbData.objects.all().filter(legid=lower['legid'])[x].post)
		else:
			lower_posts = 'No Facebook posts have been collected for this representative'
	
	lower['fbdata'] = lower_posts
	lower['tweets'] = OfficialTweets.objects.filter(legid=lower['legid']).order_by('-timestamp')[:5]
	upper['tweets'] =  OfficialTweets.objects.filter(legid=upper['legid']).order_by('-timestamp')[:5]

        upper['image'] = Officials.objects.get(legid=upper['legid']).photourl
        lower['image'] = Officials.objects.get(legid=lower['legid']).photourl

	return render_to_response('intermediate.html',{"upper": upper, "lower": lower, "upper_legid":upper['legid'], "lower_legid":lower['legid']})

def pa_tweets(request):
	"""Request for pa-tweets page, contains the last 30 tweets by members of the General Assembly"""
	tweet_list =  OfficialTweets.objects.order_by('-timestamp')[:30]
	return render_to_response('pa-tweets.html', {"tweet_list":tweet_list})

def profile(request, profile_legid):
	tweet_list = OfficialTweets.objects.filter(legid=profile_legid).order_by('-timestamp')[:5]
	official = {}
	official_object = Officials.objects.get(legid=profile_legid)
	official["fullname"] = official_object.fullname
	official["picture"] = official_object.photourl
	official['tweets'] = OfficialTweets.objects.filter(legid=profile_legid).order_by('-timestamp')[:5]
	return render_to_response('info.html', {'official': official, "tweet_list":tweet_list, "legid":profile_legid})

def MyRep(request):
	rep_id = search(request, 'LOWER')
	rep_name = name(rep_id)
	rep_picture = picture(rep_id)
	rep_bio = bio(rep_id)
	rep_news = news(rep_id)
	rep_twitter = twitter(rep_id)
	rep_facebook = facebook(rep_id)
	rep_votes = votes(rep_id)	
	return render_to_response('profile.html',{"rep_name": rep_name, "rep_picture": rep_picture, "rep_bio":rep_bio, 
	"rep_news":rep_news, "rep_twitter":rep_twitter, "rep_facebook":rep_facebook, "rep_votes":rep_votes})

vote = {'0':'Nay', '1':'Yea', '99':'Other'}

def get_recent_votes(legid_to_get, num_to_get=5):
	"""Takes legislator id, returns list of most recent votes where each vote is a dictionary that contains keys for:
		- title
		- bill (bill_id)
		- vote (Yea, Nay, Other)
		- date
		- motion (passage, other, etc.)
		"""
	leg_votes = PaLegisVotes.objects.filter(legid=legid_to_get).order_by('-date')[:100]
	vote_list = []
	for leg_vote in leg_votes:
		vote_type = Votes.objects.get(vote_id=leg_vote.vote_id).type
		if vote_type == 'passage':
			pass
		else:
			continue
		bill_title = PaBills.objects.get(bill_id=leg_vote.bill_id).title
		new_date = leg_vote.date.split(' ')[0]
		vote_list.append({'bill':leg_vote.bill_id, 'date':new_date, 'vote':vote['%s' %(leg_vote.vote)], 'motion':vote_type, 'title':bill_title})
	return vote_list[:num_to_get]

def search(request, upper_or_lower):
	if 'q' in request.GET:
		loc = request.GET['q'].replace(' ','+')
	else:
		loc = '1+Penn+Square+Philadelphia+PA+19107'
	json_response = login(cicero_user, cicero_password)
	token = json_response['token']
	uid = str(json_response['user'])
	official_response = get_officials(loc, uid, token, upper_or_lower)
	official_dict = json.loads(official_response)
	for x in range(1):
		return official_info(official_dict, x)

def search_form(request):
    return render_to_response('index.html')

def login(username, password):
	url = '/token/new.json'
	body = {'username': username, 'password': password}
	print url_base+url + '\n'
	headers = {'Content-type': 'application/x-www-form-urlencoded'}
	response, content = http.request(url_base+url, 'POST', headers=headers, body=urllib.urlencode(body))
	#print str(response) + '\n'
	content_dict = json.loads(content)
	return content_dict

def get_officials(loc, uid, token, upper_or_lower):
	url = '/official?user=' + uid + '&token=' + token + '&search_loc=' + loc + '&search_country=US&district_type=STATE_'+upper_or_lower
	headers = {'Content-type': 'application/x-www-form-urlencoded'}
	response, content = http.request(url_base+url, 'GET', headers=headers)
	return content

def official_info(official_dict, x):
	results = {}
	results['district_id'] = official_dict['response']['results']['candidates'][0]['officials'][x]['office']['district']['district_id']
	results['chamber'] = official_dict['response']['results']['candidates'][0]['officials'][x]['office']['chamber']['name']
	results['first_name'] = official_dict['response']['results']['candidates'][0]['officials'][x]['first_name']
	results['last_name'] = official_dict['response']['results']['candidates'][0]['officials'][x]['last_name']
	results['address'] = str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['address_1']) + ' ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['address_2']) + ' ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['city']) + ', ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['state']) + ' ' + str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['postal_code'])
	results['phone'] = str(official_dict['response']['results']['candidates'][0]['officials'][x]['addresses'][0]['phone_1'])
	return results
	
def name(rep_id):
	return rep_id
	
def picture(rep_id):
	picture = "picture"
	return picture
	
def bio(rep_id):
	bio = "bio!"
	return bio
	
def news(rep_id):
	news = "news!"
	return news
	
def twitter(rep_id):
	twitter = "twitter!"
	return twitter
	
def facebook(rep_id):
	facebook = "facebook!"
	return facebook
	
def votes(rep_id):
	votes = "votes!"
	return votes
	
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
