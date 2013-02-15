# Download Press Releases #

"""
Downloads press releases and enters raw HTML into the database
"""

from datetime import datetime
import dateutil.parser as dup
from hashlib import md5
from lxml.html import parse, make_links_absolute
import os, sys
import urllib2
from StringIO import StringIO
from multiprocessing import Pool
import feedparser

# Need to add django application to path #
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
split_path = os.path.split(parentdir)
sys.path.insert(0, split_path[0]) 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from state_gov_tracker_app.models import *
from state_gov_tracker_app.login_credentials import *



# Get Press Release Links #
def get_press_release_links(legid):
    """Takes a configuration dictionary that contains a
    link to the press releases, a legid, type of press
    release gathering (webpage or rss), and xpath if necessary
    to the relevant links"""
    from django.db import connection
    connection.close()

    official = Officials.objects.get(pk=legid)
    print "Getting Legislator ID %s" % (official.legid)
    # If they have RSS feed link #
    if official.press_release_url_dl:
        rss_feed = feedparser.parse(official.press_release_url_dl)
        for entry in rss_feed['entries']:
            link_md5 = md5(entry['link']).hexdigest()
            if OfficialPressReleases.objects.filter(pr_md5=link_md5).exists():
                continue
            else:
                new_pr = OfficialPressReleases(pr_legid=legid,
                    pr_url=entry['link'],
                    pr_date=dup.parse(entry['published']),
                    pr_title=entry['title'],
                    pr_md5=link_md5)
                new_pr.save()

    # Download Links to Republican/Dem Senator Press Releases #
    elif official.chamber == 'upper':
        x_path_dict = {'Republican': '//p/a', 'Democratic': '//h2/a'}
        html = urllib2.urlopen(official.press_release_url).read()
        new_html = make_links_absolute(html, official.press_release_url)
        html_tree = parse(StringIO(new_html))
        for element in html_tree.xpath(x_path_dict[official.party]):
            for links in element.iterlinks():
                link_md5 = md5(links[2]).hexdigest()
                if OfficialPressReleases.objects.filter(pr_md5=link_md5).exists():
                    continue
                else:
                    new_pr = OfficialPressReleases(pr_legid=legid,
                        pr_url=links[2],
                        pr_md5=link_md5)
                    new_pr.save()
    return official.legid

if __name__ == '__main__':
    counter = 0
    legids = [official.legid for official in Officials.objects.filter(active="True")]
    pool = Pool(processes=10)
    result = pool.map(get_press_release_links, legids)
    result.get()