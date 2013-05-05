from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.forms.models import model_to_dict

from state_gov_tracker_app.models import Officials

import os

class Command(BaseCommand):
    args = '<list of data/models to export csvs for>'
    help = 'Takes a list that includes press-releases, twitter, or facebook and exports CSVs with names, legids, and existing configurations from the Officials table. Meant to streamline the process of bulk uploads and easily updating the data.'
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.twitter = {
            'path':'raw_data/twitter/{0}.csv'.format(settings.STATE_FILTER),
            'fields':['legid', 'fullname', 'party', 'chamber', 'twitter']
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

    def printrow(self, dictionary, fields):
        s = str(dictionary[fields[0]])
        for field in fields[1:]:
            s = s + ',' + dictionary[field]
        return s

    def check_path(self, path_to_file):
        """Check if path exists, if no, create path"""
        try:
            os.makedirs(os.path.split(path_to_file)[0])
        except OSError, e:
            print e
            pass
    
    def write_csv(self):
        for i in self.data_types:
            self.check_path(i['path'])
            f = open(i['path'], 'w')
            data = Officials.objects.filter(active='True')
            headerrow = i['fields'][0]
            for field in i['fields'][1:]:
                headerrow = headerrow + ',' + field
            f.write(headerrow+'\n')
            for d in data:
                d_dict = model_to_dict(d)
                s = self.printrow(d_dict, i['fields'])
                f.write('{0}\n'.format(s))
            f.close()

    def handle(self, *args, **options):
        self.write_csv()
            