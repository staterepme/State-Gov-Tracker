from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from state_gov_tracker_app.models import Officials

import csv

class Command(BaseCommand):
    args = '<list of data/models to export csvs for>'
    help = 'Takes a list that includes press-releases, twitter, or facebook and exports CSVs with names, legids, and existing configurations from the Officials table. Meant to streamline the process of bulk uploads and easily updating the data.'
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.twitter = {
            'path':'raw_data/twitter/{0}.csv'.format(settings.STATE_FILTER),
            'fields':['legid', 'fullname', 'twitter']
        }
        self.press_release = {
            'path':'raw_data/pr_configs/{0}.csv'.format(settings.STATE_FILTER),
            'fields':['legid', 'fullname', 'rss',
                      'xpath_pr', 'xpath_date', 'pr_url']
        }
        self.facebook = {
            'path':'raw_data/facebook/{0}.csv'.format(settings.STATE_FILTER),
            'fields':['legid', 'fullname', 'facebook']
        }

        self.data_types = [self.twitter, self.press_release, self.facebook]

    def printrow(dictionary, fields):
        s = str(dictionary[fields[0]])
        for field in fields[1:]:
            s = s + ',' + dictionary[field]
        return s
        
    def write_csv(self):
        for i in self.data_types:
            f = open(i['path'], 'w')
            data = Officials.objects.filter(active='True')
            headerrow = i['fields'][0]
            for field in i['fields'][1:]:
                headerrow = headerrow + ',' + field
            f.write(headerrow+'\n')
            for d in data:
                s = "{0}, {1}, {2}".format()
            f.write(s+'\n')

    def handle(self, *args, **options):
        self.write_csv()
            