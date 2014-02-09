from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.utils import simplejson

from google.appengine.ext import deferred
from google.appengine.api import memcache

from gempa.models import Gempa
from gempa.tasks import update_latest_eq

from apiclient.discovery import build



def homepage(request):
    """Homepage view."""
    context = {
        'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
    }
    return render_to_response('base.html', context,
                              context_instance=RequestContext(request))


def update_database(request):
    """Invoke database update queue"""
    deferred.defer(update_latest_eq, settings.EQ_LATEST_SOURCE[0],
                   settings.EQ_LATEST_SOURCE[1])
    deferred.defer(update_latest_eq, settings.EQ_LATEST60_SOURCE[0],
                   settings.EQ_LATEST60_SOURCE[1])
    return HttpResponse('Whoops! nothing to see in here.')


def get_earthquakes(request):
    """
    Get earthquakes records, and return as json.
    """
    order = request.GET.get('order')
    eqs = []

    def _mapper(quake_obj):
        return {
            'eqid': quake_obj.eqid,
            'lat': quake_obj.lat,
            'lon': quake_obj.lon,
            'time': quake_obj.time,
            'year': quake_obj.wib_datetime.strftime("%Y"),
            'month': quake_obj.wib_datetime.strftime("%B"),
            'day': quake_obj.wib_datetime.strftime("%d"),
            'magnitude': quake_obj.magnitude,
            'depth': quake_obj.depth,
            'region': quake_obj.region,
        }

    cached_eqs = memcache.get(settings.EQ_CACHE_KEY)
    if cached_eqs:
        eqs = cached_eqs
    else:
        eqs = Gempa.get_latest_quakes()
        eqs = map(_mapper, eqs)
        memcache.set(settings.EQ_CACHE_KEY, eqs)

    return HttpResponse(simplejson.dumps(eqs),
                        content_type='application/json; charset=utf-8')


def get_qvideos(request):
    """
    Get indonesia's related earthquake videos.
    """
    videos = []
    cached_videos = memcache.get(settings.VIDEOS_CACHE_KEY)
    
    if cached_videos:
        videos = cached_videos
    else:
        youtube = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION,
                        developerKey=settings.GOOGLE_API_KEY)

        search_response = youtube.search().list(
            q='indonesia earthquake',
            part="id,snippet",
            maxResults=25
        ).execute()

        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                video = {
                    'title': search_result["snippet"]["title"],
                    'id': search_result["id"]["videoId"],
                    'thumbnail': 'http://img.youtube.com/vi/' + search_result["id"]["videoId"] + '/default.jpg',
                    'url': 'http://www.youtube.com/watch?v=' + search_result["id"]["videoId"],
                }
                videos.append(video)
        memcache.set(settings.VIDEOS_CACHE_KEY, videos)

    return HttpResponse(simplejson.dumps(videos),
                        content_type='application/json; charset=utf-8')
