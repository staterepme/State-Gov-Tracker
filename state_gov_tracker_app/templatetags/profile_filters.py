from django import template
from sunlight import openstates

register = template.Library()


@register.filter
def shorten_date(value):
    return value.split(' ')[0]


@register.filter
def lowers(value):
    return value.lower()


@register.filter
def num_to_vote(vote):
    vote_string = "%s" % (vote)
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

@register.filter
def facebook_url(post_id_to_split):
    post_id = post_id_to_split.split('_')
    return 'https://www.facebook.com/%s/posts/%s' % (post_id[0], post_id[1])

@register.filter
def voteurl(id):
    """Calls to OpenStates API to grab bill URL"""
    bill = openstates.bill_detail(bill_id=id,
        state="pa", session="2011-2012")
    if bill['sources'][0]['url']:
        url = bill['sources'][0]['url']
    else:
        url = None
    return url
