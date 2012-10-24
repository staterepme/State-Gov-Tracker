# Create your views here.
from state_gov_tracker_app.models import *
import urllib,httplib2, mimetypes,os,sys,re,random,string
from state_gov_tracker_app.login_credentials import *
from django.shortcuts import render_to_response
from django.template import Context, loader
from state_gov_tracker_app.models import *
from django.http import HttpResponse
from subprocess import call
from sunlight import openstates


import datetime
try:
	import json
except ImportError:
	import simplejson as json
	
####SETTINGS####
http = httplib2.Http()
url_base = 'http://cicero.azavea.com/v3.1'

pref_type = {'Republican':'Conservative', 'Democratic':'Liberal'}
num_rank = {'upper':'50', 'lower':'200'}

def WhichRep(request):
	upper = search(request, 'UPPER')
	lower = search(request, 'LOWER')
	upper['legid'] = Officials.objects.filter(district=upper['district_id']).filter(chamber="upper")[0].legid
	lower['legid'] = Officials.objects.filter(district=lower['district_id']).filter(chamber="lower")[0].legid
	upper['image'] = Officials.objects.get(legid=upper['legid']).photourl
	lower['image'] = Officials.objects.get(legid=lower['legid']).photourl

	return render_to_response('intermediate.html',{"upper": upper, "lower": lower, "upper_legid":upper['legid'], "lower_legid":lower['legid']})

def pa_tweets(request):
	"""Request for pa-tweets page, contains the last 30 tweets by members of the General Assembly"""
	tweet_list_one = OfficialTweets.objects.order_by('-timestamp')[:20]
	tweet_list_two = OfficialTweets.objects.order_by('-timestamp')[20:40]
	return render_to_response('all_tweets.html', {"tweet_list_one":tweet_list_one, "tweet_list_two":tweet_list_two})

def blog_page(request):
	"""Returns blog page"""
	return render_to_response('blog.html')

def about_myrep(request):
	"""Returns about page"""
	return render_to_response('about.html')

position = {'upper':'Senate', 'lower':'House'}

def profile(request, profile_legid):
	official = {}
	official_object = Officials.objects.get(legid=profile_legid)
	official["office_nums"], official['email'] = get_offices(profile_legid)
	official['position'] = position[official_object.chamber]
	official['district'] = official_object.district
	official["fullname"] = official_object.fullname
	official["picture"] = official_object.photourl
	official["rank_type"] = pref_type[official_object.party]
	official['num_rank'] = num_rank[official_object.chamber]
	official['tweets'] = get_official_tweets(profile_legid)[:4]
	official['votes'] = get_recent_votes(profile_legid, num_to_get=10)[:4]
	official['fb_posts'] = get_recent_fb_posts(profile_legid)
	official['press_release'] = get_press_releases(profile_legid)[:4]
	official['rank'] = get_pref_rank(profile_legid, official_object.party, official_object.chamber)
	official['website'] = official_object.homepage
	official['ideology'] = Preferences.objects.get(legid=profile_legid).ideology
	graph_data = get_kdensity_data(chamber_to_get=official_object.chamber)
	return render_to_response('info.html', {'official': official, "legid":profile_legid, "graph_data":graph_data})

def get_kdensity_data(chamber_to_get):
	kdensity_graph = {}

	## Get Bounds of Graphs ##
	y_results_desc = PreferencesKdensity.objects.filter(chamber=chamber_to_get).order_by('-curve')[0]
	y_results_asc = PreferencesKdensity.objects.filter(chamber=chamber_to_get).order_by('curve')[0]
	x_results_desc = PreferencesKdensity.objects.filter(chamber=chamber_to_get).order_by('-preference')[0]
	x_results_asc = PreferencesKdensity.objects.filter(chamber=chamber_to_get).order_by('preference')[0]
	kdensity_graph['y_max'] = float(y_results_desc.curve)
	kdensity_graph['y_min'] = float(y_results_asc.curve)
	kdensity_graph['x_max'] = float(x_results_desc.preference)
	kdensity_graph['x_min'] = float(x_results_asc.preference)

	## Get Party Data ##
	# Democrats #
	dem_points = PreferencesKdensity.objects.filter(party="Democratic", chamber=chamber_to_get).order_by('-preference')
	dem_storage = []
	for result in dem_points:
		dem_storage.append({"x_axis":result.preference, "y_axis":result.curve})
	kdensity_graph['dem'] = json.dumps(dem_storage)
	# Republicans #
	rep_points = PreferencesKdensity.objects.filter(party="Republican", chamber=chamber_to_get).order_by('-preference')
	rep_storage = []
	for result in rep_points:
		rep_storage.append({"x_axis":result.preference, "y_axis":result.curve})
	kdensity_graph['rep'] = json.dumps(rep_storage)
	return kdensity_graph


