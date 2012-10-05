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

def process_press_releases():
	for pr in session.query(press_release).filter(_and(press_release.pr_html != None, press_release.pr_html != "ERROR")).all():
		pr.pr_text = readabilify_text(pr_html)
		session.add(pr)
		session.commit()

def find_date_one(url):
	"""Finds date in URLs with 6 digit format of MMDDYY"""
	m = re.search(r'(\d{2})(\d{2})(\d{2})', url)
	return "20%s-%s-%s" %(m.group(3), m.group(1), m.group(2))

def find_date_two(html):
	"""Finds dates in html"""
	soup = BeautifulSoup(html, ["lxml", "html"])
	dateSearchString = r".*?(jan|january|feb|march|mar|april|apr|may|june|jun|july|jul|aug|sep|oct|nov|dec).*?(\d{1,2}).*(\d{4}).*"
	regexDate = re.compile(dateSearchString, re.I)
	dateSearchString_num = r".*?(\d{1,2}).*?(\d{1,2}).*?(\d{4}).*?"
	regexDateNum = re.compile(dateSearchString_num, re.I)
	if soup.findAll('time', limit=2):
		for link in soup.findAll('time', limit=2):
			m = regexDate.search(link.get_text())
			month = month2num(m.group(1))
			return "%s-%02d-%02d" %(int(m.group(3)), int(month), int(m.group(2)))
	else:
		return Error

def get_html(url):
	"""Takes URL as an argument, returns html"""
	try:
		data = urllib2.urlopen(url, timeout=30).read()
	except:
		data = "Could Not Fetch Page %s" %(url)
	return data

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

def find_date_all():
	pr_list = session.query(press_release).filter(and_(press_release.pr_html != "", press_release.pr_html != "ERROR", press_release.pr_date == None)).all()
	print "Processing %s press releases" %(len(pr_list))
	counter = 0
	for pr in session.query(press_release).filter(and_(press_release.pr_html != "", press_release.pr_html != "ERROR", press_release.pr_date == None)).order_by(func.random()).all():
		counter += 1
		print counter
		if (re.search('senatorkitchen', pr.pr_url)):
			print pr.pr_url
			# continue
		try:
			pr.pr_date = find_date_two(pr.pr_html)
			session.add(pr)
			print "Commited 2 %s" %(pr.pr_key)
			continue
		except:
			pass
		try:
			pr.pr_date = find_date_three(pr.pr_html)
			session.add(pr)
			print "Commited 3 %s" %(pr.pr_key)
			continue
		except:
			pass
		try:
			pr.pr_date = find_date_four(pr.pr_html)
			session.add(pr)
			print "Commited 4 %s" %(pr.pr_key)
			continue
		except:
			pass
		try:
			pr.pr_date = find_date_five(pr.pr_html)
			session.add(pr)
			print "Commited 5 %s" %(pr.pr_key)
			continue
		except:
			pass
		try:
			pr.pr_date = find_date_six(pr.pr_html)
			session.add(pr)
			print "Commited 5 %s" %(pr.pr_key)
			continue
		except:
			pass
		try:
			pr.pr_date = find_date_seven(pr.pr_html)
			session.add(pr)
			print "Commited 5 %s" %(pr.pr_key)
			continue
		except:
			pass
		try:
			pr.pr_date = find_date_one(pr.pr_url)
			session.add(pr)
			print "Commited 1 %s" %(pr.pr_key)
			continue
		except:
			pass
	session.commit()

def find_date_three(html):
	html_tree = parse(StringIO(html))
	for element in html_tree.xpath('///span[@class="month"]'):
		month = "%02d" %int((month2num(element.text)))
	for element in html_tree.xpath('///span[@class="day"]'):
		day = "%02d" %(int(element.text))
	for element in html_tree.xpath('///span[@class="year"]'):
		year = element.text
	return "%s-%s-%s" %(year, month, day)

def find_date_four(html):
	html_tree = parse(StringIO(html))
	if html_tree.xpath('///strong'):
		for element in html_tree.xpath('///strong/text()'):
			dateSearchString = r".*?(jan|january|feb|march|mar|april|apr|may|june|jun|july|jul|aug|sep|oct|nov|dec).*?(\d{1,2}).*(\d{4}).*"
			regexDate = re.compile(dateSearchString, re.I)
			if element.text != " " and element.text != None:
				# print element.text
				m = regexDate.search(element.text)
				month = month2num(m.group(1))
				return "%s-%02d-%02d" %(int(m.group(3)), int(month), int(m.group(2)))
	else:
		return Error

