#!/usr/bin/python

# Filename: LegTweets.py
# Author:   Christopher M. Brown
# Project:  State Gov Track
# Task:     Function for Collecting last N tweets, returns tuple of text + post-date

from twython import Twython
from datetime import datetime
from dateutil import tz

import os, sys

# Need to add django application to path #
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
split_path = os.path.split(parentdir)
sys.path.insert(0, split_path[0]) 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from state_gov_tracker_app.models import *
from state_gov_tracker_app.login_credentials import *


t = Twython(app_key=twitter_app_key,
            app_secret=twitter_app_secret,
            oauth_token=twitter_oauth_token,
            oauth_token_secret=twitter_oauth_token_secret)


def get_official_timeline(handle, num_tweets):
    user_timeline = t.getUserTimeline(screen_name=handle)[:num_tweets]
    tweet_list = []
    for entry in user_timeline:
        tweet_list.append((entry['text'], convert_twitter_timestamp(entry['created_at']), entry['id_str']))
    return tweet_list


def download_first_tweets(num_tweets=100):
    """
    Calls to the twitter API for each member,
    downloading their last 100 tweets and returns them into a dictionary.
    """
    member_data = Officials.objects.filter(active='True').only('legid', 'twitter')
    dict_list = []
    for counter, member in enumerate(member_data):
        print counter
        if member.twitter != None and member.twitter != '':
            try:
                user_tl = get_official_timeline(member.twitter, num_tweets)
            except:
                print "Could Not Get Twitter for member %s\n%s" % (member.twitter, member.legid)
                continue
            for tweet in user_tl:
                dict_list.append({'legid': member.legid,
                    'text': tweet[0],
                    'timestamp': tweet[1],
                    'tweet_id': tweet[2]})
    return dict_list


def month2num(month):
    """Takes month and translates it to a number"""
    month = month.strip()
    month = month.lower()
    monthDict = {"jan": 1,
                "feb": 2,
                "mar": 3,
                "apr": 4,
                "may": 5,
                "jun": 6,
                "jul": 7,
                "aug": 8,
                "sep": 9,
                "oct": 10,
                "nov": 11,
                "dec": 12}
    return monthDict[month[:3]]


def convert_twitter_timestamp(timestamp):
    """Takes original twitter timestamp and
    outputs correct formatted timestamp."""
    weekday, month, day, time, extra, year = timestamp.split()
    newtime = "%s-%02d-%02d %s" % (year, int(month2num(month)), int(day.encode('utf-8', 'ignore')), time)
    return newtime


def downloaded_tweets():
    """Returns list of tweet IDs that have
    already been downloaded"""
    tweet_ids = []
    for tweet in OfficialTweets.objects.only('tweet_id').all():
        tweet_ids.append(tweet.tweet_id)
    return tweet_ids


def add_tweets_to_db(list_of_dictionary_tweets):
    existing_tweets = downloaded_tweets()
    for tweet in list_of_dictionary_tweets:
        if tweet['tweet_id'] in existing_tweets:
            continue
        else:
            new_tweet = OfficialTweets(legid=tweet['legid'],
                tweet=tweet['text'].encode('utf-8'),
                tweet_id=tweet['tweet_id'],
                timestamp=tweet['timestamp'])
            session.add(new_tweet)
            session.commit()


def add_oembed_codes():
    for entry in OfficialTweets.objects.filter(oembed=None).order_by('-timestamp'):
        entry.oembed = getOembed(entry.tweet_id)
        entry.save()


def getOembed(id_str):
    oembed_dict = t.getOembedTweet(id=id_str)
    html_to_encode = oembed_dict['html']
    return html_to_encode.encode('utf-8')

if __name__ == '__main__':
    print "----------------------------"
    print datetime.now()
    # print getOembed('233584713019817984')
    new_tweets = download_first_tweets()
    add_tweets_to_db(new_tweets)
    add_oembed_codes()

    ## Convert Tweet Timezones ##
    # from_zone = tz.gettz('UTC')
    # to_zone = tz.gettz('America/New_York')
    # counter = 0
    # for entry in session.query(official_tweets):
    #     counter += 1
    #     if (counter % 20) == 0:
    #         session.commit()
    #     print counter
    #     old_tz = entry.timestamp
    #     old_tz = old_tz.replace(tzinfo=from_zone)
    #     eastern = old_tz.astimezone(to_zone)
    #     print eastern
    #     print old_tz
    #     entry.timestamp = eastern.replace(tzinfo=None)
    # session.commit()
