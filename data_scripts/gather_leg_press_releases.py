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
import csv
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
			# return self.fullname
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
	for off in session.query(official_prs).filter(official_prs.chamber=='upper').filter(official_prs.party=='Republican').all():
		# print off.fullname
		off.get_pr_urls()
		# print off.all_prs
		if len(off.all_prs) < 15:
			print off.fullname
			print off.press_release_url
		off.add_pr_urls_to_db()
	# print get_prs_from_url('http://www.senatorfarnese.com/media/press-releases/page/4', '//h2')
