# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models
from django.contrib import admin
from sunlight import openstates
from datetime import date, timedelta
from django.forms import TextInput, Textarea

try:
    import state_rep_tracker.secretballot as secretballot
except:
    import secretballot

try:
    import json
except ImportError:
    import simplejson as json
from django.contrib.contenttypes.models import ContentType

class PreferencesKdensity(models.Model):
    row_names = models.TextField(primary_key=True)
    preference = models.FloatField(blank=True)
    curve = models.FloatField(blank=True)
    party = models.TextField(blank=True)
    chamber = models.TextField(blank=True)

    class Meta:
        db_table = u'preferences_kdensity'


class Preferences(models.Model):
    row_names = models.TextField(blank=True)
    legid = models.TextField(blank=True, primary_key=True)
    party = models.TextField(blank=True)
    chamber = models.TextField(blank=True)
    ideology = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = u'preferences'


class FbData(models.Model):
    legid = models.TextField(blank=True)
    timestamp = models.TextField(blank=True)
    post = models.TextField(blank=True)
    post_id = models.TextField(blank=True)
    row_pk = models.IntegerField(primary_key=True)

    class Meta:
        db_table = u'fb_data'


class OfficialPersonalPages(models.Model):
    legid = models.CharField(max_length=100, primary_key=True, blank=True)
    fullname = models.TextField(blank=True)
    chamber = models.TextField(blank=True)
    district = models.IntegerField(null=True, blank=True)
    party = models.TextField(blank=True)
    ga_homepage = models.TextField(blank=True)
    personal_homepage = models.TextField(blank=True)
    press_release_url = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = u'official_personal_pages'


class OfficialPressReleases(models.Model):
    pr_legid = models.TextField(blank=True)
    pr_url = models.TextField(blank=True)
    pr_date = models.DateField(blank=True)
    pr_html = models.TextField(blank=True)
    pr_text = models.TextField(blank=True)
    pr_title = models.TextField(blank=True)
    pr_key = models.IntegerField(primary_key=True)
    pr_md5 = models.TextField(unique=True, blank=True)

    class Meta:
        db_table = u'official_press_releases'


class OfficialTweets(models.Model):
    legid = models.TextField(blank=True)
    tweet = models.TextField(blank=True)
    tweet_key = models.IntegerField(primary_key=True)
    tweet_id = models.TextField(blank=True)
    oembed = models.TextField(blank=True)
    timestamp = models.TextField(blank=True)

    def form_url(self, twitter_id):
        self.url = "https://twitter.com/%s/status/%s" % (twitter_id, self.tweet_id)

    def short_timestamp(self):
        self.shorttimestamp = self.timestamp.split(' ')[0]

    class Meta:
        db_table = u'official_tweets'


class Officials(models.Model):
    legid = models.TextField(primary_key=True, blank=True)
    fullname = models.TextField(blank=True)
    firstname = models.TextField(blank=True)
    middlename = models.TextField(blank=True)
    lastname = models.TextField(blank=True)
    suffixes = models.TextField(blank=True)
    nickname = models.TextField(blank=True)
    active = models.TextField(blank=True)
    state = models.TextField(blank=True)
    chamber = models.TextField(blank=True)
    district = models.IntegerField(null=True, blank=True)
    party = models.TextField(blank=True)
    transparencydataid = models.TextField(blank=True)
    photourl = models.TextField(blank=True)
    createdat = models.TextField(blank=True)
    updatedat = models.TextField(blank=True)
    homepage = models.TextField(blank=True)
    twitter = models.TextField(blank=True)
    facebook = models.TextField(blank=True)
    personal_homepage = models.TextField(blank=True)
    press_release_url = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    xpath = models.TextField(blank=True)
    press_release_url_dl = models.TextField(blank=True)

    def __unicode__(self):
        return self.fullname

    def help_vars(self):
        num_rank = {'upper': '50', 'lower': '200'}
        position = {'upper': 'Senate', 'lower': 'House'}
        pref_type = {'Republican': 'Conservative', 'Democratic': 'Liberal'}
        self.rank_type = pref_type[self.party]
        self.num_rank = num_rank[self.chamber]
        self.chamber_name = position[self.chamber]
        self.ctype = "state_gov_tracker_app.Officials"

    def get_pref_rank(self):
        if self.party == "Republican":
            prefs = Preferences.objects.filter(party=self.party, chamber=self.chamber).order_by('-ideology')
        else:
            prefs = Preferences.objects.filter(party=self.party, chamber=self.chamber).order_by('ideology')
        counter = 0
        for pref in prefs:
            counter += 1
            if pref.legid == self.legid:
                break
        self.rank = counter

    def get_offices(self):
        leg_info = openstates.legislator_detail(self.legid)
        try:
            self.email = leg_info['email']
        except:
            self.email = ''
        try:
            self.offices = leg_info['offices']
        except:
            self.offices = ''

    class Meta:
        db_table = u'officials'


class LegsSocialmedia(models.Model):
    legid = models.TextField(primary_key=True, blank=True)  # This field type is a guess.
    twitter = models.TextField(blank=True)  # This field type is a guess.
    facebook = models.TextField(blank=True)  # This field type is a guess.

    class Meta:
        db_table = u'legs_socialmedia'


