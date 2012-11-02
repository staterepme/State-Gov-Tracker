#!/usr/bin/python

# Filename: LegTweets.py
# Author:   Christopher M. Brown
# Project:  State Gov Track
# Task:     Function for Collecting last N tweets, returns tuple of text + post-date

from twython_oembed import Twython
from login_credentials import *
from load_database import *

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
    Takes input_file that is a .csv file delimited
    with commas where the first column is the
    legislator ID, second column is their facebook
    ID, and the third column is their twitter handle.

    Calls to the twitter API for each member,
    downloading their last 20 tweets and returns them into a dictionary.
    """
    member_data = session.query(social_media_ids).all()
    dict_list = []
    for member in member_data:
        if member.twitter != "":
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
    for tweet in session.query(official_tweets).all():
        tweet_ids.append(tweet.tweet_id)
    return tweet_ids


def add_tweets_to_db(list_of_dictionary_tweets):
    existing_tweets = downloaded_tweets()
    for tweet in list_of_dictionary_tweets:
        if tweet['tweet_id'] in existing_tweets:
            continue
        else:
            new_tweet = official_tweets(legid=tweet['legid'],
                tweet=tweet['text'],
                tweet_id=tweet['tweet_id'],
                timestamp=tweet['timestamp'])
            session.add(new_tweet)
            session.commit()


def add_oembed_codes():
    for entry in session.query(official_tweets).filter(official_tweets.oembed == None).order_by(official_tweets.timestamp.desc()).all():
        # print entry.timestamp
        entry.oembed = getOembed(entry.tweet_id)
        session.add(entry)
        session.commit()


def getOembed(id_str):
    oembed_dict = t.getOembedTweet(id=id_str)
    return oembed_dict['html']

if __name__ == '__main__':
    # print getOembed('233584713019817984')
    new_tweets = download_first_tweets()
    add_tweets_to_db(new_tweets)
    add_oembed_codes()
