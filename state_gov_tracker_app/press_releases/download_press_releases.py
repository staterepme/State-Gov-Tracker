# Download Press Releases #

"""
Downloads press releases and enters raw HTML into the database
"""

import dateutil.parser as dup
from readability.readability import Document
import html2text
from hashlib import md5
from lxml.html import parse, make_links_absolute
import os, sys
import urllib2
from StringIO import StringIO
from multiprocessing import Pool
import feedparser
import re

# Need to add django application to path #
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
split_path = os.path.split(parentdir)
sys.path.insert(0, split_path[0])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from state_gov_tracker_app.models import *
from state_gov_tracker_app.login_credentials import *


###############################
### Get Press Release Links ###
###############################

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
    try:
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
    except:
        print "Could not get press release for %s" % (legid)
    return official.legid


#################################
## Download Press Release Text ##
#################################

def download_press_release_text(id):
    """
    Takes a press release object from django ORM query,
    downloads press release text, saves object.
    """
    from django.db import connection
    connection.close()

    pr_object = OfficialPressReleases.objects.get(pr_key=id)
    try:
        html = urllib2.urlopen(pr_object.pr_url).read()
        pr_object.pr_html = unicode(html, errors='ignore')
        pr_object.save()
    except Exception, e:
        print "Could not download URL:%s" % (pr_object.pr_url)
        print "ERROR: %s" % (e)


#############################################################
## Find Missing Dates (those which are not from RSS feeds) ##
#############################################################

def find_missing_dates():
    """
    Goes through press releases without dates, finds them
    and saves them to database
    """
    num_missing_dates = OfficialPressReleases.objects.filter(pr_date=None).count()
    print "%s missing dates to find" % (num_missing_dates)
    counter = 0
    for pr in OfficialPressReleases.objects.filter(pr_date=None):
        counter += 1
        if counter % 20 == 0:
            print "Finished parsing %s entries" % (counter)
        try:
            html_tree = parse(StringIO(pr.pr_html))
            if pr.pr_legid == 'PAL000020':
                for element in html_tree.xpath("///span[@class='date time published']"):
                    pr.pr_date = dup.parse(element.text)
                print pr.pr_date
            elif pr.pr_legid == 'PAL000039' and pr.pr_html != "":
                for element in html_tree.xpath("///time"):
                    pr.pr_date = dup.parse(element.text)
                print pr.pr_date
            else:
                try:
                    m = re.search(r'(\d{2})(\d{2})(\d{2})', pr.pr_url)
                    pr.pr_date = "20%s-%s-%s" % (m.group(3), m.group(1), m.group(2))
                except:
                    print "Could not find date KEY:%s" % (pr.pr_key)
                    continue
            print pr.pr_date
            pr.save()
        except:
            print "Could not parse dates for KEY:%s" % (pr.pr_key)

###########################
## Parse Text and Titles ##
###########################


def readabilify_text(html):
    """ Takes raw html, processes it and returns a title and parsed
    text """
    ## Get Text ##
    try:
        text = ""
        text = Document(html).summary()
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_anchors = True
        h.ignore_images = True
        h.ignore_emphasis = True
        final_text = h.handle(text)
    except:
        final_text = None
    ## Get Title ##
    try:
        title = Document(html).short_title()
    except:
        title = None
    return title, final_text


def parse_press_releases(pr_id):
    """Parses press releases and adds text and titles to the
    database. Written in this way in order to take advantage of
    multiprocessing module to do this quickly."""
    from django.db import connection
    connection.close()
    try:
        pr = OfficialPressReleases.objects.get(pr_key=pr_id)
        title, pr.pr_text = readabilify_text(pr.pr_html)
        if pr.pr_title == "":
            pr.pr_title = title
        pr.save()
    except Exception, e:
        print "Could not parse ID:%s" % (pr_id)
        print "ERROR: %s" % (e)

if __name__ == '__main__':
    pool = Pool(processes=10)

    # Download Press Release Links #
    # print "Downloading Press Release Links"
    # legids = [official.legid for official in Officials.objects.filter(active="True")]
    # result = pool.map(get_press_release_links, legids)

    # Download Press Releases #
    # print "Downloading Press Release Texts"
    # press_release_ids = [pr.pr_key for pr in OfficialPressReleases.objects.filter(pr_html="")]
    # print "%s press releases to download" % (len(press_release_ids))
    # result = pool.map(download_press_release_text, press_release_ids)

    # Find Missing Dates #
    # find_missing_dates()

    # Process HTML from Press Releases #
    print "Parsing Press Release HTML"
    pr_ids = [pr.pr_key for pr in OfficialPressReleases.objects.exclude(pr_date=None).filter(pr_text="")]
    print "%s press releases to parse for html" % (len(pr_ids))
    result = pool.map(parse_press_releases, pr_ids)
