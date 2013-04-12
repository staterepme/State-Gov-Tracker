from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max

from state_gov_tracker_app.models import Officials, OfficialOffices
from django.conf import settings
from sunlight import openstates

class Command(BaseCommand):
    args = '<two-digit state abbr>'
    help = 'Load legislators for a given state'

    def add_specific_details(self, obj):
        legid = obj.legid
        data = openstates.legislator_detail(legid)
        obj.homepage = data.get('url','')

        # The primary key isn't actually set to auto-increment
        # so we're going to recreated starting with the largest
        # key. This makes it safe run this script over and over
        # but is mildly offensive
        pk = OfficialOffices.objects.all().aggregate(Max('office_pk'))['office_pk__max'] or 0
        pk += 1

        OfficialOffices.objects.filter(office_legid=legid).delete()

        ## There isn't actually a FK relationship
        ## to office, so just save it here
        for office in data['offices']:
            o = OfficialOffices()
            o.office_pk = pk
            o.office_legid=legid
            o.address=office['address']
            o.phone=office['phone']
            o.name=office['name']
            o.save()

            pk += 1


    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Expected two digit state prefix')

        legs = openstates.legislators(state=args[0],active=True)
        self.stdout.write('Updating %s records\n' % len(legs))

        for leg in legs:
            o = Officials()
            o.legid = leg['leg_id']
            o.firstname = leg['first_name']
            o.lastname = leg['last_name']
            o.middlename = ""
            o.fullname = " ".join([o.firstname, o.middlename, o.lastname])
            o.active = "True"
            o.state = args[0]
            o.chamber = leg['chamber']
            o.district = leg['district']
            o.party = leg['party']
            o.transparencydataid = leg['transparencydata_id']
            o.photourl = leg['photo_url']
            o.createdat = leg['created_at']
            o.updatedat = leg['updated_at']
            o.twitter = ""
            o.facebook = ""
            o.personal_homepage = ""
            o.press_release_url = ""
            o.notes = ""
            o.xpath = ""
            o.press_release_url_dl = ""
            self.add_specific_details(o)
            o.save()
