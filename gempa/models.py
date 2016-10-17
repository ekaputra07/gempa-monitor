import json
from google.appengine.ext import ndb
from google.appengine.api import urlfetch

from django.conf import settings


class Event(ndb.Model):
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    event_id = ndb.StringProperty()
    sms_body = ndb.TextProperty()
    email_body = ndb.TextProperty()
    latlon = ndb.GeoPtProperty()

    def broadcast_to_pushbullet(self):
        """
        broadcast event to PushBullet.
        """
        try:
            headers = {'Content-Type': 'application/json', 'Access-Token': settings.PB_ACCESS_TOKEN}
            payload = {
                "title": "Informasi Gempa",
                "body": self.sms_body,
                "type": "note",
                "channel_tag": settings.PB_GEMPA_CHANNEL_TAG
            }
            result = urlfetch.fetch(
                url=settings.PB_PUSH_URL,
                payload=json.dumps(payload),
                method=urlfetch.POST,
                headers=headers,
                validate_certificate=True)

            print result.status_code
            print result.content

        except urlfetch.Error as e:
            print e



class Gempa(ndb.Model):
    """
    Earth Quake data structure based on InaTEWS csv feed.
    # Src,Eqid,Datetime,Lat,Lon,Magnitude,Depth,Region
    # InaTEWS,20130710001843,Wednesday 10-07-2013 00:14:23 WIB,-3.34,100.33,5.2,22,146 km Tenggara KEP-MENTAWAI-SUMBAR
    """

    group = ndb.StringProperty()
    source = ndb.StringProperty()
    eqid = ndb.StringProperty()
    time = ndb.StringProperty()
    wib_datetime = ndb.DateTimeProperty()
    lat = ndb.StringProperty()
    lon = ndb.StringProperty()
    magnitude = ndb.StringProperty()
    depth = ndb.StringProperty()
    region = ndb.StringProperty()

    @classmethod
    def bulk_delete_previous_records(cls, group):
        """ Delete previous records"""
        eqs = Gempa.gql('WHERE group=:1', group)
        if eqs:
            try:
                ndb.delete_multi([e.key for e in eqs])
                return True
            except Exception as e:
                print e
                pass
        return

    @classmethod
    def bulk_add_new_records(cls, eqs):
        """Add new records"""
        if eqs:
            try:
                ndb.put_multi(eqs)
                return True
            except Exception as e:
                print e
                pass
        return

    @classmethod
    def get_latest_quakes(cls, single=False):
        """Get latest EQs either latest-60 or single result"""
        group = settings.EQ_LATEST60_SOURCE[0]
        if single:
            group = settings.EQ_LATEST_SOURCE[0]
        results = Gempa.gql('WHERE group=:1 ORDER BY wib_datetime DESC', group)
        return results
