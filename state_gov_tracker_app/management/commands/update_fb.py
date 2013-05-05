from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import httplib2, re, string, os, sys
import simplejson as json
from dateutil.parser import parse as date_parser

from state_gov_tracker_app.models import Officials, FbData

class Command(BaseCommand):
    args = 'None'
    help = 'Updates facebook posts for legislators'

    def facebook_token(self, FB_ID, FB_SECRET):
        """
        Gets token to access Facebook for social graph API.

        Returns a token.
        
        Arguments:
        - `FB_ID`: Facebook APP ID for graph API
        - `settings.FB_SECRET`: Facebook graph API secret
        """
        http = httplib2.Http()
        content = {}
        url = ('https://graph.facebook.com/oauth/access_token?client_id=' +
               FB_ID + '&client_secret=' + FB_SECRET +
               '&grant_type=client_credentials')
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        response, content = http.request(url, 'GET', headers=headers)
        a = content.rfind('=')
        return content[a + 1:len(content)]

    def parse_facebook_info(self, leg_fb_url):
        """Takes URL for legislator, parses it, returns
        Facebook ID"""
        pass
        if 'pages' in leg_fb_url:
            search_term = r"facebook\.com/pages/.*?/(\d+)"
            match = re.search(search_term, leg_fb_url)
            fb_id = match.group(1)
        elif 'profile' in leg_fb_url:
            search_term = 'id='
            a = leg_fb_url.rfind(search_term)
            fb_id = leg_fb_url[a + len(search_term):len(leg_fb_url)].rstrip()
        else:
            search_term = 'facebook.com/'
            a = leg_fb_url.rfind(search_term)
            fb_id = leg_fb_url[a + len(search_term):len(leg_fb_url)].rstrip()
        return fb_id

    def download_news_feed(self, FB_ID, FB_SECRET, test_official=None):
        """
        Downloads news feed for a given legislator's facebook ID.

        Adds new entries to database.
        Arguments:
        - `FB_ID`: ID for Facebook API
        - `FB_SECRET`: App secret for Facebook
        """
        # Get FB token for API #
        if test_official != None:
            officials = [test_official]
        else:
            officials = Officials.objects.filter(active='True')\
                                         .exclude(facebook = '')\
                                         .only('legid', 'facebook')
        total_o = len(officials)
        print "Downloading Facebook posts for {0} officials".format(total_o)
        for counter, o in enumerate(officials):
            sys.stdout.write('\r{0} percent complete ({1}/{2})'\
                         .format(counter/float(total_o), counter, total_o))
            sys.stdout.flush()
            # Get legislator's Facebook identifier #
            leg_fb = self.parse_facebook_info(o.facebook)
            token = self.facebook_token(FB_ID, FB_SECRET)
            posts = self.news_feed(token, leg_fb)
            self.add_posts(o.legid, posts)

    def news_feed(self, fb_token, leg_fb):
        """
        Takes a FB token and legislator's fb identifier and returns legislator's newsfeed
        """
        http = httplib2.Http()
        content = {}
        url = ('https://graph.facebook.com/' + leg_fb + '/posts?access_token='
               + fb_token + '&fields=message')
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        response, content = http.request(url, 'GET', headers=headers)
        content = json.loads(content)
        messages = []
        try:
            for entry in content['data']:
                if 'message' in entry:
                    messages.append(entry)
        except:
            print "Could not get data from %s" % (leg_fb)
        return messages

        
    def add_posts(self, legid, fb_post_list):
        """Takes a facebook post in the form of a dictionary, adds to database."""
        new_posts = []
        for fb_post in fb_post_list:
            if FbData.objects.filter(post_id=fb_post['id']).exists():
                pass
            else:
                new_post = FbData(legid=legid,
                              post=fb_post['message'].encode('utf-8'),
                              timestamp=date_parser(fb_post['created_time']),
                              post_id=fb_post['id'])
                new_posts.append(new_post)
        FbData.objects.bulk_create(new_posts)

    def handle(self, *args, **option):
        self.download_news_feed(settings.FB_APP_ID, settings.FB_APP_SECRET)