def find_date_six(html):
	html_tree = parse(StringIO(html))
	if html_tree.xpath("///span[@class='date time published']"):
		for element in html_tree.xpath("///span[@class='date time published']"):
			dateSearchString = r".*?(jan|january|feb|march|mar|april|apr|may|june|jun|july|jul|aug|sep|oct|nov|dec).*?(\d{1,2}).*(\d{4}).*"
			regexDate = re.compile(dateSearchString, re.I)
			m = regexDate.search(element.text)
			month = month2num(m.group(1))
			return "%s-%02d-%02d" %(int(m.group(3)), int(month), int(m.group(2)))
	else:
		return Error

def find_date_seven(html):
	html_tree = parse(StringIO(html))
	if html_tree.xpath("///strong"):
		for element in html_tree.xpath("///strong"):
			dateSearchString = r".*?(jan|january|feb|march|mar|april|apr|may|june|jun|july|jul|aug|sep|oct|nov|dec).*?(\d{1,2})"
			regexDate = re.compile(dateSearchString, re.I)
			m = regexDate.search(element.text)
			month = month2num(m.group(1))
			return "2012-%02d-%02d" %(int(month), int(m.group(2)))
	else:
		return Error

def find_date_eight(html):
	html_tree = parse(StringIO(html))
	if html_tree.xpath("///em/text()"):
		for element in html_tree.xpath("///em/text()"):			
			dateSearchString = r".*?(jan|january|feb|march|mar|april|apr|may|june|jun|july|jul|aug|sep|oct|nov|dec).*?(\d{1,2}).*?(\d{4}).*?"
			regexDate = re.compile(dateSearchString, re.I)
			m = regexDate.search(element.strip())
			month = month2num(m.group(1))
			return "%s-%02d-%02d" %(int(m.group(3)), int(month), int(m.group(2)))
	else:
		return Error

def find_date_five(html):
	html_tree = parse(StringIO(html))
	if html_tree.xpath('///div[@id="main"]/p[@class="meta"]'):
		for element in html_tree.xpath('///div[@id="main"]/p[@class="meta"]'):
			dateSearchString = r".*?(jan|january|feb|march|mar|april|apr|may|june|jun|july|jul|aug|sep|oct|nov|dec).*?(\d{1,2}).*(\d{4}).*"
			regexDate = re.compile(dateSearchString, re.I)
			m = regexDate.search(element.text)
			month = month2num(m.group(1))
			return "%s-%02d-%02d" %(int(m.group(3)), int(month), int(m.group(2)))
	else:
		return Error

def test(url):
	html_data = get_html(url)
	try:
		print "1"
		print find_date_one(url)
	except:
		pass
	try:
		print "2"
		print find_date_two(html_data)
	except:
		pass
	try:
		print "3"
		print find_date_three(html_data)
	except:
		pass
	try:
		print "4"
		print find_date_four(html_data)
	except:
		pass
	try:
		print "5"
		print find_date_five(html_data)
	except:
		pass
	try:
		print "6"
		print find_date_six(html_data)
	except:
		pass
	try:
		print "7"
		print find_date_seven(html_data)
	except:
		pass
	try:
		print "8"
		print find_date_eight(html_data)
	except:
		pass

def fix_dates():
	print len(session.query(press_release).all())
	counter = 0
	for pr in session.query(press_release).all():
		if counter == 100:
			break
		if pr.pr_html == '':
			counter += 1
			print pr.pr_key
			pr.pr_html == None
			session.add(pr)
		# if re.search('www.senatordinniman.com', pr.pr_url):
		# 	pr.pr_date = None
		# 	session.add(pr)
	session.commit()

def add_texts_and_titles():
	pr_list = session.query(press_release).filter(and_(press_release.pr_html != "", press_release.pr_html != "ERROR", press_release.pr_date != None, press_release.pr_title==None)).order_by(press_release.pr_date.desc()).all()
	print "Processing %s press releases" %(len(pr_list))
	counter = 0
	for pr in pr_list:
		counter += 1
		print pr.pr_key
		if counter % 25 == 0:
			print counter
		try:
			parsed_html = readabilify_text(pr.pr_html)
			pr.pr_title = parsed_html[0]
			pr.pr_text = parsed_html[1]
			session.add(pr)
		except:
			pass
		if counter == 5000:
			break
	session.commit()

if __name__ == '__main__':
	# test('http://www.senatorcosta.com/corbetts-shale-policy-falls-short')
	find_date_all()
	# fix_dates()
	# url = 'http://www.senatoranthonyhwilliams.com/grays-ferry-farmers-market-to-open-may-31'
	# html_data = get_html(url)
	# print readabilify_text(html_data)[0]
	add_texts_and_titles()
