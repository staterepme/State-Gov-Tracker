from django.core.management.base import BaseCommand, CommandError

from state_gov_tracker_app.models import Officials
from django.conf import settings
import csv

class Command(BaseCommand):
    """
    Loads configuration settings for downloading press releases.
    """
    args = 'None'
    help = 'Load configuration for downloading press releases'

    def handle(self, *args, **options):
        """
        Loads a CSV file that has settings for downloading press releases.
        The CSV should have columns (at the very least) for:
        - legid
        - rss: True/False depending on whether or not PR is available in RSS
        - xpath_pr: Xpath for press release links if not in RSS
        - xpath_date: Xpath for dates if not in RSS (none if in URL)
        - pr_url: URL for press release (either RSS or initial page with links to PRs)
        """
        pr_csv = open('raw_data/pr_configs/{0}.csv'.format(settings.STATE_FILTER), 'r')
        csv_reader = csv.DictReader(pr_csv)
        for obs in csv_reader:
            if obs['legid'] != '':
                try:
                    o = Officials.objects.get(legid=obs['legid'])
                    o.rss = obs['rss']
                    o.xpath_pr = obs['xpath_pr']
                    o.xpath_date = obs['xpath_date']
                    o.pr_url = obs['pr_url']
                    o.save()
                except:
                    self.stdout.write("Warning: Failed to find {0} (id: {1}) in database\n"\
                                      .format(obs['fullname'], obs['legid']))

