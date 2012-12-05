from django import template

register = template.Library()
from django.contrib.contenttypes.models import ContentType

@register.filter
def shorten_date(value):
    return value.split(' ')[0]

@register.filter
def lowers(value):
    return value.lower()

@register.filter
def num_to_vote(vote):
    vote_string = "%s" %(vote)
    vote_dictionary = {'0': 'Nay', '1': 'Yea', '99': 'Other'}
    return vote_dictionary[vote_string]

@register.filter
def vote_total(object):
    return object.vote_total

@register.filter
def content_type(object):
    return "%s.%s" % (object._meta.app_label, object._meta.object_name)

@register.filter
def ct(object):
    return "%s%s" % (object._meta.app_label, object._meta.object_name)