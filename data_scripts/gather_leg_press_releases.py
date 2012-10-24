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
import csv, feedparser, threading, Queue
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
	try:	
		if party == 'Democratic':
			links = get_prs_from_url(url, '//tr/td/a')
			for url in links:
				match = re.search(r'RSS_reader_Member\.asp\?Feed=(\d+)', url)
				if (match):
					feed_id = match.group(1)
			rss_feed = feedparser.parse('http://www.pahouse.com/pr/xml/%s.xml' %(feed_id))
		if party == 'Republican':
			links = get_prs_from_url(url, '//div[@id="NewsRSS"]')
			try:
				rss_feed = feedparser.parse(links[0])
			except:
				rss_feed = feedparser.parse(links[1])
			# print rss_feed
		list_of_pr_dicts = []
		for entry in rss_feed['entries']:
			# print entry
			if entry['link'] == None:
				continue
			list_of_pr_dicts.append({"title":entry['title'], "datestamp":parse_dates(entry['published']), "url":entry['link']})
		return list_of_pr_dicts
	except:
		print "Could not get RSS Feed for %s.\nHere are the links:%s" %(url, links)

def parse_dates(date_string, method=1):
	if method==1:
		"""Example string - Tue, 16 Nov 2010 19:27:00 -0500"""
		date_split = date_string.split(" ")
		return "%s-%02d-%02d" %(date_split[3], int(month2num(date_split[2])), int(date_split[1]))

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
				# print link_pattern %(base_url, year, year)
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
		# print link_list
		return list(set(link_list))
	except:
		print "Could not get links from %s" %(url)
		return []
			
class official_prs(Base):
	"""Class of Official with information on location of Press Releases"""
	__table__ = Table('official_personal_pages', Base.metadata, autoload=True, autoload_with=engine)
	def get_pr_urls(self):
		"""Find pages that have links to press releases, download press release pages"""
		if self.chamber == 'upper':
			if self.party == 'Republican':
				self.urls =  get_urls_with_prs_repsen(self.press_release_url)
			elif self.party == 'Democratic':
				self.urls = get_urls_with_prs_counter(self.press_release_url)
			self.all_prs = []
			for url in self.urls:
				self.all_prs.extend(get_prs_from_url(url, settings_dict[self.chamber][self.party]['xpath']))
				if self.legid in ['PAL000016', 'PAL000266', 'PAL000227']:
					self.all_prs.extend(get_prs_from_url(url, '//h4/a'))
			self.all_prs = list(set(self.all_prs))
		if self.chamber == 'lower':
			self.all_prs = dl_rss(self.press_release_url, party=self.party)
	def add_pr_urls_to_db(self):
		"""Take list of press release links, creates an md5 hash, checks to see if hash already in database, if not, then add link to database."""
		list_of_md5s = existing_url_md5s()
		if self.all_prs != None:
			if self.chamber == 'upper':
				for url in self.all_prs:
					if md5(url).hexdigest() in list_of_md5s:
						continue
					else:
						new_pr = press_release(pr_legid=self.legid,
							pr_md5=md5(url).hexdigest(),
							pr_url=url)
						# try:
						print url
						session.add(new_pr)
						session.commit()
						# except:
						# 	session.rollback()
						# 	print "Could not commit %s" %(url)
						# 	pass
			if self.chamber == 'lower':
				for entry in self.all_prs:
					if md5(entry['url']).hexdigest() in list_of_md5s:
						continue
					else:
						new_pr = press_release(pr_legid=self.legid,
							pr_md5=md5(entry['url']).hexdigest(),
							pr_url=entry['url'],
							pr_date=entry['datestamp'],
							pr_title=entry['title'])
						try:
							session.add(new_pr)
							session.commit()
						except:
							session.rollback()
							print "Could not commit %s" %(self.fullname)
							pass
		else:
			print "Could not find any press releases for %s" %(self.fullname)
def existing_url_md5s():
	md5_list = []
	for pr in session.query(press_release).all():
		md5_list.append(pr.pr_md5)
	return md5_list

### Functions for Actually Downloading Scripts ###

def chunks(l, n):
	"""Splits a list (l) into chunks of size -n- and returns a list of chunks"""
	return [l[i:i+n] for i in range(0, len(l), n)]

def read_url(url, queue, index):
    try:
        data = urllib2.urlopen(url, timeout=30).read()
    except:
        print url
        print "Could Not Fetch Page"
        data = "Could Not Fetch Page"
    # print('Fetched %s from %s' % (len(data), url))
    queue.put((index,data))

def fetch_parallel(urls_to_load):
    result = Queue.Queue()
    threads = [threading.Thread(target=read_url, args = (url[1], result, url[0])) for url in urls_to_load]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return result

def dl_press_releases():
	pr_list = []
	
	## Get list of Press Releases and break it into chunks ##
	print "Getting List of Press Releases"
	for pr in session.query(press_release).filter(and_(press_release.pr_html==None)).order_by(func.random()).all():
		pr_list.append(pr)
	print "Need to download %s press releases" %(len(pr_list))
	pr_chunked = chunks(pr_list, 10)
	total_count = len(pr_list)
	## Loop through Chunks ##
	dl_count = 0
	for pr_chunk in pr_chunked:
		print "Getting press release # %s of %s total" %(dl_count, total_count)
		urls_to_dl = []
		pr_rows = []
		counter = 0
		for pr in pr_chunk:
			urls_to_dl.append((counter, pr.pr_url))
			counter += 1
			pr_rows.append(pr)
		# try:
		dl_prs = fetch_parallel(urls_to_dl)
		# except:
			# continue
		dl_count += 10
		q_list = sorted(list(dl_prs.queue))
		for element in q_list:
			if element[1] == "Could Not Fetch Page":
				pr_rows[element[0]].pr_html = "ERROR"
				pr_rows[element[0]].pr_html = None
			else:
				pr_rows[element[0]].pr_html = unicode(element[1], errors='ignore')
		for pr_dld in pr_rows:
			# try:
			session.add(pr_dld)
			session.commit()
			# print pr_dld.pr_key
			# except:
			# 	session.rollback()
			# 	pr_dld.pr_html="ERROR"
			# 	session.add(pr_dld)
			# 	print "Failed!"
			# 	session.commit()

if __name__ == '__main__':	
	### Download Press Releases for State Senate ###
	print "Getting Press Release URLs for State Senate"
	officials_to_get = session.query(official_prs).filter(official_prs.chamber=='upper').all()
	print "%s Total Press Releases to Gather" %(len(officials_to_get))
	counter = 0
	for off in session.query(official_prs).filter(official_prs.chamber=='upper').all():
		counter += 1
		# print off.fullname
		off.get_pr_urls()
		# print off.all_prs
		if len(off.all_prs) < 15:
			print off.fullname
			print off.press_release_url
		off.add_pr_urls_to_db()
		print "Gathered %s so far" %(counter)

	# ### Download Press Releases for State House ###
	print "Getting Press Release URLs for State House"
	print "%s Total Press Releases to Gather" %(len(session.query(official_prs).filter(official_prs.chamber=='lower').all()))
	counter = 0
	for off in session.query(official_prs).filter(official_prs.chamber=='lower').all():
		# print off.fullname
		counter += 1
		off.get_pr_urls()
		off.add_pr_urls_to_db()
		print "Gathered %s so far" %(counter)

	### Download HTML for Press Releases ###
	dl_press_releases()