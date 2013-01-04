# export data to JSON

from models import *
from datetime import timedelta, date
from django.db.models import Count
import json

today = date.today()
d = timedelta(days=10)
filter_date = today - d

def get_top_tweeters(date_length):
    d = timedelta(days=date_length)
    filter_date = date.today() - d
    tweets = OfficialTweets.objects.only("legid").filter(timestamp__gte=filter_date)
    tweet_count = {}
    for tweet in tweets:
        if tweet.legid in tweet_count:
            tweet_count[tweet.legid] += 1
        else:
            tweet_count[tweet.legid] = 1
    top_list = []
    for counter, leg in enumerate(sorted(tweet_count, key=tweet_count.get, reverse=True)):
        official = Officials.objects.only("lastname", "chamber").get(pk=leg)
        if official.chamber == "upper":
            title = "Sen."
        else:
            title = "Rep."
        top_list.append({'legid': leg,
            'count': tweet_count[leg],
            'name': title + ' ' + official.lastname})
        if counter > 8:
            break
    return top_list

def get_leg_info(legid):
    """Helper function to grab legislator data"""
    official = Officials.objects.only("lastname", "chamber").get(pk=legid)
    if official.chamber == "upper":
        title = "Sen."
    else:
        title = "Rep."

    try:
        twitter_id = LegsSocialmedia.objects.get(legid=legid).twitter
    except:
        twitter_id = None

    return {'legid': legid,
            'name': title + ' ' + official.lastname,
            'profile_link': '/profile/%s' % (legid),
            'twitter_id': twitter_id}

def tweet_getter(filter_date):
    """Takes a filter date and returns a list of recent tweets.
    Each tweet is a dictionary that contains the following keys and values:
        - name = title+name of legislator who tweeted
        - tweet_id = tweet id of tweet (primary key)
        - legid = legislator id of person who tweeted
        - text = text of tweet
        - datestamp = datestamp of tweet
        - link = link to full tweet
        - profile_link = link to legislators profile"""
    tweets = OfficialTweets.objects.filter(timestamp__gte=filter_date).order_by('-timestamp')
    tweet_list = []
    for t in tweets:
        leg_dict = get_leg_info(t.legid)
        t.form_url(leg_dict['twitter_id'])
        tweet_dict = {'text': t.tweet.encode('ascii', 'ignore'),
            'tweet_id': t.tweet_id,
            'datestamp': t.timestamp.strftime("%Y-%m-%d"),
            'tweet_link': t.url}
        tweet_dict.update(leg_dict)
        tweet_list.append(tweet_dict)
    return tweet_list


