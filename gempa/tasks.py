import csv
import urllib2
import re
import json
from datetime import datetime, timedelta

from django.conf import settings

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import urlfetch

from bs4 import BeautifulSoup


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

            # reset the cache too
            memcache.delete(settings.EQ_CACHE_KEY)
    return


def check_latest_sms_alert():
    """
    Check latest SMS desimination and notify users if its near them.
    """
    latest_event_id = None

    try:
        result = urllib2.urlopen(settings.SMS_ALERT_LIST_URL)

        soup = BeautifulSoup(result.read(), 'html.parser')
        latest_event = soup.find(href=re.compile('detail_sms\.php\?eventid='))

        if latest_event is not None:
            search = re.search(r"[0-9]+", latest_event['href'])
            latest_event_id = search.group(0)

    except Exception as e:
        print e

    if latest_event_id is not None:
        sms_body_url = settings.SMS_ALERT_DETAIL_URL % latest_event_id

        try:
            result = urllib2.urlopen(sms_body_url)
            body = re.search(">(Info Gempa.*::BMKG)<", result.read())
            print body.group(1)

            if body:
                try:
                    headers = {'Content-Type': 'application/json', 'Access-Token': settings.PB_ACCESS_TOKEN}
                    payload = {
                        "title": "Informasi Gempa",
                        "body": body.group(1),
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

        except Exception as e:
            print e
