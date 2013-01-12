from tastypie.resources import ModelResource
from models import Preferences, OfficialPressReleases
import datetime


class PreferencesResource(ModelResource):
    class Meta:
        queryset = Preferences.objects.all()
        resource_name = 'preferences'
        filtering = {
            "chamber": ('exact', 'startswith'),
            "party": ('exact', 'startswith'),
        }
        include_resource_uri = False
        excludes = ['row_names']

    def determine_format(self, request):
        return "application/json"


class PR_Resource(ModelResource):
    class Meta:
        queryset = OfficialPressReleases.objects.exclude(pr_date__gt=datetime.date(2012, 12, 31), pr_date__lt=datetime.date(2002, 1, 1), pr_text=None).defer('pr_html', 'pr_key', 'pr_md5').all()
        resource_name = 'press_releases'
        include_resource_uri = False
        excludes = ['pr_html', 'pr_key', 'pr_md5']
        filtering = {
            "pr_legid": ('exact',),
            "pr_date": ('gt', 'lt'),
        }

    def determine_format(self, request):
        return "application/json"
