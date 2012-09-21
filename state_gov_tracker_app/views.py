# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from state_gov_tracker_app.models import OfficialTweets, Officials

def home(request):
    o = "This is a db query"
    t = loader.get_template('home.html')
    c = Context({ 'official': o,
        })
    return HttpResponse(t.render(c))
