from django.core.management.base import BaseCommand, CommandError

from state_gov_tracker_app.models import Officials
from django.conf import settings

import csv

class Command(BaseCommand):
    args = '<path to CSV file with legislator twitter handles>'
    help = 'Bulk load twitter handles for legislators into database'

    def handle(self, *args, **options):
        """
        Loads a CSV file that has legislator IDs, names, and twitter
        handles. Replaces missing twitter handles for legislators in
        the database with twitter handles.
        """

        twitter_csv = open('raw_data/twitter/{0}.csv'.format(settings.STATE_FILTER), 'r')
        csv_reader = csv.DictReader(twitter_csv)
        for obs in csv_reader:
            if obs['legid'] != '':
                try:
                    o = Officials.objects.only('legid', 'twitter')\
                                         .get(legid=obs['legid'])
                    o.twitter=obs['twitter']
                    o.save()
                except:
                    print "Warning: Failed to find {0} (id: {1}) in database"\
                        .format(obs['fullname'], obs['legid'])
