# Create your views here.
from models import *
from django.shortcuts import render_to_response
from cicero_search import *
from django.template import RequestContext, loader
########################################
## Search by address, display results ##
########################################


def WhichRep(request):
    upper = search(request, 'UPPER')
    lower = search(request, 'LOWER')
    upper_leg = Officials.objects.filter(district=upper['district_id']).filter(chamber="upper")[0]
    lower_leg = Officials.objects.filter(district=lower['district_id']).filter(chamber="lower")[0]
    upper_office = OfficialOffices.objects.filter(office_legid=upper_leg.legid).order_by('name').values()[0]
    lower_office = OfficialOffices.objects.filter(office_legid=lower_leg.legid).order_by('name').values()[0]
    return render_to_response('intermediate.html',
        {"upper": upper_leg,
        "lower": lower_leg,
        "upperoffice": upper_office,
        "loweroffice": lower_office})

####################
## PA Tweets Page ##
####################


def pa_tweets(request):
    """Request for pa-tweets page, contains the last 30 tweets by members of the General Assembly"""
    tweet_list_one = OfficialTweets.objects.order_by('-timestamp').exclude(oembed=None)[:20]
    tweet_list_two = OfficialTweets.objects.order_by('-timestamp').exclude(oembed=None)[20:40]
    return render_to_response('all_tweets.html',
        {"tweet_list_one": tweet_list_one,
        "tweet_list_two": tweet_list_two})

####################
##  Profile Page  ##
####################


def profile(request, profile_legid):
    official_object = Officials.objects.only("fullname", "photourl", "party", "chamber").get(legid=profile_legid)
    official_object.get_offices()
    official_object.help_vars()

    ## Get Tweets ##
    twitter_id = LegsSocialmedia.objects.get(legid=profile_legid).twitter
    tweets = OfficialTweets.objects.defer("oembed").filter(legid=profile_legid).order_by('-timestamp').select_related()[:10]
    for tweet in tweets:
        tweet.form_url(twitter_id)

    ## Get Votes ##
    votes = PaLegisVotes.objects.filter(legid=profile_legid).order_by('-date').select_related()[:10]

    ## Get FB Posts ##
    fb_posts = FbData.objects.filter(legid=profile_legid).order_by('-timestamp').select_related()[:10]

    ## Get Press Releases ##
    press_releases = OfficialPressReleases.objects.only("pr_title", "pr_date", "pr_url").filter(pr_legid=profile_legid).order_by('-pr_date').select_related()[:10]
    filtered_press_releases = filter_press_releases(press_releases)

    ## Ideology and Graph Data ##
    official_object.get_pref_rank()
    ideology = Preferences.objects.get(legid=profile_legid).ideology
    graph_data = get_kdensity_data(chamber_to_get=official_object.chamber)
    return render_to_response('info.html',
        {'official': official_object,
        "legid": profile_legid,
        "graph_data": graph_data,
        "tweets": tweets,
        "votes": votes,
        "fb_posts": fb_posts,
        "press_releases": filtered_press_releases,
        "ideology": ideology},
        context_instance=RequestContext(request))

###############
## Home Page ##
###############


def search_form(request):
    user = request.user
    return render_to_response('index.html', {'user': user})

#######################
## About StateRep.Me ##
#######################


def about_myrep(request):
    """Returns about page"""
    return render_to_response('about.html')

########################
## Browse Legislators ##
########################


def legislator_list(request):
    """Returns page that has list of browse-able state legislators"""
    upper_leg = Officials.objects.filter(chamber="upper").order_by('district')
    lower_leg = Officials.objects.filter(chamber="lower").order_by('district')
    return render_to_response('all_legislators.html',
        {'senators': upper_leg,
        'representatives': lower_leg})
