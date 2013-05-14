from django.core.management.base import BaseCommand, CommandError

from django.conf import settings

import os, sys, subprocess

from state_gov_tracker_app.models import Preferences

class Command(BaseCommand):
    args = 'None'
    help = """Calculates legislator preferences based on votes in current
    session"""

    def delete_csv(self):
        """Deletes preference csv file if it exists"""
        print 'Deleting current preferences file'
        try:
            os.remove('current_preferences.csv')
        except OSError:
            print 'No Current Preferences to Delete'

    def calculate_preferences(self):
        """Runs R code to calculate legislator preferences"""
        subprocess.call("R CMD BATCH calculate_legislator_preferences.R")

    def handle(self, *args, **options):
        self.delete_csv()