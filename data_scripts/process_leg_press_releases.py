#!/usr/bin/python

# Filename:	gather_leg_press_releases.py
# Author: 	Christopher M. Brown
# Project: 	State Gov Track
# Task:		Adds dates to press releases, finds text

from bs4 import BeautifulSoup
from readability.readability import Document
import html2text, re, os, requests
import threading, urllib2, mechanize
from lxml.html import parse, make_links_absolute
from StringIO import StringIO
from load_database import *
import csv, feedparser, Queue
from urlparse import urlparse
from hashlib import md5

settings_dict = {'upper':{'Republican':{'xpath':'//p/a'},'Democratic':{'xpath':'//h2/a'}}}

def readabilify_text(html):
    text = ""
    text = Document(html).summary()
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_anchors = True
    h.ignore_images = True
    h.ignore_emphasis = True
    return h.handle(text)

def process_press_releases():
	for pr in session.query(press_release).filter(_and(press_release.pr_html != None, press_release.pr_html != "ERROR")).all():
		pr.pr_text = readabilify_text(pr_html)
		session.add(pr)
		session.commit()

if __name__ == '__main__':	
	### Download Press Releases for State Senate ###
	# for off in session.query(official_prs).filter(official_prs.chamber=='upper').all():
	# 	# print off.fullname
	# 	off.get_pr_urls()
	# 	# print off.all_prs
	# 	if len(off.all_prs) < 15:
	# 		print off.fullname
	# 		print off.press_release_url
	# 	off.add_pr_urls_to_db()

	### Download Press Releases for State House ###
	# for off in session.query(official_prs).filter(official_prs.chamber=='lower').filter(official_prs.party=="Republican").all():
	# 	print off.fullname
	# 	off.get_pr_urls()
	# 	# print off.all_prs
	# 	# if len(off.all_prs) < 15:
	# 	# 	print off.fullname
	# 	# 	print off.press_release_url
	# 	off.add_pr_urls_to_db()

	### Download HTML for Press Releases ###
	dl_press_releases()