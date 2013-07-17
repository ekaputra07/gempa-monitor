import csv
import urllib2
from datetime import datetime, timedelta

from django.conf import settings

from google.appengine.ext import db

from gempa.models import Gempa


def str_to_datetime(datetime_str):
    """
    Convert formatted datetime back to datetime object
    input format: `Monday 15-07-2013 22:00:15 WIB` 
    """
    try:
        # In case input format changed
        dayname, date, time, area = datetime_str.split()
        datetime_fmt = '%s %s' % (date, time)
        return datetime.strptime(datetime_fmt, '%d-%m-%Y %H:%M:%S')
    except:
        return ''


def wib_to_utc(wib_datetime):
    """
    Convert WIB to UTC.
    WIB stands for "Waktu Indonesia Barat" (Western Indonesian Time).
    WIB offset is +7, so UTC time = local_time - time_offset.
    """
    time_offset = timedelta(hours=7)
    utc_time = wib_datetime - time_offset
    return utc_time


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
                    wib_datetime = str_to_datetime(row[2]),
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
