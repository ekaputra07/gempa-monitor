from django.conf.urls.defaults import patterns, include, url
from django.conf import settings


urlpatterns = patterns('gempa.views',
    url(r'^$', 'homepage', name='homepage'),
    url(r'^api/v1/earthquakes/$', 'get_earthquakes', name='get_earthquakes'),
    url(r'^cron/update_db/$', 'update_database', name='update_db'),
)
