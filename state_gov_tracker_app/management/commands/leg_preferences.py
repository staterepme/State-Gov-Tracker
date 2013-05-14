from django.core.management.base import BaseCommand, CommandError

from django.conf import settings

import os, sys

from state_gov_tracker_app.models import Preferences

class Command(BaseCommand):
    args = 'None'
    help = """Calculates legislator preferences based on votes in current
    session"""

    def delete_csv(self):
        """Deletes preference csv file if it exists"""
        