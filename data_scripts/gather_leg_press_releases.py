#!/usr/bin/python

# Filename:	gather_leg_press_releases.py
# Author: 	Christopher M. Brown
# Project: 	State Gov Track
# Task:		Goes to press release pages, downloads all press releases

from bs4 import BeautifulSoup
from readability.readability import Document
import html2text, re, os, requests
import threading, urllib2, mechanize
from lxml.html import parse, make_links_absolute
from StringIO import StringIO
from load_database import *
import csv, feedparser
from urlparse import urlparse
from hashlib import md5

settings_dict = {'upper':{'Republican':{'xpath':'//p/a'},'Democratic':{'xpath':'//h2/a'}}}

def get_urls_with_prs_counter(first_url):
	"""Counter method for gathering more press releases"""
	link_array = []
	link_array.append(first_url)
	link_exist = True
	nexturl = first_url
	counter = 1
	while link_exist == True:
		counter += 1
		if counter > 25:
			break # Don't think there will be more than 25 pages of press releases
		try:
			urllib2.urlopen("%s/page/%s" %(first_url, counter))
			link_array.append("%s/page/%s" %(first_url, counter))
			link_exist = True
		except:
			link_exist = False
	return link_array

def dl_rss(url, party='Democratic'):
	"""Takes url to media/press release page and finds the rss feed there"""
	if party == 'Democratic':
		links = get_prs_from_url(url, '//tr/td/a')
		feed_id = None
		for url in links:
			match = re.search(r'RSS_reader_Member\.asp\?Feed=(\d+)', url)
			if (match):
				feed_id = match.group(1)
		rss_feed = feedparser.parse('http://www.pahouse.com/pr/xml/%s.xml' %(feed_id))
	if party == 'Republican':
		links = get_prs_from_url(url, '//div[@id="NewsRSS"]/a')
		rss_feed = feedparser.parse(links[0])
	for entry in rss_feed['entries']:
		print entry['title']
		print parse_dates(entry['published'])
		print entry['link']


def parse_dates(date_string, method=1):
	if method==1:
		"""Example string - Tue, 16 Nov 2010 19:27:00 -0500"""
		date_split = date_string.split(" ")
		return "%s-%02d-%02d %s" %(date_split[3], int(month2num(date_split[2])), int(date_split[1]), date_split[4])

def month2num(month):
    """Takes month and translates it to a number"""
    month = month.strip()
    month = month.lower()
    monthDict = {"jan":1,
                "feb":2,
                "mar":3,
                "apr":4,
                "may":5,
                "jun":6,
                "jul":7,
                "aug":8,
                "sep":9,
                "oct":10,
                "nov":11,
                "dec":12}
    return monthDict[month[:3]]

def parse_to_base(url):
	parsed_url = urlparse(url)
	return "%s://%s" %(parsed_url[0], parsed_url[1])

def get_urls_with_prs_repsen(first_url):
	"""Use this function to gather pages that have links for press releases for	Republican State Senators in PA"""
	link_list = []
	link_list.append(first_url)
	base_url = parse_to_base(first_url)
	# Not Pretty At All...3 potential ways senate republicans format urls for pages with press releases from a given year. I try all 3 different ways, if the response for urllib2 isn't a 404 error I add it to the list #
	link_patterns = [r"%s/press/%s/news-%s.htm", r"%s/press-%s/news-%s.htm", r"%s/%s-press/news-%s.htm"]
	for link_pattern in link_patterns:
		for year in range(2007,2012):
			try:
				urllib2.urlopen(link_pattern %(base_url, year, year))
				link_list.append(link_pattern %(base_url, year, year))
				print link_pattern %(base_url, year, year)
			except:
				pass
	newlist = list(set(link_list))
	return newlist

def get_html(url):
	"""Takes URL as an argument, returns html"""
	try:
		data = urllib2.urlopen(url, timeout=30).read()
	except:
		data = "Could Not Fetch Page %s" %(url)
	return data

def get_prs_from_url(url, path):
	"""uses lxml.html to parse for press release
	urls"""
	# Make Links Absolute #
	try:
		html = urllib2.urlopen(url).read()
		new_html = make_links_absolute(html, url)
		html_tree = parse(StringIO(new_html))
		link_list = []
		for element in html_tree.xpath(path):
			for links in element.iterlinks():
				link_list.append(links[2])
		return list(set(link_list))
	except:
		print "Could not get %s" %(url)
		return []
			
class official_prs(Base):
	"""Class of Official with information on location of Press Releases"""
	__table__ = Table('official_personal_pages', Base.metadata, autoload=True, autoload_with=engine)
	def get_pr_urls(self):
		"""Find pages that have links to press releases, download press release pages"""
		if self.chamber == 'upper' and self.party == 'Republican':
			self.urls =  get_urls_with_prs_repsen(self.press_release_url)
		elif self.chamber == 'upper' and self.party == 'Democratic':
			self.urls = get_urls_with_prs_counter(self.press_release_url)
		self.all_prs = []
		for url in self.urls:
			self.all_prs.extend(get_prs_from_url(url, settings_dict[self.chamber][self.party]['xpath']))
			if self.legid in ['PAL000016', 'PAL000266', 'PAL000227']:
				self.all_prs.extend(get_prs_from_url(url, '//h4/a'))
		self.all_prs = list(set(self.all_prs))
	def add_pr_urls_to_db(self):
		"""Take list of press release links, creates an md5 hash, checks to see if hash already in database, if not, then add link to database."""
		list_of_md5s = existing_url_md5s()
		for url in self.all_prs:
			if md5(url).hexdigest() in list_of_md5s:
				continue
			else:
				new_pr = press_release(pr_legid=self.legid,
					pr_md5=md5(url).hexdigest(),
					pr_url=url)
				session.add(new_pr)
				session.commit()

def existing_url_md5s():
	md5_list = []
	for pr in session.query(press_release).all():
		md5_list.append(pr.pr_md5)
	return md5_list

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

	print dl_rss('http://www.repsaccone.com/latestnews.aspx', party="Republican")