class PaBills(models.Model):
    state = models.TextField(blank=True)
    session = models.TextField(blank=True)
    chamber = models.TextField(blank=True)
    created_at = models.TextField(blank=True)
    updated_at = models.TextField(blank=True)
    type = models.TextField(blank=True)
    subjects = models.TextField(blank=True)
    title = models.TextField(blank=True)
    bill_id = models.TextField(primary_key=True)
    bill_url = models.TextField()

    class Meta:
        db_table = u'pa_bills'


class PaLegisNews(models.Model):
    legid = models.TextField(blank=True)
    title = models.TextField(blank=True)
    link = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    date = models.TextField(blank=True)
    relevant = models.TextField(blank=True)
    yeas = models.TextField(blank=True)
    nays = models.TextField(blank=True)
    news_key = models.IntegerField(primary_key=True)

    class Meta:
        db_table = u'pa_legis_news'


class PaLegisSponsors(models.Model):
    legid = models.TextField(blank=True)
    bill_id = models.TextField(blank=True)
    type = models.TextField(blank=True)
    yeas = models.TextField(blank=True)
    nays = models.TextField(blank=True)
    sponsor_key = models.IntegerField(primary_key=True)

    class Meta:
        db_table = u'pa_legis_sponsors'


class LegisVotes(models.Model):
    vote_id = models.CharField(max_length=200, primary_key=True)
    chamber = models.TextField(blank=True)
    date = models.TextField(blank=True)
    motion = models.TextField(blank=True)
    num_no = models.IntegerField(null=True, blank=True)
    num_yes = models.IntegerField(null=True, blank=True)
    num_other = models.IntegerField(null=True, blank=True)
    type = models.TextField(blank=True)
    bill_id = models.TextField(blank=True)
    status = models.TextField(blank=True)
    session = models.TextField(blank=True)

    class Meta:
        db_table = u'legis_votes'


class PaLegisVotes(models.Model):
    legid = models.TextField(blank=True)
    bill_id = models.ForeignKey(PaBills)
    vote = models.IntegerField(null=True, blank=True)
    date = models.TextField(blank=True)
    vote_id = models.ForeignKey(LegisVotes)
    legis_vote_key = models.IntegerField(primary_key=True)

    class Meta:
        db_table = u'pa_legis_votes'


class OfficialOffices(models.Model):
    office_legid = models.TextField(blank=True)
    office_pk = models.IntegerField(primary_key=True)
    address = models.TextField(blank=True)
    phone = models.TextField(blank=True)
    name = models.TextField(blank=True)

    class Meta:
        db_table = u'official_offices'


secretballot.enable_voting_on(Officials)
secretballot.enable_voting_on(OfficialTweets)
secretballot.enable_voting_on(PaLegisVotes)
secretballot.enable_voting_on(FbData)
secretballot.enable_voting_on(OfficialPressReleases)

####################################
## Utility Functions for Views.py ##
####################################

## Filters Press Releases that have incorrect dates ##
## and incorrect titles                           


def filter_press_releases(press_releases):
    relevant_prs = []
    if len(press_releases) == 0:
        return []
    for pr in press_releases:
        if pr.pr_date == None:
            continue
        date_split = pr.pr_date.timetuple()
        if int(date_split[0]) > 2012:
            continue
        if pr.pr_title == "":
            continue
        if pr.pr_title != None:
            pr.pr_title = pr.pr_title
        else:
            pr.pr_title = "Sorry, we couldn't find the title"
        relevant_prs.append(pr)
    return relevant_prs

## Grabs Kernel Density Graph Data ##


def get_kdensity_data(chamber_to_get):
    kdensity_graph = {}
    kdensity_data = PreferencesKdensity.objects.defer("chamber", "row_names").filter(chamber=chamber_to_get).iterator()
    y_data = []
    x_data = []
    rep_data = []
    dem_data = []
    for data in kdensity_data:
        y_data.append(data.curve)
        x_data.append(data.preference)
        if data.party == 'Republican':
            rep_data.append({"x_axis": data.preference, "y_axis": data.curve})
        else:
            dem_data.append({"x_axis": data.preference, "y_axis": data.curve})
    y_data.sort()
    x_data.sort()

    kdensity_graph['y_max'] = y_data[-1]
    kdensity_graph['y_min'] = y_data[0]
    kdensity_graph['x_max'] = x_data[-1]
    kdensity_graph['x_min'] = x_data[0]

    kdensity_graph['dem'] = json.dumps(dem_data)

    kdensity_graph['rep'] = json.dumps(rep_data)
    return kdensity_graph


## Admin Stuff ##
class OfficialAdmin(admin.ModelAdmin):
    search_fields = ["fullname"]
    list_display = ('firstname', 'lastname', 'active', 'chamber', 'district', 'facebook', 'twitter')
    list_filter = ['active', 'chamber']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '240'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 540})},
        models.IntegerField: {'widget': Textarea(attrs={'rows': 1, 'cols': 240})},
    }
    fields = ("fullname", "chamber", "district", "party", "facebook", "twitter", "homepage")

admin.site.register(Officials, OfficialAdmin)