def get_official_tweets(legid_to_get):
	tweets = OfficialTweets.objects.filter(legid=legid_to_get).order_by('-timestamp')[:4]
	new_tweets = []
	twitter_id = LegsSocialmedia.objects.get(legid=legid_to_get).twitter
	for t in tweets:
		url = "https://twitter.com/%s/status/%s" %(twitter_id, t.tweet_id)
		new_tweets.append({'tweet':t.tweet, 'timestamp':t.timestamp.split(' ')[0], 'url':url})
	return new_tweets

def get_pref_rank(legid_to_get, party_to_get, chamber_to_get):
	if party_to_get == "Republican":
		prefs = Preferences.objects.filter(party=party_to_get, chamber=chamber_to_get).order_by('-ideology')
	else:
		prefs = Preferences.objects.filter(party=party_to_get, chamber=chamber_to_get).order_by('-ideology')
	counter = 0
	for pref in prefs:
		counter += 1
		if pref.legid==legid_to_get:
			break
	return counter

def get_offices(legid_to_get):
	leg_info = openstates.legislator_detail(legid_to_get)
	try:
		email = leg_info['email']
	except:
		email = ''
	try:
		offices = leg_info['offices']
	except:
		offices = ''
	return offices, email

def get_press_releases(legid_to_get):
	press_releases = OfficialPressReleases.objects.filter(pr_legid=legid_to_get).order_by('-pr_date')[:10]
	relevant_prs = []
	if len(press_releases) == 0:
		return []
	for pr in press_releases:
		new_pr = {}
		if pr.pr_date == None:
			continue
		date_split = pr.pr_date.split('-')
		if int(date_split[0]) > 2012:
			continue
		if pr.pr_title == "":
			continue
		if pr.pr_title != None:
			new_pr['title'] = pr.pr_title
		else:
			new_pr['title'] = pr.pr_text
		new_pr['url'] = pr.pr_url
		new_pr['date'] = pr.pr_date
		relevant_prs.append(new_pr)
	return relevant_prs

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

def get_recent_fb_posts(legid_to_get, num_to_get=4):
	fb_posts = FbData.objects.filter(legid=legid_to_get).order_by('-timestamp')[:num_to_get]
	fb_list = []
	for fb_post in fb_posts:
		date = fb_post.timestamp.split(' ')[0]
		post_id = fb_post.post_id.split('_')
		link_to_post = 'https://www.facebook.com/%s/posts/%s' %(post_id[0], post_id[1])
		fb_list.append({'date':date, 'post':fb_post.post, 'url':link_to_post})
	return fb_list

vote = {'0':'Nay', '1':'Yea', '99':'Other'}
def get_recent_votes(legid_to_get, num_to_get=5):
	"""Takes legislator id, returns list of most recent votes where each vote is a dictionary that contains keys for:
		- title
		- bill (bill_id)
		- vote (Yea, Nay, Other)
		- date
		- motion (passage, other, etc.)
		"""
	leg_votes = PaLegisVotes.objects.filter(legid=legid_to_get).order_by('-date')[:20]
	vote_list = []
	for leg_vote in leg_votes:
		vote_type = Votes.objects.get(vote_id=leg_vote.vote_id).type
		if vote_type == 'passage':
			pass
		else:
			continue
		bill_title = PaBills.objects.get(bill_id=leg_vote.bill_id).title
		new_date = leg_vote.date.split(' ')[0]
		url = get_vote_url(leg_vote.bill_id)
		vote_list.append({'bill':leg_vote.bill_id, 'date':new_date, 'vote_yno':vote['%s' %(leg_vote.vote)], 'motion':vote_type, 'title':bill_title, 'url':url})
	return vote_list[:num_to_get]

def get_vote_url(bill_id_to_lookup):
	"""Calls to OpenStates API to grab bill URL"""
	bill = openstates.bill_detail(bill_id=bill_id_to_lookup, 
		state="pa", session="2011-2012")
	if bill['sources'][0]['url']:
		return bill['sources'][0]['url']
	else:
		return None

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
