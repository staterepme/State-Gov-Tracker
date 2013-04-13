from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max

from state_gov_tracker_app.models import Officials, OfficialOffices
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

        if len(args) != 1:
            raise CommandError('Expected path to csv file')
        
        twitter_csv = open(args[0], 'r')
        csv_reader = csv.DictReader(twitter_csv)
        for obs in csv_reader:
            try:
                o = Officials.objects.only('legid', 'twitter')\
                              .get(legid=obs['legid'])
                o.twitter=obs['twitter']
                o.save()
            except:
                print obs['legid']
                print obs['fullname']
                