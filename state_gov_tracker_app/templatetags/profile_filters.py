from django import template

register = template.Library()

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
