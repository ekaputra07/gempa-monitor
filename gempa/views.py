from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.utils import simplejson

from google.appengine.ext import deferred

from gempa.models import Gempa
from gempa.tasks import update_latest_eq



def homepage(request):
    """Homepage view."""
    return render_to_response('index.html', None,
                              context_instance=RequestContext(request))


def update_database(request):
    """Invoke database update queue"""
    deferred.defer(update_latest_eq, settings.EQ_LATEST_SOURCE[0],
                   settings.EQ_LATEST_SOURCE[1])
    deferred.defer(update_latest_eq, settings.EQ_LATEST60_SOURCE[0],
                   settings.EQ_LATEST60_SOURCE[1])
    return HttpResponse('Whoops! nothing to see in here.')


def get_earthquakes(request):
    """Get earthquakes records, and return as json"""
    source = request.GET.get('source', 'latest60')
    eqs = []

    def _mapper(quake_obj):
        return {
            'lat': quake_obj.lat,
            'lon': quake_obj.lon,
            'time': quake_obj.time,
            'magnitude': quake_obj.magnitude,
            'depth': quake_obj.depth,
            'region': quake_obj.region,
        }

    if source == 'latest':
        eqs = Gempa.get_latest_quakes(single=True)

    if source == 'latest60':
        eqs = Gempa.get_latest_quakes()

    eqs = map(_mapper, eqs)
    return HttpResponse(simplejson.dumps(eqs),
                        content_type='application/json; charset=utf-8')