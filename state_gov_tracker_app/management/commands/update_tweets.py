from django.core.management.base import BaseCommand, CommandError

from twython import Twython
from datetime import datetime
from dateutil import parser as dp

from state_gov_tracker_app.models import Officials, OfficialTweets
from django.conf import settings

class Command(BaseCommand):
    args = 'None - uses twitter handles and tweets from DB'
    help = 'Downloads new tweets for legislators with twitter handles'

    def handle(self, *args, **options):
        twython = Twython(app_key=settings.TWITTER_APP_KEY,
                app_secret=settings.TWITTER_APP_SECRET,
                oauth_token=settings.TWITTER_OAUTH_TOKEN,
                oauth_token_secret=settings.TWITTER_OAUTH_SECRET)

        legs = Officials.objects.filter(active='True').exclude(twitter='').only('legid', 'fullname', 'twitter')
        print "Downloading new tweets for legislators."
        for counter, o in enumerate(legs):
            try:
                timeline = twython.getUserTimeline(screen_name=o.twitter)[:30]
            except:
                print "Could not download tweets for {0} (id: {1}, handle: {2})".format(o.fullname, o.legid, o.twitter)
                continue
            for t in timeline:
                if OfficialTweets.objects.filter(tweet_id=t['id_str']).exists():
                    continue
                else:
                    
                    new_tweet = OfficialTweets.objects.create(legid=o.legid,
                        tweet=t['text'],
                        tweet_id=t['id_str'],
                        timestamp=dp.parse(t['created_at']))
                    new_tweet.save()

        print "Downloading Twitter Oembed HTML for tweets"
        for tweet in OfficialTweets.objects.filter(oembed='').order_by('-timestamp'):
            oembed_dict = twython.getOembedTweet(id=tweet.tweet_id)
            tweet.oembed = oembed_dict['html']
            tweet.save()