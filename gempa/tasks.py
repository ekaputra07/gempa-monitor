import csv
import urllib2

from django.conf import settings

from google.appengine.ext import db

from gempa.models import Gempa


def update_latest_eq(group, source):
    """Fetch latest EQ recorded, and update database"""
    try:
        result = urllib2.urlopen(source)
    except Exception as e:
        return e
    else:
        rows = csv.reader(result)
        eqs = []
        
        for row in rows:
            if row[0] != 'Src':
                eq = Gempa(
                    group= group,
                    source = row[0],
                    eqid = row[1],
                    time = row[2],
                    lat = row[3],
                    lon = row[4],
                    magnitude = row[5],
                    depth = row[6],
                    region = row[7]
                    )
                eqs.append(eq)

        if eqs:
            # Delete previously EQs in database
            is_clear = Gempa.bulk_delete_previous_records(group)

            # Add the new one
            if is_clear:
                Gempa.bulk_add_new_records(eqs)
    return
