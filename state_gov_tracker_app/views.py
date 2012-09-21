# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from state_gov_tracker_app.models import Officials, OfficialTweets
import datetime

def home(request):
    o = "This is a db query"
    t = loader.get_template('home.html')
    c = Context({ 'official': o,
        })
    return HttpResponse(t.render(c))

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)
