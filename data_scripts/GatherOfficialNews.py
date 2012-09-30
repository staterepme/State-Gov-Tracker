#!/usr/local/bin/python

# Filename:	GatherOfficialNews.py
# Author: 	Christopher M. Brown
# Project: 	State Gov Track
# Task:		Function that takes search terms of last_name + first_name + state and returns last X links to news articles
from load_database import *
import feedparser
import csv, urllib2, html2text
import pprint

def strip_html(html):
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_anchors = True
    h.ignore_images = True
    h.ignore_emphasis = True
    clean_html = h.handle(html)
    chtml = clean_html.replace('\t', '    ')
    chtml = chtml.replace('\n', ' ')
    chtml = chtml.replace('\r', ' ')
    return chtml

def get_search_terms():
    """Loads names from database to use as search terms"""
    official_search_terms = []
    for member in session.query(official_info).all():
        official_search_terms.append((member.legid, member.firstname+' '+member.lastname))
    return official_search_terms
    
def gather_news_feeds(list_of_member_tuples, num_results):
    news_results = []
    for member_tuple in list_of_member_tuples:
        search_terms = member_tuple[1]
        mem_id = member_tuple[0]
        search_terms = search_terms.replace(' ','+')
        d = feedparser.parse("http://news.google.com/news?hl=en&gl=us&q=%s&geo=Pennsylvania&bav=on.2,or.r_gc.r_pw.r_cp.r_qf.&biw=1280&bih=635&um=1&ie=UTF-8&output=rss" %(search_terms))
        news_list = []
        for entry in d['entries']:
            news_list.append((entry['title'], entry['link'], strip_html(entry['summary']), entry['published']))
            if len(news_list) == num_results:
                break
        news_results.append({mem_id:news_list})
    return news_results

if __name__ == '__main__':
    member_search_list = get_search_terms()
    print gather_news_feeds(member_search_list[:10], 2)
