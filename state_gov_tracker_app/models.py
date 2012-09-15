from django.db import models

# Create your models here.
class State(models.Model):
    state_code = models.CharField(max_length=2)

    def __unicode__(self):
        return self.state_code

class Party(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class District(models.Model):
    district_number = models.IntegerField()

    def __unicode__(self):
        return self.district_number

class Official(models.Model):
    leg_id = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    suffixes = models.CharField(max_length=200)
    nickname = models.CharField(max_length=200)
    active = models.BooleanField()
    state = models.ForeignKey(State)
    chamber = models.CharField(max_length=200)
    party = models.ForeignKey(Party)
    transparencydata_id = models.CharField(max_length=200)
    photo_url = models.CharField(max_length=200)

    def __unicode__(self):
        return self.leg_id
        return self.full_name
        return self.first_name
        return self.middle_name
        return self.last_name
        return self.suffixes
        return self.nickname
        return self.active
        return self.state
        return self.chamber
        return self.party
        return self.transparencydata_id
        return self.photo_url



