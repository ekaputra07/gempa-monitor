from google.appengine.ext import db

from django.conf import settings


class Gempa(db.Model):
    """
    Earth Quake data structure based on InaTEWS csv feed.
    # Src,Eqid,Datetime,Lat,Lon,Magnitude,Depth,Region
    # InaTEWS,20130710001843,Wednesday 10-07-2013 00:14:23 WIB,-3.34,100.33,5.2,22,146 km Tenggara KEP-MENTAWAI-SUMBAR
    """

    group = db.StringProperty()
    source = db.StringProperty()
    eqid = db.StringProperty()
    time = db.StringProperty()
    lat = db.StringProperty()
    lon = db.StringProperty()
    magnitude = db.StringProperty()
    depth = db.StringProperty()
    region = db.StringProperty()

    @classmethod
    def bulk_delete_previous_records(cls, group):
        """ Delete previous records"""
        eqs = Gempa.gql('WHERE group=:1', group)
        if eqs:
            try:
                db.delete(list(eqs))
                return True
            except:
                pass
        return

    @classmethod
    def bulk_add_new_records(cls, eqs):
        """Add new records"""
        if eqs:
            try:
                db.put(eqs)
                return True
            except:
                pass
        return

    @classmethod
    def get_latest_quakes(cls, single=False):
        """Get latest EQs either latest-60 or single result"""
        group = settings.EQ_LATEST60_SOURCE[0]
        if single:
            group = settings.EQ_LATEST_SOURCE[0]
        results = Gempa.gql('WHERE group=:1', group)
        return results