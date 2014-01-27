from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'primdb_app.views.index', name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^mzml/$','primdb_app.views.mzml', name='mzml'),
    url(r'^pepxml/$','primdb_app.views.pepxml', name='pepxml'),
    url(r'^result/(?P<match>\d+)/(?P<tab>\d+)$', 'primdb_app.views.detail', name='detail'),
    url(r'^match/(?P<match_id>\d+)/tab/(?P<tab_id>\d+)$', 'primdb_app.views.matchdetail', name='matchdetail'),
    url(r'^result/tab/(?P<tab_id>\d+)/match/(?P<match_id>\d+)$', 'primdb_app.views.tabdetail', name='tabdetail'),
)
