#!/usr/bin/python

import httplib2
import re
import string
import simplejson as json
import pprint
from datetime import datetime
pp = pprint.PrettyPrinter(indent=4)

import os, sys

# Need to add django application to path #
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
split_path = os.path.split(parentdir)
sys.path.insert(0, split_path[0]) 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from state_gov_tracker_app.models import *
from state_gov_tracker_app.login_credentials import *


def facebook_token(app_id, app_secret):
    """
    Gathers Facebook token
    """
    http = httplib2.Http()
    content = {}
    url = ('https://graph.facebook.com/oauth/access_token?client_id=' +
        app_id + '&client_secret=' + app_secret +
        '&grant_type=client_credentials')
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    response, content = http.request(url, 'GET', headers=headers)
    a = content.rfind('=')
    return content[a + 1:len(content)]


def facebook_news_feed(app_id, app_secret, rep_FB_ID):
    http = httplib2.Http()
    content = {}
    fb_token = facebook_token(app_id, app_secret)
    url = ('https://graph.facebook.com/' + rep_FB_ID + '/posts?access_token='
        + fb_token + '&fields=message')
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    response, content = http.request(url, 'GET', headers=headers)
    content = json.loads(content)
    messages = []
    try:
        for entry in content['data']:
            if 'message' in entry:
                entry['created_time'].replace
                messages.append(entry)
    except:
        print "Could not get data from %s" % (rep_FB_ID)
    return messages


def get_facebook_ids():
    """ Query database and get all facebook IDs, parse for correct IDs"""
    fb_id_list = []
    for member in Officials.objects.filter(active='True').only('legid', 'facebook'):
        if member.facebook != "":
            fb_info = parse_facebook_info(member.facebook)
            fb_id_list.append((member.legid, fb_info))
    return fb_id_list


def parse_facebook_info(line):
    """Facebook id's right now include more than what we need, this
    function parses that line and returns exactly what we need."""
    if 'pages' in line:
        print line
        search_term = r"facebook\.com/pages/.*?/(\d+)"
        match = re.search(search_term, line)
        fb_id = match.group(1)
        print fb_id
    elif 'profile' in line:
        search_term = 'id='
        a = line.rfind(search_term)
        fb_id = line[a + len(search_term):len(line)].rstrip()
    else:
        search_term = 'facebook.com/'
        a = line.rfind(search_term)
        fb_id = line[a + len(search_term):len(line)].rstrip()
    return fb_id


def download_fb_posts(app_id, app_secret, list_of_fb_ids):
    """Downloads most recent facebook posts, returns a list of dictionary
    entries"""
    dict_list = []
    print "Downloading facebook posts for %s members right now" % (len(list_of_fb_ids))
    counter = 0
    for member_tuple in list_of_fb_ids:
        counter += 1
        print counter
        # if counter > 2:
        #     break
        try:
            posts = facebook_news_feed(app_id, app_secret, member_tuple[1])
        except:
            print "Could not get FB posts for %s" % (member_tuple[0])
        for post in posts:
            # print pp.pprint(post)
            post[u'legid'] = member_tuple[0]
            post[u'created_time'] = fix_fb_timestamp(post[u'created_time'])
            dict_list.append(post)
    return dict_list


def fix_fb_timestamp(timestamp):
    new_t = string.replace(timestamp, 'T', ' ')
    return new_t


def downloaded_posts():
    """Returns list of fb post IDs that have already been downloaded"""
    fb_post_ids = []
    for post in FbData.objects.all():
        fb_post_ids.append(post.post_id)
    return fb_post_ids


def add_posts_to_db(list_of_dictionary_posts):
    print "This %s many posts to go through" % (len(list_of_dictionary_posts))
    counter = 0
    for post in list_of_dictionary_posts:
        counter += 1
        print counter
        if FbData.objects.filter(post_id=post['id']).exists():
            continue
        else:
            new_post = FbData(legid=post['legid'],
                post=post['message'].encode('utf-8'),
                post_id=post['id'],
                timestamp=post['created_time'][:19])
            new_post.save()

if __name__ == '__main__':
    print "----------------------------"
    print datetime.now()
    pp = pprint.PrettyPrinter(indent=4)
    mem_list = get_facebook_ids()
    print mem_list
    new_posts = download_fb_posts(fb_app_id, fb_app_secret, mem_list)
    add_posts_to_db(new_posts)
