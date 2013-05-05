from django.core.management.base import BaseCommand, CommandError

from state_gov_tracker_app.models import Officials
from django.conf import settings

import csv

class Command(BaseCommand):
    args = 'None'
    help = 'Bulk load facebook pages for legislators into database'

    def handle(self, *args, **options):
        """
        Loads CSV file that has legislator IDs, names, and urls for their
        Facebook pages. Replaces missing FB pages for legislators in the
        database.
        """
    fb_csv = open('raw_data/facebook/{0}.csv'.format(settings.STATE_FILTER), 'r')
    csv_reader = csv.DictReader(fb_csv)
    for obs in csv_reader:
        if obs['legid'] != '':
            try:
                o = Officials.objects.only('legid', 'facebook')\
                                     .get(legid=obs['legid'])
                o.facebook = obs['facebook']
                o.save()
            except:
                print "Warning: Failed to find {0} (id: {1}) in database"\
                    .format(obs['fullname'], obs['legid'])
