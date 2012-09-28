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

def get_urls_with_prs_repsen(first_url, method_num=1):
	link_array = []
	link_array.append(first_url)
	if method == 1:
		for year in range(2007,2012):
			print year
			try:
				urllib2.urlopen("http://www.senatorgordner.com/press/%s/press-%s.htm" %(year, year))
				link_array.append("http://www.senatorgordner.com/press/%s/press-%s.htm" %(year, year))
			except:
				pass
	if method == 2:
		for year in range(2007,2012):
			print year
			try:
				urllib2.urlopen("http://www.senatormcilhinney.com/press-%s/news-%s.htm" %(year, year))
				link_array.append("http://www.senatormcilhinney.com/press-%s/news-%s.htm" %(year, year))
			except:
				pass
	return link_array

def get_html(url):
	"""Takes URL as an argument, returns html"""
	try:
		data = urllib2.urlopen(url, timeout=30).read()
	except:
		print url
		data = "Could Not Fetch Page"
	return data

def get_prs_from_url(url, path):
	"""uses lxml.html to parse for press release
	urls"""
	# Make Links Absolute #
	html = urllib2.urlopen(url).read()
	new_html = make_links_absolute(html, url)
	html_tree = parse(StringIO(new_html))
	link_list = []
	for element in html_tree.xpath(path):
		print element
		for links in element.iterlinks():
			link_list.append(links[2])
	print link_list
	return link_list[None:None]

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

def get_press_releases(first_url):
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
	print get_prs_from_url('http://www.senatorblake.com/newsroom/news-releases', '//h2/a')