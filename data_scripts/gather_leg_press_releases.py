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
from django.core.validators import URLValidator
from urlparse import urlparse

def get_urls_with_prs_regex(first_url, regex):
	"""Takes first page that has press releases,
	then gathers all pages that have press releases"""
	link_array = []
	link_array.append(first_url)
	br = mechanize.Browser()
	link_exist = True
	nexturl = first_url
	while link_exist == True:
		br.open(nexturl)
		try:
			nexturl = br.find_link(text_regex=re.compile(regex)).url
			link_array.append(nexturl)
			link_exist = True
		except:
			link_exist = False
	return link_array

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
	"""Use this function to gather links for 
	Republican State Senators in PA"""
	link_list = []
	link_list.append(first_url)
	base_url = parse_to_base(first_url)
	print base_url
	for year in range(2007,2012):
		print year
		try:
			urllib2.urlopen("%s/press/%s/news-%s.htm" %(base_url, year, year))
			link_list.append("%s/press/%s/news-%s.htm" %(base_url, year, year))
		except:
			pass
	for year in range(2007,2012):
		print year
		try:
			urllib2.urlopen("%s/press-%s/news-%s.htm" %(base_url, year, year))
			link_list.append("%s/press-%s/news-%s.htm" %(base_url, year, year))
		except:
			pass
	for year in range(2007,2012):
		print year
		try:
			urllib2.urlopen("%s/%s-press/news-%s.htm" %(base_url, year, year))
			link_list.append("%s/%s-press/news-%s.htm" %(base_url, year, year))
		except:
			pass
	newlist = list(set(link_list))
	return newlist

def get_html(url):
	"""Takes URL as an argument, returns html"""
	try:
		data = urllib2.urlopen(url, timeout=30).read()
	except:
		print url
		data = "Could Not Fetch Page"
	return data

def get_prs_from_url(url, path, list_min=None, list_max=None):
	"""uses lxml.html to parse for press release
	urls"""
	# Make Links Absolute #
	print url
	html = urllib2.urlopen(url).read()
	new_html = make_links_absolute(html, url)
	html_tree = parse(StringIO(new_html))
	link_list = []
	for element in html_tree.xpath(path):
		# print element
		for links in element.iterlinks():
			if (re.search(r'htm$', links[2])):
				link_list.append(links[2])
	return list(set(link_list[list_min:list_max]))

def get_prs_from_html(html, first_tag, second_tag, method='bs4'):
	url_list = []
	# print html
	soup = BeautifulSoup(html)
	if method == 'bs4':
		# print soup.prettify()
		for link in soup.findAll(first_tag):
			# print link
			for url in link.findAll(second_tag):
				url_list.append(url.get("href"))
	return url_list

def get_press_releases(first_url, chamber, party):
	"""Gathers links to all press releases"""
	all_urls = get_urls_with_prs_regex(first_url)
	pr_urls = []
	for url in all_urls:
		html = get_html(url)
		pr_urls.extend(get_pr_urls(html))
	return pr_urls

if __name__ == '__main__':
	# html = get_html('http://www.senatorwashington.com/newsroom/press-releases')
	# print get_pr_urls(html, first_tag='li', second_tag='a')
	# print get_urls_with_prs_counter('http://www.senatordinniman.com/newsroom/press-releases/')
	# entry = session.query(official_webpages).filter(official_webpages.legid=='PAL000013').first()
	# print get_prs_from_url('http://senatorsmucker.com/press/2011/news-2011.htm', '//td[@valign="top"]/p/a')
	# print parse_to_base('http://www.senatormcilhinney.com/news.htm')
	urls =  get_urls_with_prs_repsen('http://senatorgeneyaw.com/news.htm')
	all_prs = []
	for url in urls:
		all_prs.extend(get_prs_from_url(url, '//p/a'))
	print list(set(all_prs))
	print len(list(set(all_prs)))